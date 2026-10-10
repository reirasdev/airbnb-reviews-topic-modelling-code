"""Etapa 25 — Efeito do limite de 30 avaliações por anúncio (usado nas limitações).

(a) proporção de anúncios elegíveis truncados (número total de avaliações > limite), no total e entre os de nota 5,0;
(b) confiabilidade split-half do sentimento médio por anúncio (metade mais recente × metade mais antiga das 30 avaliações usadas) e Spearman-Brown para 15, 30, 60 e 120 avaliações;
(c) deriva temporal: estrelas médias das 10 avaliações mais recentes × as 20 mais antigas, nos anúncios com 30 avaliações usadas.
Usa o modelo de sentimento do store ativo. Saída: tabela `limite30` (aba Limite_30_Avaliacoes).
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .utils import Store, stage

log = logging.getLogger("pipeline")


def run(cfg, store: Store) -> None:
    with stage("Etapa 25 — Efeito do limite de avaliações por anúncio"):
        L = store.load("listings_elig")
        lim = cfg.MAX_REVIEWS_PER_LISTING
        top = L[L["review_scores_rating"] == 5.0]
        rows = [("limite de avaliações por anúncio", lim), ("anúncios elegíveis", len(L)), ("anúncios com mais avaliações que o limite (truncados)", int((L["number_of_reviews"] > lim).sum())),
                ("proporção de anúncios truncados", float((L["number_of_reviews"] > lim).mean())), ("anúncios elegíveis com nota 5,0", len(top)),
                ("proporção de truncados entre os de nota 5,0", float((top["number_of_reviews"] > lim).mean()))]
        A = store.load("sentencas_aspecto")[["listing_id", "review_id", "date", "stars"]]
        R = A.groupby(["listing_id", "review_id", "date"])["stars"].mean().reset_index().sort_values(["listing_id", "date", "review_id"], ascending=[True, False, False])
        R["posto"] = R.groupby("listing_id").cumcount()
        n = R.groupby("listing_id").size()
        full = R[R["listing_id"].isin(n[n == lim].index)]
        a = full[full["posto"] < lim // 2].groupby("listing_id")["stars"].mean()
        b = full[full["posto"] >= lim // 2].groupby("listing_id")["stars"].mean().reindex(a.index)
        r = float(np.corrcoef(a, b)[0, 1])
        sb = lambda k: k * r / (1 + (k - 1) * r)
        rows += [("anúncios com o número máximo de avaliações usadas", len(a)), ("correlação split-half (metade recente × metade antiga)", r),
                 (f"confiabilidade Spearman-Brown com {lim // 2} avaliações", sb(1)), (f"confiabilidade Spearman-Brown com {lim} avaliações", sb(2)),
                 (f"confiabilidade Spearman-Brown com {2 * lim} avaliações", sb(4)), (f"confiabilidade Spearman-Brown com {4 * lim} avaliações", sb(8))]
        rec = full[full["posto"] < 10].groupby("listing_id")["stars"].mean()
        old = full[full["posto"] >= 10].groupby("listing_id")["stars"].mean()
        rows += [("estrelas médias das 10 avaliações mais recentes", float(rec.mean())), (f"estrelas médias das {lim - 10} avaliações mais antigas", float(old.mean()))]
        T = pd.DataFrame(rows, columns=["medida", "valor"])
        store.save("limite30", T)
        log.info("Limite de avaliações:\n%s", T.round(4).to_string(index=False))
        store.metric("etapa25", prop_truncados=round(float((L["number_of_reviews"] > lim).mean()), 3), confiabilidade_30=round(sb(2), 3))
