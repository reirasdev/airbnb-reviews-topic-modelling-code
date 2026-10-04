"""Etapa 17 — Tabelas de referência (benchmarks) por bairro e tipo de acomodação, e cache da tabela anúncio × aspecto
usada pela ferramenta de diagnóstico (`diagnostico.py`). Mantém só grupos com amostra suficiente (>= 30 anúncios)."""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .diagnostico import MIN_PEERS
from .s15_importancia import tabela_anuncio_aspecto
from .utils import Store, stage

log = logging.getLogger("pipeline")


def _resumo(g: pd.DataFrame, asp: list[str]) -> dict:
    out = {"n_anuncios": len(g), "nota_mediana": g["review_scores_rating"].median(), "prop_nota_ge_4_9": float((g["review_scores_rating"] >= 4.9).mean()),
           "avaliacoes_mediana": g["number_of_reviews"].median()}
    for a in asp:
        s = g[f"s_{a}"].dropna()
        out[f"sentimento_{a}_mediana"] = s.median() if len(s) >= 10 else np.nan
        out[f"sentimento_{a}_p25"] = s.quantile(.25) if len(s) >= 10 else np.nan
        out[f"sentimento_{a}_p75"] = s.quantile(.75) if len(s) >= 10 else np.nan
        out[f"cobertura_{a}"] = float(g[f"s_{a}"].notna().mean())
    return out


def run(cfg, store: Store) -> None:
    with stage("Etapa 17 — Benchmarks por bairro e tipo"):
        F = tabela_anuncio_aspecto(cfg, store)
        store.save("listing_aspect_table", F)
        asp = list(cfg.ASPECT_SEEDS)
        rows = [{"bairro": b, "tipo": t, **_resumo(g, asp)} for (b, t), g in F.groupby(["neighbourhood_cleansed", "room_type"]) if len(g) >= MIN_PEERS]
        B = pd.DataFrame(rows).sort_values("n_anuncios", ascending=False)
        C = pd.DataFrame([{"tipo": t, **_resumo(g, asp)} for t, g in F.groupby("room_type") if len(g) >= MIN_PEERS])
        store.save("benchmark_bairro_tipo", B)
        store.save("benchmark_cidade_tipo", C)
        log.info("Benchmarks: %d grupos bairro × tipo com >= %d anúncios (de %d anúncios)", len(B), MIN_PEERS, len(F))
        log.info("Maiores grupos:\n%s", B.head(8)[["bairro", "tipo", "n_anuncios", "nota_mediana", "prop_nota_ge_4_9"]].round(3).to_string(index=False))
        store.metric("etapa17", grupos_bairro_tipo=len(B), anuncios=len(F))
