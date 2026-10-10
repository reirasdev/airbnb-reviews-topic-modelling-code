"""Etapa 19 — Comparação dos dois modelos de sentimento no corpus (itens 1.3 e 1.4).

1.3 Descritivas de A e de B (mesmos moldes): média e mediana das estrelas esperadas (por texto único), proporção de sentenças com >= 4 e <= 2 estrelas e distribuição
    das três polaridades (por sentença).
1.4 Concordância A × B: no nível da sentença e no nível anúncio × aspecto; Spearman e Pearson das estrelas esperadas e kappa ponderado linear das polaridades; total e por
    idioma (pt, en, es, demais); matriz de confusão 3 × 3 das polaridades. No nível anúncio × aspecto a polaridade é a MODAL das frases do anúncio no aspecto (empate = neutro).
Saídas compartilhadas (prefixo cmp_): cmp_descritivas, cmp_concordancia, cmp_confusao_polaridade, cmp_concordancia_aspecto.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import cohen_kappa_score

from config import GENERAL_BUCKET
from .sentimento import load_sentiment
from .utils import Store, stage

log = logging.getLogger("pipeline")
IDIOMAS = ("pt", "en", "es")


def _grupo_idioma(l: pd.Series) -> pd.Series:
    return l.where(l.isin(IDIOMAS), "demais")


def _par(a: pd.Series, b: pd.Series, ca: pd.Series, cb: pd.Series) -> dict:
    return {"n": len(a), "spearman_estrelas": float(stats.spearmanr(a, b)[0]) if len(a) > 2 else np.nan,
            "pearson_estrelas": float(np.corrcoef(a, b)[0, 1]) if len(a) > 2 else np.nan,
            "kappa_ponderado_linear_polaridade": float(cohen_kappa_score(ca, cb, weights="linear", labels=[0, 1, 2])) if len(a) > 2 else np.nan,
            "concordancia_polaridade": float((ca == cb).mean())}


def _modal(x: pd.Series) -> int:
    c = np.bincount(x.to_numpy(), minlength=3)
    top = np.flatnonzero(c == c.max())
    return int(top[0]) if len(top) == 1 else 1  # empate entre classes = neutro


def run(cfg, store: Store) -> None:
    with stage("Etapa 19 — Comparação dos modelos de sentimento A e B"):
        sA, sB = Store(cfg, suffix=""), Store(cfg, suffix="__B")
        A, B = load_sentiment(sA), load_sentiment(sB)
        T = sA.load("texts")[["text_id"]]
        MA = T.merge(A[["text_id", "stars", "cls"]], on="text_id").rename(columns={"stars": "a", "cls": "ca"})
        MB = B[["text_id", "stars", "cls"]].rename(columns={"stars": "b", "cls": "cb"})
        M = MA.merge(MB, on="text_id", how="inner")
        completo = len(M) == len(T)
        log.info("Textos únicos com A e B: %d de %d%s", len(M), len(T), "" if completo else "  [PARCIAL: B ainda incompleto]")

        S = sA.load("sentences")[["sent_id", "listing_id", "text_id", "lang"]].merge(M, on="text_id")
        S["grupo"] = _grupo_idioma(S["lang"])

        # ---- 1.3 descritivas
        rows = []
        for nome, col, ccol in (("A", "a", "ca"), ("B", "b", "cb")):
            rows.append({"modelo": nome, "textos_unicos": len(M), "estrelas_media_texto": float(M[col].mean()), "estrelas_mediana_texto": float(M[col].median()),
                         "prop_sentencas_ge_4_estrelas": float((S[col] >= 4).mean()), "prop_sentencas_le_2_estrelas": float((S[col] <= 2).mean()),
                         "prop_sentencas_negativa": float((S[ccol] == 0).mean()), "prop_sentencas_neutra": float((S[ccol] == 1).mean()),
                         "prop_sentencas_positiva": float((S[ccol] == 2).mean()), "sentencas": len(S)})
        D = pd.DataFrame(rows)
        sA.save("cmp_descritivas", D)

        # ---- 1.4 concordância na sentença (total e por idioma)
        rows = [{"nivel": "sentença", "grupo": "total", **_par(S["a"], S["b"], S["ca"], S["cb"])}]
        for g in (*IDIOMAS, "demais"):
            d = S[S["grupo"] == g]
            rows.append({"nivel": "sentença", "grupo": g, **_par(d["a"], d["b"], d["ca"], d["cb"])})
        conf = pd.crosstab(S["ca"].map({0: "A negativo", 1: "A neutro", 2: "A positivo"}), S["cb"].map({0: "B negativo", 1: "B neutro", 2: "B positivo"}))
        sA.save("cmp_confusao_polaridade", conf.reset_index())

        # ---- 1.4 concordância anúncio × aspecto (aspecto do BERTopic; sentenças com aspecto, exceto 'geral')
        P = sA.load("sentencas_aspecto")[["sent_id", "listing_id", "text_id", "aspecto", "lang"]]
        P = P[P["aspecto"] != GENERAL_BUCKET].merge(M, on="text_id")
        g = P.groupby(["listing_id", "aspecto"]).agg(n=("a", "size"), a=("a", "mean"), b=("b", "mean"), ca=("ca", _modal), cb=("cb", _modal)).reset_index()
        g = g[g["n"] >= cfg.MIN_SENT_PER_ASPECT]
        rows.append({"nivel": "anúncio × aspecto", "grupo": "total", **_par(g["a"], g["b"], g["ca"], g["cb"])})
        # por idioma predominante do anúncio no aspecto e por aspecto
        lang_mode = P.groupby(["listing_id", "aspecto"])["lang"].agg(lambda x: x.value_counts().index[0]).rename("lang_pred").reset_index()
        g = g.merge(lang_mode, on=["listing_id", "aspecto"])
        g["grupo"] = _grupo_idioma(g["lang_pred"])
        for gr in (*IDIOMAS, "demais"):
            d = g[g["grupo"] == gr]
            rows.append({"nivel": "anúncio × aspecto", "grupo": f"idioma predominante: {gr}", **_par(d["a"], d["b"], d["ca"], d["cb"])})
        by_asp = []
        for a, d in g.groupby("aspecto"):
            by_asp.append({"aspecto": a, **_par(d["a"], d["b"], d["ca"], d["cb"])})
        C = pd.DataFrame(rows)
        sA.save("cmp_concordancia", C)
        sA.save("cmp_concordancia_aspecto", pd.DataFrame(by_asp))
        log.info("Descritivas A × B:\n%s", D.round(4).to_string(index=False))
        log.info("Concordância A × B:\n%s", C.round(4).to_string(index=False))
        log.info("Matriz de confusão das polaridades (linhas A, colunas B):\n%s", conf.to_string())
        log.info("Concordância por aspecto (anúncio × aspecto):\n%s", pd.DataFrame(by_asp).round(3).to_string(index=False))
        sA.metric("etapa19", textos_com_A_e_B=len(M), completo=bool(completo))
