"""Etapa 1 — Ingestão, limpeza, segmentação em sentenças e idioma.

Saídas (Store): listings_elig, sentences, texts, corpus_stats, lang_dist.
A sentença é a unidade do ABSA; sentences guarda sentença -> avaliação -> imóvel.
Sentenças com texto idêntico compartilham um text_id: sentimento/embedding/tópico são
calculados uma vez por texto único (muitas sentenças são "Excelente!", "Recomendo.").
"""
from __future__ import annotations

import html
import logging
import re

import numpy as np
import pandas as pd

from .utils import Store, stage

log = logging.getLogger("pipeline")

_BR = re.compile(r"<br\s*/?>", re.I)
_TAG = re.compile(r"<[^>]+>")
# Fronteira de sentença: pontuação final + espaço; quebra de linha; ou pontuação colada a maiúscula
# ("Ótimo.Recomendo"). A 3ª alternativa exige maiúscula depois, para não cortar decimais ("4.5").
_SPLIT = re.compile(r"(?<=[.!?…])\s+|\n+|(?<=[.!?…])(?=[A-ZÁÉÍÓÚÀÂÊÔÃÕÇÑ¿¡])")
_HAS_WORD = re.compile(r"\w")
_AUTO = re.compile(r"automated posting|canceled this reservation|reservation was canceled|cancelou esta reserva|cancelada automaticamente",
                   re.I)


def parse_price(s: pd.Series) -> pd.Series:
    """'$2,700.00' -> 2700.0 (NaN se vazio)."""
    return pd.to_numeric(s.astype("string").str.replace(r"[^0-9.]", "", regex=True), errors="coerce")


def clean_comments(s: pd.Series) -> pd.Series:
    """Remove HTML (<br/> vira quebra de linha, que também segmenta), normaliza espaços."""
    s = s.str.replace(_BR, "\n", regex=True).str.replace(_TAG, " ", regex=True)
    s = s.map(html.unescape)
    s = s.str.replace(r"[ \t\r\f\v ]+", " ", regex=True).str.replace(r"\s*\n\s*", "\n", regex=True)
    return s.str.strip()


def split_sentences(text: str, min_tokens: int) -> list[str]:
    """Segmenta por regex (independe de idioma; reviews são informais e mal pontuadas).

    Fragmentos com < min_tokens tokens são fundidos ao vizinho para não gerar sentenças
    sem conteúdo ("Ótimo."). Uma avaliação curta inteira é mantida como está.
    """
    out: list[str] = []
    carry = ""
    for piece in _SPLIT.split(text):
        piece = piece.strip()
        if not piece or not _HAS_WORD.search(piece):
            continue
        if carry:
            piece, carry = f"{carry} {piece}", ""
        if len(piece.split()) < min_tokens:
            carry = piece
        else:
            out.append(piece)
    if carry:
        if out:
            out[-1] = f"{out[-1]} {carry}"
        else:
            out.append(carry)
    return out


def detect_languages(texts: list[str], lang_set: tuple) -> list[str]:
    """Idioma por avaliação (lingua, restrito a lang_set); cada sentença herda o idioma da avaliação.

    Detectar por sentença curta é pouco confiável; a spec usa o idioma só para caracterização.
    # EXTENSÃO FUTURA: robustez por idioma.
    """
    from lingua import IsoCode639_1, Language, LanguageDetectorBuilder

    langs = [Language.from_iso_code_639_1(getattr(IsoCode639_1, c.upper())) for c in lang_set]
    det = LanguageDetectorBuilder.from_languages(*langs).build()
    res = det.detect_languages_in_parallel_of([t.replace("\n", " ")[:400] for t in texts])
    return [r.iso_code_639_1.name.lower() if r is not None else "und" for r in res]


def run(cfg, store: Store) -> None:
    with stage("Etapa 1 — Ingestão e pré-processamento"):
        L = pd.read_csv(cfg.LISTINGS_CSV, low_memory=False)
        R = pd.read_csv(cfg.REVIEWS_CSV, low_memory=False)
        log.info("listings %s | reviews %s", L.shape, R.shape)
        stats: dict = {"imoveis_total": len(L), "avaliacoes_total": len(R)}

        # --- imóveis elegíveis ---
        L["price_num"] = parse_price(L["price"])
        elig = L[L["review_scores_rating"].notna() & (L["review_scores_rating"] > 0)
                 & (L["number_of_reviews"] >= cfg.MIN_REVIEWS)].copy()
        stats["imoveis_com_nota"] = int(L["review_scores_rating"].notna().sum())
        stats["imoveis_elegiveis(nota>0, v>=MIN_REVIEWS)"] = len(elig)
        if cfg.DEV_SAMPLE_FRAC < 1:
            elig = elig.sample(frac=cfg.DEV_SAMPLE_FRAC, random_state=cfg.SEED)
            log.warning("DEV_SAMPLE_FRAC=%s: usando %d imóveis (resultados NÃO são finais)", cfg.DEV_SAMPLE_FRAC, len(elig))
        stats["imoveis_analisados"] = len(elig)

        # --- limpeza de avaliações ---
        R = R.dropna(subset=["comments"]).copy()
        R["comments"] = clean_comments(R["comments"].astype(str))
        n0 = len(R)
        R = R[~R["comments"].str.contains(_AUTO)]
        stats["avaliacoes_automaticas_removidas"] = n0 - len(R)
        R = R[R["comments"].str.split().str.len() >= 2]
        n1 = len(R)
        R = R.drop_duplicates(["listing_id", "reviewer_id", "comments"])
        stats["avaliacoes_duplicadas_removidas"] = n1 - len(R)
        R = R[R["listing_id"].isin(elig["id"])]
        stats["avaliacoes_dos_imoveis_analisados"] = len(R)

        # --- N mais recentes por imóvel (custo computacional; v do shrinkage segue sendo o total real) ---
        if cfg.MAX_REVIEWS_PER_LISTING:
            R = R.sort_values(["listing_id", "date", "id"], ascending=[True, False, False])
            R = R.groupby("listing_id", sort=False).head(cfg.MAX_REVIEWS_PER_LISTING)
        R = R.sort_values("id").reset_index(drop=True)
        stats["avaliacoes_usadas"] = len(R)

        # --- mascara o primeiro nome do anfitrião (vira ruído nos tópicos) ---
        names = elig.set_index("id")["host_name"].astype("string").str.split().str[0]
        names = names[names.str.len() >= 3].dropna()
        pats = {k: re.compile(rf"\b{re.escape(v)}\b", re.I) for k, v in names.items()}
        R["comments"] = [pats[l].sub(" ", t) if l in pats else t for l, t in zip(R["listing_id"], R["comments"])]

        # --- idioma por avaliação ---
        log.info("Detectando idioma em %d avaliações...", len(R))
        R["lang"] = detect_languages(R["comments"].tolist(), cfg.LANG_SET)

        # --- sentenças ---
        log.info("Segmentando em sentenças...")
        sents = [split_sentences(t, cfg.MIN_SENT_TOKENS) for t in R["comments"]]
        n_per = np.array([len(x) for x in sents])
        S = pd.DataFrame({
            "review_id": np.repeat(R["id"].to_numpy(), n_per),
            "listing_id": np.repeat(R["listing_id"].to_numpy(), n_per),
            "date": np.repeat(R["date"].to_numpy(), n_per),
            "lang": np.repeat(R["lang"].to_numpy(), n_per),
            "text": [s for x in sents for s in x],
        })
        S = S[S["text"].str.len() > 0].reset_index(drop=True)
        S.insert(0, "sent_id", np.arange(len(S), dtype=np.int64))
        key = S["text"].str.lower().str.strip()
        S["text_id"], uniq = pd.factorize(key)
        first = S.drop_duplicates("text_id").set_index("text_id")["text"].sort_index()
        T = pd.DataFrame({"text_id": first.index.astype("int64"), "text": first.to_numpy()})
        T["n_tok"] = T["text"].str.split().str.len().astype("int32")
        S["text_id"] = S["text_id"].astype("int64")

        stats.update({"sentencas": len(S), "textos_unicos": len(T),
                      "sentencas_por_avaliacao(media)": round(float(n_per.mean()), 2),
                      "tokens_por_sentenca(media)": round(float(T["n_tok"].mean()), 2)})
        lang = (R["lang"].value_counts(normalize=True).rename("prop_avaliacoes").to_frame()
                .join(R["lang"].value_counts().rename("n_avaliacoes")).reset_index(names="idioma"))

        keep = ["id", "neighbourhood_cleansed", "room_type", "number_of_reviews", "number_of_reviews_ltm",
                "reviews_per_month", "estimated_occupancy_l365d", "estimated_revenue_l365d", "price_num",
                "review_scores_rating", *cfg.ASPECT_TO_SUBSCORE.values()]
        store.save("listings_elig", elig[keep].reset_index(drop=True))
        store.save("sentences", S)
        store.save("texts", T)
        store.save("lang_dist", lang)
        store.save("corpus_stats", pd.DataFrame({"metrica": list(stats), "valor": list(stats.values())}))
        store.metric("etapa1", **stats)
