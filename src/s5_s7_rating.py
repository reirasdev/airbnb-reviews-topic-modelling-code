"""Etapas 5, 6 e 7 — ABSA por imóvel, validação de construto e rating sintético.

Etapa 5: sentença -> tópico -> aspecto; média de sentimento (1-5) por imóvel × aspecto.
Etapa 6: Spearman (principal) e Pearson entre sentimento do aspecto e subnota oficial.
Etapa 7: R_syn_raw = média igual dos aspectos disponíveis, com shrinkage empírico-bayesiano
         (aplicado ANTES da calibração, para não distorcer a distribuição calibrada) e
         R_syn_cal = quantile mapping para a distribuição de R_off (SÓ para exibição em estrelas).
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from scipy import stats

from config import GENERAL_BUCKET
from .s4_mapa_aspecto import resolve_mapping
from .utils import Store, stage

log = logging.getLogger("pipeline")


def run_absa(cfg, store: Store) -> None:
    with stage("Etapa 5 — ABSA por imóvel"):
        mapping, confirmed = resolve_mapping(cfg, store)
        S = store.load("sentences")[["listing_id", "text_id"]]
        S = S.merge(store.load("text_topics")[["text_id", "topic"]], on="text_id")
        S = S.merge(store.load("sentiment")[["text_id", "stars"]], on="text_id")
        S["aspecto"] = S["topic"].map(mapping).fillna(GENERAL_BUCKET)  # topic -1 (outlier) -> geral
        share = S["aspecto"].value_counts(normalize=True).round(4).to_dict()
        log.info("Distribuição de sentenças por aspecto: %s", share)
        A = S[S["aspecto"] != GENERAL_BUCKET]
        g = A.groupby(["listing_id", "aspecto"])["stars"].agg(["mean", "count"]).reset_index()
        g.loc[g["count"] < cfg.MIN_SENT_PER_ASPECT, "mean"] = np.nan  # pouca evidência -> aspecto ausente
        mean = g.pivot(index="listing_id", columns="aspecto", values="mean")
        cnt = g.pivot(index="listing_id", columns="aspecto", values="count").fillna(0).astype(int)
        cols = list(cfg.ASPECT_SEEDS)
        P = mean.reindex(columns=cols)
        C = cnt.reindex(columns=cols).fillna(0).astype(int).add_prefix("n_")
        prof = pd.concat([P, C], axis=1).reset_index().rename(columns={"listing_id": "id"})
        store.save("perfil_absa", prof)
        store.metric("etapa5", mapeamento_confirmado=confirmed, imoveis_com_perfil=len(prof),
                     sentencas_por_aspecto=share,
                     cobertura_por_aspecto={a: int(P[a].notna().sum()) for a in cols})


def run_validation(cfg, store: Store) -> None:
    with stage("Etapa 6 — Validação de construto (concordância com subnotas)"):
        prof, L = store.load("perfil_absa"), store.load("listings_elig")
        D = prof.merge(L, on="id")
        rows = []
        for a, sub in cfg.ASPECT_TO_SUBSCORE.items():
            d = D[[a, sub]].dropna()
            if len(d) < 10:
                rows.append({"aspecto": a, "subnota": sub, "n": len(d)})
                continue
            rs, ps = stats.spearmanr(d[a], d[sub])
            rp, pp = stats.pearsonr(d[a], d[sub])
            rows.append({"aspecto": a, "subnota": sub, "n": len(d), "spearman": rs, "p_spearman": ps,
                         "pearson": rp, "p_pearson": pp})
        V = pd.DataFrame(rows)
        store.save("validacao_construto", V)
        log.info("Concordância ABSA × subnota (sem limiar de corte):\n%s", V.round(3).to_string(index=False))
        store.metric("etapa6", spearman_por_aspecto={r["aspecto"]: round(r.get("spearman", np.nan), 3) for r in rows})


def quantile_map(x: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Casa percentis: valor de x no percentil p recebe o quantil p de target (empates de x -> posto médio)."""
    p = (stats.rankdata(x) - 0.5) / len(x)
    return np.quantile(target, p)


def build_rating(cfg, store: Store, exclude: tuple = (), shrink: bool = True) -> tuple[pd.DataFrame, float, float]:
    """R_syn por imóvel. exclude = aspectos fora da média; shrink=False deixa R_syn_raw == R_syn_pre (sem encolhimento).
    Retorna (tabela, m, R_global)."""
    prof, L = store.load("perfil_absa"), store.load("listings_elig")
    cols = list(cfg.ASPECT_SEEDS)
    spec = [c for c in cols if c not in cfg.GENERIC_ASPECTS]
    use = [c for c in cols if c not in exclude]
    prof["n_aspectos"] = prof[spec].notna().sum(axis=1)  # só aspectos específicos contam para o mínimo
    prof["n_sent_aspectos"] = prof[[f"n_{a}" for a in cols]].sum(axis=1)
    ok = prof[prof["n_aspectos"] >= cfg.MIN_ASPECTS].copy()
    log.info("Imóveis com >= %d aspectos específicos: %d de %d (excluídos por pouca evidência textual: %d)",
             cfg.MIN_ASPECTS, len(ok), len(prof), len(prof) - len(ok))
    ok["R_syn_pre"] = ok[use].mean(axis=1)  # média igual dos aspectos disponíveis
    R = ok[["id", "R_syn_pre", "n_aspectos", "n_sent_aspectos"]].merge(
        L[["id", "review_scores_rating", "number_of_reviews"]], on="id")
    v = R["number_of_reviews"].to_numpy(float)  # v = total real de avaliações (não o amostrado)
    m = cfg.SHRINKAGE_M if cfg.SHRINKAGE_M is not None else float(np.median(v))
    r_global = float(R["R_syn_pre"].mean())
    # média bayesiana: v/(v+m)*R_imovel + m/(v+m)*R_global (empirical Bayes, estilo beta-binomial)
    R["R_syn_raw"] = v / (v + m) * R["R_syn_pre"] + m / (v + m) * r_global if shrink else R["R_syn_pre"]
    R["R_syn_cal"] = np.clip(quantile_map(R["R_syn_raw"].to_numpy(), R["review_scores_rating"].to_numpy()), 1, 5)
    R = R.rename(columns={"review_scores_rating": "R_off", "number_of_reviews": "v"})
    R["diff_cal_menos_off"] = R["R_syn_cal"] - R["R_off"]
    return R, m, r_global


def run_rating(cfg, store: Store) -> None:
    with stage("Etapa 7 — Rating sintético"):
        R, m, r_global = build_rating(cfg, store, exclude=cfg.RSYN_EXCLUDE_ASPECTS, shrink=True)
        store.save("rating_sintetico", R)
        rho = stats.spearmanr(R["R_syn_raw"], R["R_off"])[0]
        store.metric("etapa7", n_imoveis=len(R), shrinkage_m=m, R_global=round(r_global, 4),
                     spearman_Rsyn_Roff=round(float(rho), 4),
                     Rsyn_raw_media=round(float(R["R_syn_raw"].mean()), 3), Rsyn_raw_dp=round(float(R["R_syn_raw"].std()), 3),
                     Roff_media=round(float(R["R_off"].mean()), 3), Roff_dp=round(float(R["R_off"].std()), 3),
                     prop_Roff_igual_5=round(float((R["R_off"] == 5).mean()), 3),
                     prop_Rsyn_cal_ge_4_99=round(float((R["R_syn_cal"] >= 4.99).mean()), 3))
