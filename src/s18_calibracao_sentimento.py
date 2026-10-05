"""Etapa 18 (EXPLORATÓRIA, não altera nenhuma análise principal) — quanto uma recalibração do sentimento com os rótulos manuais melhoraria o estudo?

O modelo erra de forma conservadora (frases positivas viram "neutro"). Aqui se ajusta, com os 297 rótulos do pesquisador, uma regressão logística multinomial sobre
log(P(neg)/P(neu)), log(P(pos)/P(neu)) e um indicador de português, que reponderam as três probabilidades. Dois resultados:
  1. Validação cruzada (5 dobras × 20 repetições) do sentimento de 3 classes, com pesos que corrigem a amostragem estratificada (aspecto × polaridade prevista),
     comparando o modelo original (argmax) com o recalibrado.
  2. Efeito nas correlações aspecto × subnota (validade de construto): estrelas recalibradas = 1·P'(neg) + 3·P'(neu) + 5·P'(pos), reagregadas por anúncio e aspecto.
Cuidados: 297 rótulos de um avaliador; a amostra é estratificada (os pesos usam a população de cada estrato); a recalibração é ajustada nessa amostra e depois aplicada a todo o corpus.
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import cohen_kappa_score, f1_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.preprocessing import StandardScaler

from config import GENERAL_BUCKET
from .utils import Store, stage

log = logging.getLogger("pipeline")
CLASSES = ["negativo", "neutro", "positivo"]


def _feat(p: pd.DataFrame, pt: np.ndarray) -> np.ndarray:
    e = 1e-6
    return np.column_stack([np.log((p["p_neg"] + e) / (p["p_neu"] + e)), np.log((p["p_pos"] + e) / (p["p_neu"] + e)), pt.astype(float)])


def _rotulos(cfg, store: Store) -> tuple[pd.DataFrame, np.ndarray]:
    path = Path(cfg.MANUAL_VALIDATION_XLSX)
    H = pd.read_excel(path, sheet_name="Amostra").merge(pd.read_excel(path, sheet_name="Gabarito_modelo"), on="id_amostra")
    H = H[H["sentimento_humano"].notna()].reset_index(drop=True)
    # pesos: população de cada estrato (aspecto previsto × polaridade) / frases rotuladas no estrato
    S = store.load("sentencas_aspecto")
    T = store.load("texts")[["text_id", "n_tok"]]
    S = S.merge(T, on="text_id")
    S = S[S["n_tok"] >= cfg.MIN_SENT_TOKENS].drop_duplicates("text_id")
    pol = lambda s: pd.cut(s, [0, 2.5, 3.5, 5.01], labels=["neg", "neu", "pos"])
    pop = S.assign(pol=pol(S["stars"])).groupby(["aspecto", "pol"], observed=True).size().rename("N")
    H["pol"] = pol(H["estrelas_modelo"])
    n = H.groupby(["aspecto_modelo", "pol"], observed=True).size().rename("n")
    w = H.join(pop, on=["aspecto_modelo", "pol"]).join(n, on=["aspecto_modelo", "pol"])
    wt = (w["N"] / w["n"]).fillna(1.0).to_numpy()
    return H, wt / wt.mean()


def validacao_cruzada(H: pd.DataFrame, wt: np.ndarray, seed: int) -> pd.DataFrame:
    y = H["sentimento_humano"].map({c: i for i, c in enumerate(CLASSES)}).to_numpy()
    P = H[["p_neg", "p_neu", "p_pos"]]
    X = _feat(H.rename(columns={}), (H["idioma"] == "pt").to_numpy())
    base = P.to_numpy().argmax(1)
    rows = []
    for tr, te in RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=seed).split(X, y):
        sc = StandardScaler().fit(X[tr])
        m = LogisticRegression(max_iter=1000).fit(sc.transform(X[tr]), y[tr], sample_weight=wt[tr])
        pred = m.predict(sc.transform(X[te]))
        for nome, p in (("original (argmax)", base[te]), ("recalibrado", pred)):
            rows.append({"modelo": nome, "acuracia_pond": float(np.average(p == y[te], weights=wt[te])),
                         "kappa_pond": float(cohen_kappa_score(y[te], p, sample_weight=wt[te])),
                         "kappa_linear_pond": float(cohen_kappa_score(y[te], p, weights="linear", sample_weight=wt[te])),
                         "f1_macro_pond": float(f1_score(y[te], p, average="macro", sample_weight=wt[te]))})
    return pd.DataFrame(rows).groupby("modelo").agg(["mean", "std"]).round(4)


def run(cfg, store: Store) -> None:
    with stage("Etapa 18 (exploratória) — recalibração do sentimento com os rótulos manuais"):
        H, wt = _rotulos(cfg, store)
        log.info("Rótulos: %d frases; pesos de estratificação: min %.2f, máx %.2f", len(H), wt.min(), wt.max())
        cv = validacao_cruzada(H, wt, cfg.SEED)
        log.info("Validação cruzada (pesos pela população):\n%s", cv.to_string())
        cvf = cv.copy()
        cvf.columns = ["_".join(c) for c in cvf.columns]
        store.save("calib_cv", cvf.reset_index())

        # ajuste final e aplicação a todas as sentenças
        y = H["sentimento_humano"].map({c: i for i, c in enumerate(CLASSES)}).to_numpy()
        X = _feat(H, (H["idioma"] == "pt").to_numpy())
        sc = StandardScaler().fit(X)
        m = LogisticRegression(max_iter=1000).fit(sc.transform(X), y, sample_weight=wt)
        log.info("Coeficientes (padronizados) por classe [neg, neu, pos] × [log neg/neu, log pos/neu, português]:\n%s", np.round(m.coef_, 3))

        S = store.load("sentencas_aspecto")
        S = S[S["aspecto"] != GENERAL_BUCKET]
        Sn = store.load("sentiment")[["text_id", "p_neg", "p_neu", "p_pos"]]
        S = S.merge(Sn, on="text_id")
        Pc = m.predict_proba(sc.transform(_feat(S, (S["lang"] == "pt").to_numpy())))
        S["stars_cal"] = Pc @ np.array([1.0, 3.0, 5.0])
        log.info("Estrelas médias das sentenças: original %.3f; recalibrado %.3f", S["stars"].mean(), S["stars_cal"].mean())

        L = store.load("listings_elig").set_index("id")
        rows = []
        for a, sub in cfg.ASPECT_TO_SUBSCORE.items():
            g = S[S["aspecto"] == a].groupby("listing_id").agg(n=("stars", "size"), o=("stars", "mean"), c=("stars_cal", "mean"))
            g = g[g["n"] >= cfg.MIN_SENT_PER_ASPECT].join(L[sub].rename("sub")).dropna()
            ro, rc = stats.spearmanr(g["o"], g["sub"])[0], stats.spearmanr(g["c"], g["sub"])[0]
            rows.append({"aspecto": a, "subnota": sub, "n": len(g), "spearman_original": ro, "spearman_recalibrado": rc, "diferenca": rc - ro})
        R = pd.DataFrame(rows)
        store.save("calib_correlacoes", R)
        log.info("Correlação aspecto × subnota, original vs recalibrado:\n%s", R.round(3).to_string(index=False))
        store.metric("etapa18", media_diferenca_spearman=round(float(R["diferenca"].mean()), 4))
