"""Etapas 8 e 9 — Análise A (poder explicativo) e Análise B (monotonicidade e reordenamento).

Trabalho de mensuração e associação: nenhuma interpretação causal.

Ressalvas metodológicas registradas no log/Excel:
  * estimated_occupancy_l365d / estimated_revenue_l365d são estimativas da Inside Airbnb
    derivadas em grande parte do volume de avaliações recentes; por isso os controles de
    volume (total, últimos 12 meses) são obrigatórios e o resultado deve ser lido com essa
    limitação. Receita ≈ ocupação × preço, daí log(preço) como controle.
  * Todos os modelos de um mesmo cenário usam a MESMA amostra e os MESMOS folds.
  * Modelos além dos pedidos: M0 (só controles) e M3 (R_off + R_syn_raw), necessários para o
    R² incremental ("R_syn explica além de R_off?"). Não são testes não-aninhados.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import RepeatedKFold

from .utils import Store, stage

log = logging.getLogger("pipeline")


def build_frame(cfg, store: Store, rating_table: str = "rating_sintetico") -> tuple[pd.DataFrame, list[str]]:
    """Junta R_off, R_syn_raw, desfechos e controles. Retorna (df, colunas de controle)."""
    R, L = store.load(rating_table), store.load("listings_elig")
    D = R[["id", "R_off", "R_syn_raw", "R_syn_cal", "v"]].merge(
        L[["id", "neighbourhood_cleansed", "room_type", "number_of_reviews_ltm", "price_num",
           cfg.PRIMARY_OUTCOME, cfg.SECONDARY_OUTCOME]], on="id")
    n0 = len(D)
    D = D.dropna(subset=["price_num", cfg.PRIMARY_OUTCOME, cfg.SECONDARY_OUTCOME, "number_of_reviews_ltm"])
    log.info("Amostra analítica: %d de %d imóveis (removidos %d sem preço/receita)", len(D), n0, n0 - len(D))
    D = D.reset_index(drop=True)
    D["log_v"] = np.log1p(D["v"])
    D["log_ltm"] = np.log1p(D["number_of_reviews_ltm"])
    D["log_price"] = np.log1p(D["price_num"])
    for o in (cfg.PRIMARY_OUTCOME, cfg.SECONDARY_OUTCOME):
        D["y_" + o] = np.log1p(D[o]) if o in cfg.LOG_OUTCOMES else D[o].astype(float)
    nb = D["neighbourhood_cleansed"].where(
        D["neighbourhood_cleansed"].map(D["neighbourhood_cleansed"].value_counts()) >= cfg.RARE_NEIGHBOURHOOD_MIN, "OUTROS")
    dum = pd.get_dummies(nb, prefix="bairro", drop_first=True, dtype=float)
    dum = dum.join(pd.get_dummies(D["room_type"], prefix="tipo", drop_first=True, dtype=float))
    D = pd.concat([D, dum], axis=1)
    return D, ["log_v", "log_ltm", "log_price", *dum.columns]


def _cv(X: np.ndarray, y: np.ndarray, cfg) -> pd.DataFrame:
    """R² e RMSE out-of-sample em k-fold repetido (seed fixa; mesmos folds para todos os modelos)."""
    rkf = RepeatedKFold(n_splits=cfg.K_FOLDS, n_repeats=cfg.CV_REPEATS, random_state=cfg.SEED)
    out = []
    for tr, te in rkf.split(X):
        m = LinearRegression().fit(X[tr], y[tr])
        p = m.predict(X[te])
        out.append((r2_score(y[te], p), float(np.sqrt(np.mean((y[te] - p) ** 2)))))
    return pd.DataFrame(out, columns=["r2", "rmse"])


def run_analise_a(cfg, store: Store, rating_table: str = "rating_sintetico", persist: bool = True):
    """persist=False (sensibilidade): só devolve as tabelas, sem gravar nem sobrescrever os resultados principais."""
    with stage("Etapa 8 — Análise A (poder explicativo do desempenho)"):
        D, ctrl = build_frame(cfg, store, rating_table)
        res, diffs, coefs = [], [], []
        scopes = [("amostra completa", np.ones(len(D), bool))] + [
            (f"teto: R_off >= {t}", (D["R_off"] >= t).to_numpy()) for t in cfg.CEIL_THRESHOLDS]
        specs = {"M0 controles": [], "M1 R_off": ["R_off"], "M2 R_syn": ["R_syn_raw"], "M3 R_off + R_syn": ["R_off", "R_syn_raw"]}
        for outcome in (cfg.PRIMARY_OUTCOME, cfg.SECONDARY_OUTCOME):
            ycol = "y_" + outcome
            for scope, mask in scopes:
                d = D[mask]
                if len(d) < 200:
                    log.warning("escopo %s com n=%d: pulado", scope, len(d))
                    continue
                folds = {}
                for name, preds in specs.items():
                    X = d[ctrl + preds].to_numpy(float)
                    folds[name] = _cv(X, d[ycol].to_numpy(float), cfg)
                    res.append({"desfecho": outcome, "escopo": scope, "n": len(d), "modelo": name,
                                "r2_oos_medio": folds[name]["r2"].mean(), "r2_oos_dp": folds[name]["r2"].std(),
                                "rmse_oos_medio": folds[name]["rmse"].mean(), "rmse_oos_dp": folds[name]["rmse"].std()})
                for a, b in [("M2 R_syn", "M1 R_off"), ("M3 R_off + R_syn", "M1 R_off"), ("M3 R_off + R_syn", "M2 R_syn"),
                             ("M1 R_off", "M0 controles")]:
                    dr = folds[a]["r2"] - folds[b]["r2"]
                    diffs.append({"desfecho": outcome, "escopo": scope, "n": len(d), "comparacao": f"{a} − {b}",
                                  "delta_r2_medio": dr.mean(), "delta_r2_dp": dr.std(),
                                  "prop_folds_positivos": float((dr > 0).mean()),
                                  "p2.5": dr.quantile(.025), "p97.5": dr.quantile(.975)})
                # coeficientes in-sample do M3 (preditores padronizados), erro-padrão robusto HC3
                import statsmodels.api as sm
                preds = [p for p in ("R_off", "R_syn_raw") if d[p].std() > 0]
                if preds:
                    Z = d[ctrl].copy()
                    for p in preds:
                        Z[p] = (d[p] - d[p].mean()) / d[p].std()
                    fit = sm.OLS(d[ycol].to_numpy(float), sm.add_constant(Z.to_numpy(float))).fit(cov_type="HC3")
                    names = ["const", *Z.columns]
                    for p in preds:
                        i = names.index(p)
                        coefs.append({"desfecho": outcome, "escopo": scope, "n": len(d), "termo": p + " (z)",
                                      "coef": fit.params[i], "ep_HC3": fit.bse[i], "p": fit.pvalues[i],
                                      "r2_insample_M3": fit.rsquared})
        R, Dd, C = pd.DataFrame(res), pd.DataFrame(diffs), pd.DataFrame(coefs)
        if not persist:
            return R, Dd, C
        store.save("analise_a_modelos", R)
        store.save("analise_a_diferencas", Dd)
        store.save("analise_a_coefs", C)
        log.info("R² out-of-sample:\n%s", R.round(4).to_string(index=False))
        log.info("Ganho de R² (pareado por fold):\n%s", Dd.round(4).to_string(index=False))
        main = Dd[(Dd["desfecho"] == cfg.PRIMARY_OUTCOME) & (Dd["comparacao"] == "M3 R_off + R_syn − M1 R_off")]
        store.metric("etapa8", delta_r2_M3_menos_M1_por_escopo=dict(zip(main["escopo"], main["delta_r2_medio"].round(4))),
                     n_amostra=len(D))


def run_analise_b(cfg, store: Store, rating_table: str = "rating_sintetico", persist: bool = True):
    with stage("Etapa 9 — Análise B (monotonicidade e reordenamento)"):
        D, ctrl = build_frame(cfg, store, rating_table)
        y = D["y_" + cfg.PRIMARY_OUTCOME].to_numpy(float)
        # desempenho residualizado nos controles (volume/bairro dominam o desfecho bruto)
        resid = y - LinearRegression().fit(D[ctrl].to_numpy(float), y).predict(D[ctrl].to_numpy(float))
        D["y_res"], D["y_raw"] = resid, y

        # --- correlação de posto por faixa de R_off ---
        edges = list(cfg.R_OFF_BANDS)
        labels = [f"[{a:g}, {b:g})" for a, b in zip(edges[:-2], edges[1:-1])] + ["= 5,0"]
        D["faixa"] = pd.cut(D["R_off"], bins=edges, labels=labels, right=False)
        pr_off, pr_syn = stats.rankdata(D["R_off"]) / len(D), stats.rankdata(D["R_syn_raw"]) / len(D)
        D["shift_pp"] = 100 * (pr_syn - pr_off)
        rows = []
        for lab, d in [("TODAS", D)] + [(l, g) for l, g in D.groupby("faixa", observed=True)]:
            row = {"faixa_R_off": lab, "n": len(d), "dp_R_off": d["R_off"].std(), "dp_R_syn": d["R_syn_raw"].std(),
                   "spearman_Rsyn_vs_desempenho_residual": stats.spearmanr(d["R_syn_raw"], d["y_res"])[0] if len(d) > 10 else np.nan,
                   "spearman_Rsyn_vs_desempenho_bruto": stats.spearmanr(d["R_syn_raw"], d["y_raw"])[0] if len(d) > 10 else np.nan,
                   "spearman_Roff_vs_desempenho_residual": stats.spearmanr(d["R_off"], d["y_res"])[0] if d["R_off"].nunique() > 1 else np.nan,
                   "spearman_Rsyn_vs_Roff": stats.spearmanr(d["R_syn_raw"], d["R_off"])[0] if d["R_off"].nunique() > 1 else np.nan,
                   "shift_abs_medio_pp": d["shift_pp"].abs().mean(),
                   "prop_mudanca_relevante": float((d["shift_pp"].abs() >= cfg.RANK_SHIFT_PCT).mean()),
                   "prop_sobe": float((d["shift_pp"] >= cfg.RANK_SHIFT_PCT).mean()),
                   "prop_desce": float((d["shift_pp"] <= -cfg.RANK_SHIFT_PCT).mean())}
            rows.append(row)
        B = pd.DataFrame(rows)
        if persist:
            store.save("analise_b_faixas", B)
        log.info("Correlação de posto e reordenamento por faixa de R_off:\n%s", B.round(3).to_string(index=False))

        # --- regressão isotônica (monotônica crescente) com validação out-of-sample ---
        iso_rows = []
        scopes = [("amostra completa", np.ones(len(D), bool))] + [(f"teto: R_off >= {t}", (D["R_off"] >= t).to_numpy())
                                                                   for t in cfg.CEIL_THRESHOLDS]
        for scope, mask in scopes:
            d = D[mask].reset_index(drop=True)
            if len(d) < 200:
                continue
            for pred in ("R_off", "R_syn_raw"):
                x, yy = d[pred].to_numpy(float), d["y_res"].to_numpy(float)
                r2s = []
                for tr, te in RepeatedKFold(n_splits=cfg.K_FOLDS, n_repeats=cfg.CV_REPEATS, random_state=cfg.SEED).split(x):
                    iso = IsotonicRegression(increasing=True, out_of_bounds="clip").fit(x[tr], yy[tr])
                    r2s.append(r2_score(yy[te], iso.predict(x[te])))
                full = IsotonicRegression(increasing=True, out_of_bounds="clip").fit(x, yy)
                iso_rows.append({"escopo": scope, "n": len(d), "preditor": pred, "r2_oos_isotonica_medio": np.mean(r2s),
                                 "r2_oos_isotonica_dp": np.std(r2s), "n_degraus_ajustados": len(np.unique(full.predict(x))),
                                 "spearman_preditor_vs_desempenho_residual":
                                     stats.spearmanr(x, yy)[0] if np.unique(x).size > 1 else np.nan})
        I = pd.DataFrame(iso_rows)
        if not persist:
            return B, I
        store.save("analise_b_isotonica", I)
        log.info("Regressão isotônica (desempenho residualizado):\n%s", I.round(4).to_string(index=False))
        top = B[B["faixa_R_off"] == "= 5,0"]
        store.metric("etapa9", prop_mudanca_relevante_global=round(float(B.iloc[0]["prop_mudanca_relevante"]), 3),
                     spearman_Rsyn_desempenho_na_faixa_5=(round(float(top.iloc[0]["spearman_Rsyn_vs_desempenho_residual"]), 3)
                                                          if len(top) else None))
