"""Etapa 15 — Importância de aspectos e tópicos para a nota (pergunta de pesquisa 2).

Mede ASSOCIAÇÃO (não causa) entre o que os hóspedes escrevem e a nota/subnotas oficiais, no nível do anúncio:
  A. Aspectos: decomposição LMG/Shapley do R² (cada aspecto = sentimento médio, imputado quando há < MIN_SENT_PER_ASPECT
     sentenças, o que permite incluir anúncios com pouco texto), betas padronizados (HC3), floresta/GBM com importância
     por permutação fora da amostra, e regressão logística para "nota >= 4,9".
  B. Tópicos finos: prevalência × impacto de queixas (frases negativas) e de elogios (positivas) sobre o percentil da nota,
     controlando volume e nº de sentenças; q-valores de Benjamini-Hochberg; usa só tópicos DIRETOS (acerto de aspecto ~65%
     contra ~38% nas reatribuídas, validação manual).
  C. Segmentos: tipo de acomodação, idioma predominante e principais bairros.
  D. Sensibilidades: tópicos diretos, v <= 30, >= 3 aspectos, sem 'satisfacao_geral' como preditor.
A nota é comprimida no teto; por isso o alvo é o PERCENTIL (posto) da nota e há um modelo logístico para "nota alta".
"""
from __future__ import annotations

import logging
from math import factorial

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.model_selection import KFold, cross_val_predict

from config import GENERAL_BUCKET
from .utils import Store, stage

log = logging.getLogger("pipeline")
TOP_RATING = 4.9  # "nota alta" para o modelo logístico


# ------------------------------------------------------------------ dados
def tabela_anuncio_aspecto(cfg, store: Store, direct_only: bool = False) -> pd.DataFrame:
    """Uma linha por anúncio: s_<aspecto> (sentimento médio, NaN se < MIN_SENT_PER_ASPECT), m_<aspecto> (participação nas
    sentenças do anúncio), mais volume e características."""
    A = store.load("sentencas_aspecto")
    tot = A.groupby("listing_id").size().rename("n_used")
    S = A[A["aspecto"] != GENERAL_BUCKET]
    if direct_only:
        S = S[S["topic_direto"]]
    asp = list(cfg.ASPECT_SEEDS)
    g = S.groupby(["listing_id", "aspecto"])["stars"].agg(["mean", "count"]).reset_index()
    m = g.pivot(index="listing_id", columns="aspecto", values="mean").reindex(columns=asp)
    c = g.pivot(index="listing_id", columns="aspecto", values="count").reindex(columns=asp).fillna(0)
    m = m.where(c >= cfg.MIN_SENT_PER_ASPECT)
    share = c.div(tot.reindex(c.index), axis=0)
    F = pd.concat([m.add_prefix("s_"), share.add_prefix("m_")], axis=1)
    F["n_asp"] = m.notna().sum(axis=1)
    F = F.join(tot).reset_index().rename(columns={"listing_id": "id"})
    L = store.load("listings_elig")
    F = F.merge(L, on="id")
    F["log_v"] = np.log1p(F["number_of_reviews"])
    lang = A.assign(pt=(A["lang"] == "pt")).groupby("listing_id")["pt"].mean().rename("prop_pt")
    return F.merge(lang, left_on="id", right_index=True)


def prep(F: pd.DataFrame, asp: list[str], target: str) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """X padronizado (sentimento imputado pela média), y = percentil padronizado do alvo. Retorna também o indicador de presença."""
    X = F[[f"s_{a}" for a in asp]].copy()
    present = X.notna().astype(float)
    X = X.fillna(X.mean())
    X = (X - X.mean()) / X.std()
    d = pd.concat([X, F[target]], axis=1).dropna()
    y = F.loc[d.index, target].rank(pct=True)
    y = (y - y.mean()) / y.std()
    return d[X.columns].to_numpy(), y.to_numpy(), present.loc[d.index]


def lmg(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
    """Decomposição LMG (média de Shapley do R² sobre todas as ordens). Retorna (contribuição de cada preditor, R² total)."""
    p = X.shape[1]
    R = np.corrcoef(np.column_stack([X, y]), rowvar=False)
    Rxx, rxy = R[:p, :p], R[:p, p]
    r2 = np.zeros(1 << p)
    for mask in range(1, 1 << p):
        idx = [i for i in range(p) if mask >> i & 1]
        r = rxy[idx]
        r2[mask] = r @ np.linalg.solve(Rxx[np.ix_(idx, idx)] + 1e-9 * np.eye(len(idx)), r)
    w = [factorial(k) * factorial(p - k - 1) / factorial(p) for k in range(p)]
    out = np.zeros(p)
    for j in range(p):
        for mask in range(1 << p):
            if not mask >> j & 1:
                out[j] += w[bin(mask).count("1")] * (r2[mask | (1 << j)] - r2[mask])
    return out, float(r2[-1])


# ------------------------------------------------------------------ A. aspectos
def importancia_aspectos(cfg, store: Store, F: pd.DataFrame) -> dict[str, pd.DataFrame]:
    asp = list(cfg.ASPECT_SEEDS)
    targets = {"nota_global": "review_scores_rating", **{a: s for a, s in cfg.ASPECT_TO_SUBSCORE.items() if s != "review_scores_rating"}}
    rows = []
    for nome, col in targets.items():
        X, y, _ = prep(F, asp, col)
        c, r2 = lmg(X, y)
        for a, v in zip(asp, c):
            rows.append({"alvo": f"{nome} ({col})", "aspecto": a, "contribuicao_R2": v, "parcela_do_R2": v / r2 if r2 > 0 else np.nan,
                         "R2_total": r2, "n": len(y)})
    LMG = pd.DataFrame(rows)

    # betas padronizados (nota global), HC3, com indicadores de presença e volume
    X, y, present = prep(F, asp, "review_scores_rating")
    d = F.loc[present.index]
    Z = pd.DataFrame(X, columns=[f"s_{a}" for a in asp], index=present.index)
    Z = pd.concat([Z, present.add_prefix("tem_"), d[["log_v"]]], axis=1)
    f = sm.OLS(y, sm.add_constant(Z.astype(float))).fit(cov_type="HC3")
    ci = f.conf_int()
    B = pd.DataFrame({"termo": f.params.index, "beta_padronizado": f.params.values, "ep_HC3": f.bse.values, "p": f.pvalues.values,
                      "ic_inf": ci[0].values, "ic_sup": ci[1].values})
    B["R2_insample"] = f.rsquared

    # GBM com NaN nativo + permutação por aspecto (fora da amostra), contra OLS imputado
    feats = [f"s_{a}" for a in asp] + [f"m_{a}" for a in asp] + ["log_v"]
    Dg = F[feats + ["review_scores_rating"]].dropna(subset=["review_scores_rating"]).reset_index(drop=True)
    yg = Dg["review_scores_rating"].rank(pct=True).to_numpy()
    rng = np.random.default_rng(cfg.SEED)
    gb_r2, ols_r2, perm = [], [], {a: [] for a in asp}
    for tr, te in KFold(cfg.K_FOLDS, shuffle=True, random_state=cfg.SEED).split(Dg):
        gb = HistGradientBoostingRegressor(max_depth=4, max_iter=200, learning_rate=0.05, random_state=cfg.SEED).fit(Dg.loc[tr, feats], yg[tr])
        base = r2_score(yg[te], gb.predict(Dg.loc[te, feats]))
        gb_r2.append(base)
        Xi = Dg[[f"s_{a}" for a in asp] + ["log_v"]].copy()
        Xi = pd.concat([Xi.fillna(Xi.mean()), Dg[[f"s_{a}" for a in asp]].notna().astype(float).add_prefix("tem_")], axis=1)
        ols_r2.append(r2_score(yg[te], LinearRegression().fit(Xi.iloc[tr], yg[tr]).predict(Xi.iloc[te])))
        for a in asp:
            T = Dg.loc[te, feats].copy()
            idx = rng.permutation(len(T))
            for c in (f"s_{a}", f"m_{a}"):
                T[c] = T[c].to_numpy()[idx]
            perm[a].append(base - r2_score(yg[te], gb.predict(T)))
    G = pd.DataFrame({"aspecto": asp, "queda_R2_oos_por_permutacao": [np.mean(perm[a]) for a in asp],
                      "dp_entre_dobras": [np.std(perm[a]) for a in asp]})
    G["R2_oos_GBM"], G["R2_oos_OLS_imputado"] = np.mean(gb_r2), np.mean(ols_r2)

    # logística: nota alta (>= TOP_RATING)
    X, _, present = prep(F, asp, "review_scores_rating")
    d = F.loc[present.index]
    yb = (d["review_scores_rating"] >= TOP_RATING).astype(int).to_numpy()
    Xl = pd.DataFrame(X, columns=[f"s_{a}" for a in asp], index=present.index)
    Xl["log_v"] = ((d["log_v"] - d["log_v"].mean()) / d["log_v"].std()).to_numpy()
    p_oos = cross_val_predict(LogisticRegression(max_iter=1000), Xl, yb, cv=KFold(cfg.K_FOLDS, shuffle=True, random_state=cfg.SEED),
                              method="predict_proba")[:, 1]
    lo = sm.Logit(yb, sm.add_constant(Xl.astype(float))).fit(disp=0, cov_type="HC3")
    ci = lo.conf_int()
    Lg = pd.DataFrame({"termo": lo.params.index, "odds_ratio_por_DP": np.exp(lo.params.values), "or_ic_inf": np.exp(ci[0].values),
                       "or_ic_sup": np.exp(ci[1].values), "p": lo.pvalues.values})
    Lg["AUC_oos"], Lg["prop_nota_alta"], Lg["n"] = roc_auc_score(yb, p_oos), yb.mean(), len(yb)
    return {"imp_lmg": LMG, "imp_betas": B, "imp_gbm": G, "imp_logit": Lg}


# ------------------------------------------------------------------ B. tópicos
def importancia_topicos(cfg, store: Store, F: pd.DataFrame) -> dict[str, pd.DataFrame]:
    A = store.load("sentencas_aspecto")
    A = A[A["topic_direto"] & (A["topic"] >= 0)]
    Sn = store.load("sentiment")[["text_id", "p_neg", "p_neu", "p_pos"]]
    A = A.merge(Sn, on="text_id")
    cls = np.array(["neg", "neu", "pos"])[A[["p_neg", "p_neu", "p_pos"]].to_numpy().argmax(1)]
    A["cls"] = cls
    T = store.load("topics_bertopic")[["topic", "top_words"]]
    asp_of = A.drop_duplicates("topic").set_index("topic")["aspecto"]
    F = F.set_index("id")
    y = F["review_scores_rating"].rank(pct=True)
    ctrl = sm.add_constant(pd.DataFrame({"log_v": F["log_v"], "log_used": np.log1p(F["n_used"])}))
    rows = []
    for kind, label in (("neg", "queixa"), ("pos", "elogio")):
        cnt = A[A["cls"] == kind].groupby(["listing_id", "topic"]).size().unstack(fill_value=0).reindex(F.index, fill_value=0)
        for t in cnt.columns:
            x = (cnt[t] > 0).astype(float)
            n1 = int(x.sum())
            if n1 < 100 or n1 > len(x) - 100:
                continue
            fit = sm.OLS(y.to_numpy(), pd.concat([x.rename("x"), ctrl], axis=1).to_numpy(float), missing="drop").fit(cov_type="HC3")
            rows.append({"tipo": label, "topic": int(t), "aspecto": asp_of.get(t), "n_anuncios_com_mencao": n1,
                         "prevalencia": n1 / len(x), "efeito_pontos_percentil_nota": 100 * fit.params[0],
                         "ep": 100 * fit.bse[0], "p": fit.pvalues[0]})
    R = pd.DataFrame(rows).merge(T, on="topic", how="left")
    for k in R["tipo"].unique():
        m = R["tipo"] == k
        p = R.loc[m, "p"].to_numpy()
        o = np.argsort(p)
        q = np.empty_like(p)
        q[o] = np.minimum.accumulate((p[o] * len(p) / (np.arange(len(p)) + 1))[::-1])[::-1]  # Benjamini-Hochberg
        R.loc[m, "q_BH"] = np.minimum(q, 1)
    R["impacto_x_prevalencia"] = R["efeito_pontos_percentil_nota"] * R["prevalencia"]
    # exemplos de frases negativas/positivas por tópico (amostra com seed)
    Tx = store.load("texts")[["text_id", "text"]].set_index("text_id")["text"]
    rng = np.random.default_rng(cfg.SEED)
    ex = {}
    for (kind, t), g in A.groupby(["cls", "topic"]):
        if kind in ("neg", "pos"):
            ex[(kind, t)] = " || ".join(Tx.loc[g["text_id"].sample(min(3, len(g)), random_state=int(rng.integers(1e9)))].str.slice(0, 160))
    R["exemplos"] = [ex.get(("neg" if k == "queixa" else "pos", t)) for k, t in zip(R["tipo"], R["topic"])]
    Q = R[R["tipo"] == "queixa"].sort_values("impacto_x_prevalencia")
    E = R[R["tipo"] == "elogio"].sort_values("impacto_x_prevalencia", ascending=False)
    return {"imp_topicos_queixas": Q, "imp_topicos_elogios": E}


# ------------------------------------------------------------------ C. segmentos e D. sensibilidades
def _lmg_nota(cfg, F: pd.DataFrame, asp: list[str]) -> tuple[np.ndarray, float, int]:
    X, y, _ = prep(F, asp, "review_scores_rating")
    c, r2 = lmg(X, y)
    return c, r2, len(y)


def segmentos_e_sensibilidade(cfg, store: Store, F: pd.DataFrame, Fd: pd.DataFrame) -> dict[str, pd.DataFrame]:
    asp = list(cfg.ASPECT_SEEDS)
    top_b = F["neighbourhood_cleansed"].value_counts().head(6).index
    segs = {"todos": F, "casa/apto inteiro": F[F["room_type"] == "Entire home/apt"], "quarto privado": F[F["room_type"] == "Private room"],
            "idioma predominante pt": F[F["prop_pt"] >= 0.5], "idioma predominante não-pt": F[F["prop_pt"] < 0.5],
            **{f"bairro: {b}": F[F["neighbourhood_cleansed"] == b] for b in top_b}}
    rows = []
    for nome, d in segs.items():
        if len(d) < 300:
            continue
        c, r2, n = _lmg_nota(cfg, d, asp)
        rows += [{"segmento": nome, "aspecto": a, "parcela_do_R2": v / r2 if r2 > 0 else np.nan, "R2_total": r2, "n": n} for a, v in zip(asp, c)]
    seg = pd.DataFrame(rows)
    sens_def = {"base (todos os anúncios, imputação)": (F, asp), "só tópicos diretos": (Fd, asp), "v <= 30": (F[F["number_of_reviews"] <= 30], asp),
                ">= 3 aspectos com evidência": (F[F["n_asp"] >= 3], asp),
                "sem satisfacao_geral como preditor": (F, [a for a in asp if a != "satisfacao_geral"])}
    rows = []
    for nome, (d, aa) in sens_def.items():
        c, r2, n = _lmg_nota(cfg, d, aa)
        rows += [{"variante": nome, "aspecto": a, "parcela_do_R2": v / r2 if r2 > 0 else np.nan, "R2_total": r2, "n": n} for a, v in zip(aa, c)]
    return {"imp_segmentos": seg, "imp_sensibilidade": pd.DataFrame(rows)}


def run(cfg, store: Store) -> None:
    with stage("Etapa 15 — Importância de aspectos e tópicos"):
        F = tabela_anuncio_aspecto(cfg, store)
        Fd = tabela_anuncio_aspecto(cfg, store, direct_only=True)
        log.info("Anúncios na análise de importância: %d (com >= 3 aspectos: %d)", len(F), int((F["n_asp"] >= 3).sum()))
        out = importancia_aspectos(cfg, store, F)
        out |= importancia_topicos(cfg, store, F)
        out |= segmentos_e_sensibilidade(cfg, store, F, Fd)
        for k, v in out.items():
            store.save(k, v)
        L = out["imp_lmg"]
        log.info("Parcela do R² (LMG) por aspecto e alvo:\n%s", L.pivot_table(index="aspecto", columns="alvo", values="parcela_do_R2").round(3).to_string())
        log.info("R² total por alvo:\n%s", L.drop_duplicates("alvo").set_index("alvo")[["R2_total", "n"]].round(3).to_string())
        log.info("GBM/permutação:\n%s", out["imp_gbm"].round(4).to_string(index=False))
        log.info("Logística (nota >= %.1f):\n%s", TOP_RATING, out["imp_logit"].round(3).to_string(index=False))
        log.info("Top queixas (impacto × prevalência):\n%s", out["imp_topicos_queixas"].head(15)[
            ["topic", "aspecto", "top_words", "prevalencia", "efeito_pontos_percentil_nota", "q_BH"]].round(3).to_string(index=False))
        log.info("Top elogios:\n%s", out["imp_topicos_elogios"].head(10)[
            ["topic", "aspecto", "top_words", "prevalencia", "efeito_pontos_percentil_nota", "q_BH"]].round(3).to_string(index=False))
        store.metric("etapa15", n_anuncios=len(F), r2_nota_global=round(float(L[L["alvo"].str.startswith("nota_global")]["R2_total"].iloc[0]), 3))
