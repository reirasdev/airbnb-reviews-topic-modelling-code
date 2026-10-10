"""Fase 3 — o LDA como CHECAGEM do método de tópicos (não como competidor do BERTopic).

Pergunta: os resultados por aspecto dependem do método de tópicos? O BERTopic continua sendo o método; o LDA (K = 10, já ajustado na etapa 3) é usado para
atribuir cada sentença a um aspecto por um caminho independente e comparar o perfil de sentimento, a validade de construto e a importância dos aspectos.

Etapa 22 (independe do modelo de sentimento): reajusta o LDA com a mesma amostra, dicionário e semente da etapa 3 (e confere que reproduz os tópicos gravados),
atribui as ~1,37 milhão de textos únicos ao tópico dominante e propõe um mapa PROVISÓRIO tópico -> aspecto ("a confirmar pelo pesquisador"; tópico que
mistura aspectos é "misto" e fica fora do perfil; não se força).
Etapa 23 (usa o modelo de sentimento ativo): perfil por aspecto via LDA, concordância com o perfil do BERTopic, validade de construto e decomposição LMG.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from scipy import stats

from config import GENERAL_BUCKET
from .embeddings import get_embedder
from .s15_importancia import lmg, prep
from .s3_topicos import stopwords, tokenize
from .utils import Store, stage

log = logging.getLogger("pipeline")
MISTO = "misto"


def _ajustar_lda(cfg, store: Store):
    """Reajusta o LDA exatamente como em s3_topicos.run_lda (mesma amostra, filtros, semente) e devolve (modelo, dicionário, tokens de todos os textos)."""
    from gensim.corpora import Dictionary
    from gensim.models import LdaModel

    T = store.load("texts").sort_values("text_id").reset_index(drop=True)
    sw = stopwords(cfg)
    toks = T["text"].map(lambda s: tokenize(s, sw))
    k = len(store.load("topics_lda"))
    rng = np.random.default_rng(cfg.SEED)
    pool = np.where(toks.map(len) >= cfg.LDA_MIN_TOKENS)[0]
    idx = np.sort(rng.choice(pool, size=min(cfg.LDA_SAMPLE, len(pool)), replace=False))
    sample = [toks.iloc[i] for i in idx]
    dic = Dictionary(sample)
    dic.filter_extremes(no_below=20, no_above=0.5)
    corpus = [dic.doc2bow(d) for d in sample]
    lda = LdaModel(corpus, id2word=dic, num_topics=k, random_state=cfg.SEED, passes=cfg.LDA_PASSES, iterations=50, chunksize=10_000)
    return lda, dic, toks, T


def run_prep(cfg, store: Store) -> None:
    with stage("Etapa 22 — LDA: reajuste, atribuição e mapa provisório de aspectos"):
        lda, dic, toks, T = _ajustar_lda(cfg, store)
        guardado = store.load("topics_lda")
        novas = [", ".join(dic[w] for w, _ in lda.get_topic_terms(t, cfg.TOPIC_TOP_WORDS)) for t in range(lda.num_topics)]
        iguais = [a == b for a, b in zip(novas, guardado["top_words"])]
        log.info("Reajuste do LDA reproduz os tópicos gravados: %d de %d tópicos idênticos", sum(iguais), len(iguais))
        if not all(iguais):
            log.warning("Tópicos reajustados diferem dos gravados; usando os reajustados e registrando a divergência")
        store.metric("etapa22", topicos_identicos_aos_gravados=int(sum(iguais)), K=int(lda.num_topics))

        # atribuição de todos os textos únicos ao tópico dominante (gamma da inferência variacional)
        topic = np.full(len(T), -1, dtype="int16")
        prob = np.zeros(len(T), dtype="float32")
        bows = [dic.doc2bow(d) for d in toks]
        for i in range(0, len(bows), 20_000):
            blk = bows[i:i + 20_000]
            ok = [j for j, b in enumerate(blk) if b]
            if not ok:
                continue
            gamma, _ = lda.inference([blk[j] for j in ok])
            gamma = gamma / gamma.sum(axis=1, keepdims=True)
            topic[[i + j for j in ok]] = gamma.argmax(1)
            prob[[i + j for j in ok]] = gamma.max(1)
        store.save("lda_shared_atribuicao", pd.DataFrame({"text_id": T["text_id"].to_numpy(), "lda_topic": topic, "lda_prob": prob}))
        log.info("Textos sem palavras no vocabulário do LDA (sem tópico): %.1f%%", 100 * float((topic == -1).mean()))

        # mapa provisório: similaridade do vetor das palavras do tópico com o vetor de cada aspecto (mesma construção da etapa 4)
        model = get_embedder(cfg)
        aspects = list(cfg.ASPECT_SEEDS)
        A = []
        for a in aspects:
            v = model.encode(cfg.ASPECT_SEEDS[a], normalize_embeddings=True).mean(0)
            A.append(v / np.linalg.norm(v))
        W = model.encode([n.replace(",", " ") for n in novas], normalize_embeddings=True)
        sim = W @ np.vstack(A).T
        M = pd.DataFrame(sim, columns=[f"sim_{a}" for a in aspects])
        order = np.argsort(-sim, axis=1)
        M.insert(0, "lda_topic", range(lda.num_topics))
        M.insert(1, "top_words", novas)
        M["aspecto_mais_similar"] = [aspects[o[0]] for o in order]
        M["margem_1o_2o"] = [float(sim[i, o[0]] - sim[i, o[1]]) for i, o in enumerate(order)]
        M["n_textos"] = [int((topic == t).sum()) for t in range(lda.num_topics)]
        prov = cfg.LDA_ASPECT_MAP_PROVISORIO
        M["mapeamento_provisorio"] = [prov.get(t, MISTO) for t in range(lda.num_topics)]
        M["decisao_pesquisador"] = ""
        M["status"] = "provisório: a confirmar pelo pesquisador"
        store.save("lda_shared_mapa", M)
        log.info("Mapa provisório LDA → aspecto:\n%s", M[["lda_topic", "top_words", "aspecto_mais_similar", "margem_1o_2o", "n_textos", "mapeamento_provisorio"]]
                 .round(3).to_string(index=False))


def _mapa(cfg, store: Store) -> dict[int, str]:
    M = store.load("lda_shared_mapa")
    dec = M["decisao_pesquisador"].fillna("").astype(str).str.strip()
    return {int(t): (d if d else p) for t, d, p in zip(M["lda_topic"], dec, M["mapeamento_provisorio"])}


def _perfil(A: pd.DataFrame, col: str, cfg) -> pd.DataFrame:
    """Média de estrelas por anúncio × aspecto (aspectos específicos e satisfacao_geral; 'geral' e 'misto' ficam fora), com o mínimo de frases do estudo."""
    S = A[~A[col].isin([GENERAL_BUCKET, MISTO])]
    g = S.groupby(["listing_id", col])["stars"].agg(["mean", "count"]).reset_index()
    return g[g["count"] >= cfg.MIN_SENT_PER_ASPECT].pivot(index="listing_id", columns=col, values="mean")


def run_comparacao(cfg, store: Store) -> None:
    with stage(f"Etapa 23 — Checagem LDA com o sentimento {cfg.SENTIMENT_SOURCE}"):
        asg = store.load("lda_shared_atribuicao")
        mapa = _mapa(cfg, store)
        A = store.load("sentencas_aspecto")[["sent_id", "listing_id", "text_id", "stars", "aspecto"]].merge(asg, on="text_id", how="left")
        A["lda_topic"] = A["lda_topic"].fillna(-1).astype(int)
        A["aspecto_lda"] = A["lda_topic"].map(mapa).fillna(GENERAL_BUCKET)  # sem tópico -> fora do perfil
        A["aspecto"] = A["aspecto"].astype(str)

        # (3.2a) concordância das atribuições por sentença
        dois = A[~A["aspecto"].isin([GENERAL_BUCKET]) & ~A["aspecto_lda"].isin([GENERAL_BUCKET, MISTO])]
        conc = {"sentencas": len(A), "prop_mesmo_aspecto_total": float((A["aspecto"] == A["aspecto_lda"]).mean()),
                "sentencas_com_aspecto_nos_dois_metodos": len(dois), "prop_mesmo_aspecto_entre_as_com_aspecto_nos_dois": float((dois["aspecto"] == dois["aspecto_lda"]).mean()),
                "prop_sentencas_misto_no_lda": float((A["aspecto_lda"] == MISTO).mean()), "prop_sentencas_sem_topico_lda": float((A["lda_topic"] == -1).mean())}
        store.save("lda_concordancia_sentencas", pd.DataFrame({"medida": list(conc), "valor": list(conc.values())}))

        # (3.2b) perfil por anúncio e correlação com o perfil do BERTopic, por aspecto
        P_b, P_l = _perfil(A, "aspecto", cfg), _perfil(A, "aspecto_lda", cfg)
        L = store.load("listings_elig").set_index("id")
        rows = []
        for a in cfg.ASPECT_SEEDS:
            if a in P_l.columns and a in P_b.columns:
                d = pd.concat([P_b[a].rename("b"), P_l[a].rename("l")], axis=1).dropna()
                rs = stats.spearmanr(d["b"], d["l"])[0] if len(d) > 30 else np.nan
            else:
                d, rs = pd.DataFrame(), np.nan
            rows.append({"aspecto": a, "anuncios_com_aspecto_bertopic": int(P_b[a].notna().sum()) if a in P_b else 0,
                         "anuncios_com_aspecto_lda": int(P_l[a].notna().sum()) if a in P_l else 0, "anuncios_nos_dois": len(d), "spearman_perfil_bertopic_lda": rs})
        store.save("lda_perfil_correlacao", pd.DataFrame(rows))

        # (3.3a) validade de construto com o perfil LDA (tabela principal: Spearman e Pearson com a subnota)
        rows = []
        for a, sub in cfg.ASPECT_TO_SUBSCORE.items():
            if a not in P_l.columns:
                rows.append({"aspecto": a, "subnota": sub, "n": 0, "spearman_lda": np.nan, "pearson_lda": np.nan})
                continue
            d = pd.concat([P_l[a].rename("x"), L[sub].rename("y")], axis=1).dropna()
            rows.append({"aspecto": a, "subnota": sub, "n": len(d), "spearman_lda": stats.spearmanr(d["x"], d["y"])[0] if len(d) > 30 else np.nan,
                         "pearson_lda": stats.pearsonr(d["x"], d["y"])[0] if len(d) > 30 else np.nan})
        V = pd.DataFrame(rows)
        Vb = store.load("validacao_construto")[["aspecto", "n", "spearman", "pearson"]].rename(columns={"n": "n_bertopic", "spearman": "spearman_bertopic", "pearson": "pearson_bertopic"})
        V = V.merge(Vb, on="aspecto", how="left")
        V["mesmo_sinal"] = np.where(V["spearman_lda"].notna() & V["spearman_bertopic"].notna(), np.sign(V["spearman_lda"]) == np.sign(V["spearman_bertopic"]), np.nan)
        store.save("lda_validade", V)

        # (3.3b) decomposição LMG da nota global com o perfil LDA vs BERTopic (aspectos com cobertura mínima nos dois)
        cobertura = {a: int(P_l[a].notna().sum()) for a in P_l.columns}
        asp = [a for a in cfg.ASPECT_SEEDS if cobertura.get(a, 0) >= 500]
        F = L[["review_scores_rating"]].copy()
        for a in asp:
            F[f"s_{a}"] = P_l[a].reindex(F.index)
        Fb = L[["review_scores_rating"]].copy()
        for a in asp:
            Fb[f"s_{a}"] = P_b[a].reindex(Fb.index) if a in P_b else np.nan
        out = []
        for nome, FF in (("lda", F), ("bertopic_mesmos_aspectos", Fb)):
            X, y, _ = prep(FF.reset_index(drop=True), asp, "review_scores_rating")
            c, r2 = lmg(X, y)
            out += [{"metodo": nome, "aspecto": a, "parcela_do_R2": v / r2 if r2 > 0 else np.nan, "R2_total": r2, "n": len(y)} for a, v in zip(asp, c)]
        Lm = pd.DataFrame(out)
        W = Lm.pivot(index="aspecto", columns="metodo", values="parcela_do_R2")
        W["posto_lda"], W["posto_bertopic"] = W["lda"].rank(ascending=False), W["bertopic_mesmos_aspectos"].rank(ascending=False)
        W = W.reset_index()
        rho = stats.spearmanr(W["lda"], W["bertopic_mesmos_aspectos"])[0] if len(W) > 3 else np.nan
        store.save("lda_importancia", Lm)
        store.save("lda_importancia_comparacao", W)
        store.metric("etapa23", spearman_ordenacao_importancia=round(float(rho), 3) if np.isfinite(rho) else None, aspectos_na_importancia=asp, **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in conc.items()})
        log.info("Concordância das atribuições:\n%s", pd.Series(conc).round(4).to_string())
        log.info("Correlação do perfil BERTopic × LDA por aspecto:\n%s", pd.DataFrame(rows if False else store.load("lda_perfil_correlacao")).round(3).to_string(index=False))
        log.info("Validade de construto com LDA:\n%s", V.round(3).to_string(index=False))
        log.info("Importância (LMG, nota global) — LDA vs BERTopic nos mesmos aspectos:\n%s\nSpearman da ordenação: %.3f", W.round(3).to_string(index=False), rho)
