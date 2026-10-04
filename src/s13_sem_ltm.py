"""Verificação da fórmula da ocupação estimada e reanálise SEM o controle de avaliações dos últimos 12 meses.

Achado: estimated_occupancy_l365d = min(255, number_of_reviews_ltm * 2 * max(3, minimum_nights)) em 100% dos anúncios, e
estimated_revenue_l365d = price * ocupação. Logo, controlar por number_of_reviews_ltm "controla o desfecho". Esta etapa:
  (a) documenta a verificação (tabela `formula_ocupacao`);
  (b) refaz as Análises A e B SEM log_ltm (apenas volume total, preço, tipo e bairro, como na spec original), para os
      desfechos ocupação, receita e número de avaliações nos últimos 12 meses (log1p; desfecho sem construção);
Saídas: `formula_ocupacao`, `sem_ltm_modelos`, `sem_ltm_diferencas`, `sem_ltm_faixas`.
"""
from __future__ import annotations

import dataclasses
import logging

import numpy as np
import pandas as pd

import statsmodels.api as sm

from .s8_s9_analises import build_frame, run_analise_a, run_analise_b
from .utils import Store, stage

log = logging.getLogger("pipeline")


def verificar_formula(cfg) -> pd.DataFrame:
    L = pd.read_csv(cfg.LISTINGS_CSV, usecols=["number_of_reviews_ltm", "minimum_nights", "minimum_nights_avg_ntm", "price",
                                                "estimated_occupancy_l365d", "estimated_revenue_l365d"], low_memory=False)
    y = L["estimated_occupancy_l365d"]
    rows = []
    for nome, stay in [("max(3, minimum_nights)", np.maximum(3, L["minimum_nights"])),
                       ("max(3, minimum_nights_avg_ntm)", np.maximum(3, L["minimum_nights_avg_ntm"])),
                       ("3 fixo", 3)]:
        p = np.minimum(255, L["number_of_reviews_ltm"] * 2 * stay)
        rows.append({"formula": f"min(255, ltm × 2 × {nome})", "n": len(L), "prop_exata": float((abs(p - y) < 0.5).mean()),
                     "R2": float(1 - ((p - y) ** 2).sum() / ((y - y.mean()) ** 2).sum())})
    price = pd.to_numeric(L["price"].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
    ok = L["estimated_revenue_l365d"].notna()
    rows.append({"formula": "receita = preço × ocupação", "n": int(ok.sum()),
                 "prop_exata": float((abs(price * y - L["estimated_revenue_l365d"])[ok] <= 1).mean()), "R2": np.nan})
    rows.append({"formula": "ltm = 0 ⇒ ocupação = 0", "n": int((L["number_of_reviews_ltm"] == 0).sum()),
                 "prop_exata": float((y[L["number_of_reviews_ltm"] == 0] == 0).mean()), "R2": np.nan})
    return pd.DataFrame(rows)


def coef_forma_flexivel(cfg, store: Store) -> pd.DataFrame:
    """Coeficiente de R_syn (z) sobre a ocupação nos tetos, com controles da Análise A (log_ltm linear), com forma flexível
    em ltm/estadia e com a fórmula exata. Mostra que o coeficiente negativo é artefato de má especificação."""
    D, ctrl = build_frame(cfg, store)  # cfg com INCLUDE_LTM_CONTROL=True (análise original)
    X = pd.read_csv(cfg.LISTINGS_CSV, usecols=["id", "minimum_nights"])
    D = D.merge(X, on="id")
    D["stay"] = np.maximum(3, D["minimum_nights"])
    D["ltm"] = D["number_of_reviews_ltm"]
    D["raw"] = D["ltm"] * 2 * D["stay"]
    D["cap"] = (D["raw"] >= 255).astype(float)
    D["ltm2"], D["raw2"] = D["ltm"] ** 2, D["raw"] ** 2
    D["ltm_x_stay"] = D["ltm"] * D["stay"]
    D["f_exata"] = np.minimum(255, D["raw"])
    rows = []
    for escopo, m in [("R_off >= 4,9", D["R_off"] >= 4.9), ("R_off = 5,0", D["R_off"] == 5.0)]:
        d = D[m]
        z = (d["R_syn_raw"] - d["R_syn_raw"].mean()) / d["R_syn_raw"].std()
        for nome, extra in [("controles da Análise A (log_ltm linear)", []),
                            ("+ forma flexível (ltm, ltm², ltm×estadia, raw, raw², indicador de teto)", ["ltm", "ltm2", "ltm_x_stay", "raw", "raw2", "cap"]),
                            ("+ fórmula exata min(255, 2·ltm·estadia)", ["f_exata"])]:
            Z = pd.concat([d[ctrl + extra].astype(float), z.rename("z")], axis=1)
            f = sm.OLS(d["estimated_occupancy_l365d"].to_numpy(float), sm.add_constant(Z.to_numpy(float))).fit(cov_type="HC3")
            rows.append({"escopo": escopo, "n": len(d), "controles": nome, "coef_R_syn_z": f.params[-1], "p": f.pvalues[-1],
                         "r2_insample": f.rsquared})
    return pd.DataFrame(rows)


def run(cfg, store: Store) -> None:
    with stage("Verificação da fórmula e reanálise sem o controle de avaliações recentes"):
        F = verificar_formula(cfg)
        store.save("formula_ocupacao", F)
        log.info("Fórmula da ocupação estimada:\n%s", F.round(4).to_string(index=False))

        C = coef_forma_flexivel(cfg, store)
        store.save("coef_forma_flexivel", C)
        log.info("Coeficiente de R_syn no teto, por forma funcional dos controles:\n%s", C.round(4).to_string(index=False))

        c2 = dataclasses.replace(cfg, INCLUDE_LTM_CONTROL=False, LOG_OUTCOMES=(*cfg.LOG_OUTCOMES, "number_of_reviews_ltm"))
        outs = (cfg.PRIMARY_OUTCOME, cfg.SECONDARY_OUTCOME, "number_of_reviews_ltm")
        A, D, Bs = [], [], []
        for var in ("sem_shrinkage", "com_shrinkage"):
            tab = f"rating_sintetico__{var}"
            a, d, _ = run_analise_a(c2, store, tab, persist=False, outcomes=outs)
            b, _ = run_analise_b(c2, store, tab, persist=False)
            A.append(a.assign(variante=var)); D.append(d.assign(variante=var)); Bs.append(b.assign(variante=var))
        A, D, Bs = pd.concat(A), pd.concat(D), pd.concat(Bs)
        store.save("sem_ltm_modelos", A)
        store.save("sem_ltm_diferencas", D)
        store.save("sem_ltm_faixas", Bs)
        for var in ("sem_shrinkage", "com_shrinkage"):
            log.info("SEM controle ltm — R² OOS (%s):\n%s", var, A[A.variante == var][["desfecho", "escopo", "n", "modelo", "r2_oos_medio"]]
                     .round(4).to_string(index=False))
            log.info("SEM controle ltm — ganho de R² (%s):\n%s", var, D[(D.variante == var) & D.comparacao.isin(
                ["M2 R_syn − M1 R_off", "M3 R_off + R_syn − M1 R_off", "M1 R_off − M0 controles"])][
                ["desfecho", "escopo", "comparacao", "delta_r2_medio", "p2.5", "p97.5"]].round(4).to_string(index=False))
        store.metric("sem_ltm", formula_exata_prop=float(F.iloc[0]["prop_exata"]))
