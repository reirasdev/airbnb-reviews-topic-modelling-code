"""Etapa 3 — Modelagem de tópicos: BERTopic (embeddings multilíngues) e LDA (linha de base).

BERTopic é ajustado numa amostra (UMAP+HDBSCAN não escalam para milhões de sentenças) e
os demais textos são atribuídos por transform (approximate_predict). Outliers (-1) são
reatribuídos ao centroide mais próximo se cos >= OUTLIER_MIN_SIM; o resto fica -1 e vira "geral".
Coerência C_v (gensim) é calculada com o mesmo tokenizador e as mesmas amostras para os dois.
"""
from __future__ import annotations

import hashlib
import logging
import re

import numpy as np
import pandas as pd

from .embeddings import embed_all
from .utils import Store, stage

log = logging.getLogger("pipeline")
_TOK = re.compile(r"(?u)\b[^\W\d_]{3,}\b")


def stopwords(cfg) -> set[str]:
    import stopwordsiso
    sw: set[str] = set()
    for lang in cfg.LANG_SET:
        sw |= set(stopwordsiso.stopwords(lang))
    return sw


def tokenize(text: str, sw: set[str]) -> list[str]:
    return [w for w in _TOK.findall(text.lower()) if w not in sw]


def _cv_per_topic(topics: list[list[str]], texts: list[list[str]], dictionary) -> list[float]:
    """C_v por tópico (palavras fora do dicionário são descartadas; tópicos com <2 palavras -> NaN)."""
    from gensim.models import CoherenceModel
    clean = [[w for w in t if w in dictionary.token2id] for t in topics]
    ok = [i for i, t in enumerate(clean) if len(t) >= 2]
    res = [np.nan] * len(topics)
    if ok:
        cm = CoherenceModel(topics=[clean[i] for i in ok], texts=texts, dictionary=dictionary,
                            coherence="c_v", processes=1)
        for i, v in zip(ok, cm.get_coherence_per_topic()):
            res[i] = float(v)
    return res


def run_bertopic(cfg, store: Store, E: np.ndarray, T: pd.DataFrame, sw: set[str], coh_texts, coh_dict) -> None:
    from bertopic import BERTopic
    from hdbscan import HDBSCAN
    from sklearn.feature_extraction.text import CountVectorizer
    from umap import UMAP

    rng = np.random.default_rng(cfg.SEED)
    pool = T.index[T["n_tok"] >= cfg.TOPIC_MIN_TOKENS].to_numpy()
    fit_ids = np.sort(rng.choice(pool, size=min(cfg.BERTOPIC_FIT_SAMPLE, len(pool)), replace=False))
    docs = T.loc[fit_ids, "text"].tolist()
    emb = E[fit_ids].astype("float32")
    log.info("BERTopic: ajustando em %d sentenças (>= %d tokens)", len(docs), cfg.TOPIC_MIN_TOKENS)

    umap_model = UMAP(n_neighbors=cfg.UMAP_N_NEIGHBORS, n_components=cfg.UMAP_N_COMPONENTS, min_dist=0.0,
                      metric="cosine", random_state=cfg.SEED)
    hdb = HDBSCAN(min_cluster_size=cfg.HDBSCAN_MIN_CLUSTER_SIZE, min_samples=cfg.HDBSCAN_MIN_SAMPLES,
                  metric="euclidean", cluster_selection_method="eom", prediction_data=True)
    vec = CountVectorizer(stop_words=sorted(sw), min_df=cfg.VECTORIZER_MIN_DF, token_pattern=_TOK.pattern)
    # language="multilingual" é ESSENCIAL: com o padrão "english" o BERTopic remove todo caractere fora de
    # [A-Za-z0-9 ] (_preprocess_text), o que mutilava palavras acentuadas (v1: "anfitri", "farmcia").
    tm = BERTopic(language="multilingual", embedding_model=None, umap_model=umap_model, hdbscan_model=hdb, vectorizer_model=vec,
                  top_n_words=cfg.TOPIC_TOP_WORDS, calculate_probabilities=False, verbose=False)
    fit_topics, _ = tm.fit_transform(docs, embeddings=emb)
    fit_topics = np.asarray(fit_topics)
    ids = sorted(t for t in set(fit_topics) if t != -1)
    log.info("BERTopic descobriu %d tópicos; outliers na amostra de ajuste: %.1f%%", len(ids), 100 * (fit_topics == -1).mean())

    # centroides no espaço original dos embeddings (vetor de cada tópico, usado na Etapa 4)
    cent = np.vstack([emb[fit_topics == t].mean(0) for t in ids])
    cent /= np.linalg.norm(cent, axis=1, keepdims=True)
    np.save(store.root / "topic_centroids.npy", cent)

    # atribuição de todos os textos únicos, em chunks com checkpoint. A assinatura do ajuste invalida chunks
    # de um ajuste diferente (ids de tópico não seriam comparáveis).
    cdir = store.subdir("topic_chunks")
    sig = hashlib.md5(fit_topics.tobytes()).hexdigest()
    sig_file = cdir / "fit_signature.txt"
    if not sig_file.exists() or sig_file.read_text() != sig:
        for old in cdir.glob("c*.npy"):
            old.unlink()
        sig_file.write_text(sig)
    raw = np.full(len(T), -1, dtype="int32")
    pos = T.index.to_numpy()
    step = cfg.TOPIC_TRANSFORM_CHUNK
    for c, i in enumerate(range(0, len(T), step)):
        f = cdir / f"c{c:05d}.npy"
        if f.exists():
            raw[i:i + step] = np.load(f)
            continue
        sel = pos[i:i + step]
        tp, _ = tm.transform(T.loc[sel, "text"].tolist(), embeddings=E[sel].astype("float32"))
        raw[i:i + step] = tp
        np.save(f, np.asarray(tp, dtype="int32"))
        log.info("  transform chunk %d/%d", c + 1, int(np.ceil(len(T) / step)))

    # reatribuição de outliers por similaridade ao centroide
    final = raw.copy()
    id_arr = np.array(ids)
    for i in range(0, len(T), 200_000):
        m = np.where(raw[i:i + 200_000] == -1)[0] + i
        if len(m):
            sim = E[m].astype("float32") @ cent.T
            best, bs = sim.argmax(1), sim.max(1)
            final[m] = np.where(bs >= cfg.OUTLIER_MIN_SIM, id_arr[best], -1)
    store.save("text_topics", pd.DataFrame({"text_id": T["text_id"].to_numpy(), "topic_raw": raw, "topic": final}))

    # tabela de tópicos para auditoria / mapeamento manual
    words = {t: [w for w, _ in tm.get_topic(t)] for t in ids}
    cv = _cv_per_topic([words[t] for t in ids], coh_texts, coh_dict)
    rows = []
    for k, t in enumerate(ids):
        m = np.where(fit_topics == t)[0]
        top = m[np.argsort(-(emb[m] @ cent[k]))[:3]]
        rows.append({"topic": t, "n_fit": len(m), "n_textos_final": int((final == t).sum()),
                     "top_words": ", ".join(words[t]), "exemplos": " || ".join(docs[j] for j in top), "c_v": cv[k]})
    tab = pd.DataFrame(rows).sort_values("n_fit", ascending=False)
    store.save("topics_bertopic", tab)
    store.metric("etapa3_bertopic", n_topicos=len(ids), outliers_fit_pct=round(100 * float((fit_topics == -1).mean()), 1),
                 outliers_final_pct_textos=round(100 * float((final == -1).mean()), 1),
                 c_v_medio=round(float(np.nanmean(cv)), 4))


def run_lda(cfg, store: Store, T: pd.DataFrame, sw: set[str], coh_texts) -> None:
    from gensim.corpora import Dictionary
    from gensim.models import LdaModel

    rng = np.random.default_rng(cfg.SEED)
    toks = T["text"].map(lambda s: tokenize(s, sw))
    pool = np.where(toks.map(len) >= cfg.LDA_MIN_TOKENS)[0]
    idx = np.sort(rng.choice(pool, size=min(cfg.LDA_SAMPLE, len(pool)), replace=False))
    sample = [toks.iloc[i] for i in idx]
    dic = Dictionary(sample)
    dic.filter_extremes(no_below=20, no_above=0.5)
    corpus = [dic.doc2bow(d) for d in sample]
    log.info("LDA: %d sentenças, vocabulário %d | grade de K=%s (critério: C_v máximo)", len(sample), len(dic), cfg.LDA_K_GRID)
    full_dic = Dictionary(coh_texts)
    best, grid = None, []
    for k in cfg.LDA_K_GRID:
        lda = LdaModel(corpus, id2word=dic, num_topics=k, random_state=cfg.SEED, passes=cfg.LDA_PASSES,
                       iterations=50, chunksize=10_000)
        tw = [[dic[w] for w, _ in lda.get_topic_terms(t, cfg.TOPIC_TOP_WORDS)] for t in range(k)]
        cv = _cv_per_topic(tw, coh_texts, full_dic)
        grid.append({"K": k, "c_v_medio": float(np.nanmean(cv))})
        log.info("  LDA K=%d  C_v=%.4f", k, grid[-1]["c_v_medio"])
        if best is None or grid[-1]["c_v_medio"] > best[0]:
            best = (grid[-1]["c_v_medio"], k, tw, cv)
    _, k, tw, cv = best
    store.save("lda_grid", pd.DataFrame(grid))
    store.save("topics_lda", pd.DataFrame({"topic": range(k), "top_words": [", ".join(w) for w in tw], "c_v": cv}))
    store.metric("etapa3_lda", K_escolhido=k, c_v_medio=round(best[0], 4))


def run(cfg, store: Store) -> None:
    with stage("Etapa 3 — Tópicos (BERTopic e LDA)"):
        E = embed_all(cfg, store)
        T = store.load("texts").sort_values("text_id").reset_index(drop=True)
        assert (T["text_id"].to_numpy() == np.arange(len(T))).all()
        sw = stopwords(cfg)
        # amostra comum para estimar C_v nos dois modelos (mesma referência de coocorrência)
        rng = np.random.default_rng(cfg.SEED + 1)
        pool = T.index[T["n_tok"] >= cfg.LDA_MIN_TOKENS].to_numpy()
        cidx = rng.choice(pool, size=min(cfg.COHERENCE_SAMPLE, len(pool)), replace=False)
        coh_texts = [t for t in (tokenize(T.at[i, "text"], sw) for i in cidx) if len(t) >= 2]
        from gensim.corpora import Dictionary
        coh_dict = Dictionary(coh_texts)
        run_bertopic(cfg, store, E, T, sw, coh_texts, coh_dict)
        run_lda(cfg, store, T, sw, coh_texts)
