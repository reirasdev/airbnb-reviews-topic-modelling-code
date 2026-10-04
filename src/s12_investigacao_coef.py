"""Investigação do coeficiente NEGATIVO de R_syn sobre a ocupação nos tetos (R_off >= 4,9 e = 5,0).

Contexto: na Análise A, R_syn (principal, sem shrinkage) tem coeficiente in-sample negativo e significativo no teto, mas sem
ganho out-of-sample. Hipóteses testadas (todas exploratórias, declaradas como tais):
  H1 (mecânica da estimativa): a ocupação estimada deriva do nº de avaliações × duração média de estadia (aproximada por
      minimum_nights). Se R_syn se correlaciona com minimum_nights, o coeficiente reflete essa via, não demanda.
      NOTA: a descrição do método da Inside Airbnb vem de conhecimento externo (o dicionário de dados não define
      estimated_*); o pesquisador deve confirmá-la na documentação oficial antes de citar.
  H2 (características do anúncio): capacidade, disponibilidade, reserva instantânea, nº de anúncios do anfitrião.
  H3 (quantidade de texto): n de aspectos / sentenças usadas no R_syn.
  H4 (zeros): imóveis sem avaliação recente têm ocupação 0 por construção.
  H5 (um aspecto): leave-one-aspect-out.
Saída: tabela `investigacao_coef` (aba Investigacao_Coef).
"""
from __future__ import annotations

import dataclasses
import logging

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from .s8_s9_analises import build_frame
from .utils import Store, stage

log = logging.getLogger("pipeline")

EXTRA_COLS = ["minimum_nights", "minimum_nights_avg_ntm", "accommodates", "availability_365", "instant_bookable",
              "calculated_host_listings_count"]


def _fit(d: pd.DataFrame, ctrl: list[str], rsyn: str, extra: list[str]) -> dict:
    """OLS da ocupação em controles + extras + R_syn padronizado (EP robusto HC3)."""
    z = (d[rsyn] - d[rsyn].mean()) / d[rsyn].std()
    X = pd.concat([d[ctrl + extra].astype(float), z.rename("R_syn_z")], axis=1)
    f = sm.OLS(d["y_estimated_occupancy_l365d"].to_numpy(float), sm.add_constant(X.to_numpy(float))).fit(cov_type="HC3")
    i = list(X.columns).index("R_syn_z") + 1
    return {"coef_noites_por_dp": f.params[i], "ep_HC3": f.bse[i], "p": f.pvalues[i], "r2_insample": f.rsquared}


def run(cfg, store: Store) -> None:
    with stage("Investigação do coeficiente negativo de R_syn no teto"):
        cfg = dataclasses.replace(cfg, INCLUDE_LTM_CONTROL=True)  # investigação sobre a análise ORIGINAL (com ltm)
        D, ctrl = build_frame(cfg, store)
        X = pd.read_csv(cfg.LISTINGS_CSV, usecols=["id", *EXTRA_COLS], low_memory=False)
        for c in ("instant_bookable",):
            X[c] = X[c].map({"t": 1.0, "f": 0.0})
        for c in ("minimum_nights", "minimum_nights_avg_ntm", "availability_365", "calculated_host_listings_count"):
            X["log_" + c] = np.log1p(X[c])
        D = D.merge(X, on="id", how="left")
        extra_nights = ["log_minimum_nights", "log_minimum_nights_avg_ntm"]
        extra_list = ["accommodates", "log_availability_365", "instant_bookable", "log_calculated_host_listings_count"]
        R = store.load("rating_sintetico")[["id", "n_aspectos", "n_sent_aspectos"]]
        D = D.merge(R, on="id", how="left")
        D["log_n_sent"] = np.log1p(D["n_sent_aspectos"])
        prof = store.load("perfil_absa")
        cols = list(cfg.ASPECT_SEEDS)
        rows = []
        corr_rows = []
        for escopo, mask in [("amostra completa", D["R_off"] > 0), ("R_off >= 4,9", D["R_off"] >= 4.9), ("R_off = 5,0", D["R_off"] == 5.0)]:
            d = D[mask].dropna(subset=extra_nights + extra_list).reset_index(drop=True)
            # vias candidatas: correlação de R_syn com cada candidato dentro do escopo
            for c in ["log_ltm", "log_v", "log_price", *extra_nights, *extra_list, "n_aspectos", "log_n_sent"]:
                corr_rows.append({"escopo": escopo, "n": len(d), "variavel": c, "spearman_com_R_syn": stats.spearmanr(d["R_syn_raw"], d[c])[0],
                                  "spearman_com_ocupacao": stats.spearmanr(d[c], d["estimated_occupancy_l365d"])[0]})
            specs = {
                "S0 controles da Análise A (replicação)": (ctrl, []),
                "S1 + minimum_nights (H1)": (ctrl, extra_nights),
                "S2 + características do anúncio (H2)": (ctrl, extra_list),
                "S3 + minimum_nights + características (H1+H2)": (ctrl, extra_nights + extra_list),
                "S4 S3 + quantidade de texto (H3)": (ctrl, extra_nights + extra_list + ["n_aspectos", "log_n_sent"]),
                "S5 S3 sem log_ltm (mostra o papel do volume recente)": ([c for c in ctrl if c != "log_ltm"], extra_nights + extra_list),
            }
            for nome, (cc, ee) in specs.items():
                rows.append({"escopo": escopo, "especificacao": nome, "n": len(d), **_fit(d, cc, "R_syn_raw", ee)})
            dz = d[d["estimated_occupancy_l365d"] > 0].reset_index(drop=True)  # H4: sem imóveis de ocupação 0
            rows.append({"escopo": escopo, "especificacao": "S6 S3 só com ocupação > 0 (H4)", "n": len(dz),
                         **_fit(dz, ctrl, "R_syn_raw", extra_nights + extra_list)})
            # H5: leave-one-aspect-out, nas covariáveis de S0
            pr = prof.set_index("id")[cols]
            for a in cols:
                keep = [c for c in cols if c != a]
                tmp = d.assign(R_loo=d["id"].map(pr[keep].mean(axis=1))).dropna(subset=["R_loo"])
                rows.append({"escopo": escopo, "especificacao": f"S7 S0 com R_syn sem o aspecto {a} (H5)", "n": len(tmp),
                             **_fit(tmp, ctrl, "R_loo", [])})
        T = pd.DataFrame(rows)
        C = pd.DataFrame(corr_rows)
        store.save("investigacao_coef", T)
        store.save("investigacao_coef_correlacoes", C)
        log.info("Coeficiente de R_syn (noites/DP) por especificação:\n%s",
                 T.drop(columns=["r2_insample"]).round(4).to_string(index=False))
        log.info("Correlações candidatas (R_syn × variável; variável × ocupação):\n%s",
                 C[C["escopo"] == "R_off = 5,0"].round(3).to_string(index=False))
        store.metric("investigacao_coef", n_linhas=len(T))
