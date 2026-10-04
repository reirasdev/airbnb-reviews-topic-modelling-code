"""Análises complementares (fora das 9 etapas da spec), pedidas após os resultados principais:

  1. Descritivo do teto: compressão/empates de R_off vs R_syn e quanto R_syn discrimina dentro de R_off = 5,0.
     É a metade descritiva da tese ("a nota oficial comprime no teto"), independente do desempenho.
  2. Seleção: quem fica de fora de R_syn (poucos aspectos com evidência textual) e da Análise A (sem preço).
Saídas: tabelas `descritivo_teto` e `selecao` (abas Descritivo_Teto e Selecao do Excel).
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from scipy import stats

from .utils import Store, stage

log = logging.getLogger("pipeline")


def _compressao(x: pd.Series, nome: str, variante: str) -> dict:
    r = x.round(2)  # a nota oficial vem com 2 casas; mesma resolução para todos
    vc = r.value_counts()
    p = vc / vc.sum()
    pct = x.rank(pct=True)
    return {"variante": variante, "medida": nome, "n": len(x), "media": x.mean(), "dp": x.std(),
            "p5": x.quantile(.05), "p25": x.quantile(.25), "mediana": x.median(), "p75": x.quantile(.75), "p95": x.quantile(.95),
            "valores_distintos(2 casas)": int(vc.size),
            "prop_no_valor_mais_comum": float(p.iloc[0]),
            "prop_em_empate_exato": float((r.map(vc) > 1).mean()),
            "entropia_normalizada": float(-(p * np.log(p)).sum() / np.log(len(x))),
            "coef_variacao": x.std() / x.mean(),
            "amplitude_p5_p95": x.quantile(.95) - x.quantile(.05),
            "prop_em_algum_empate_de_posto": float((pct.map(pct.value_counts()) > 1).mean())}


def descritivo_teto(cfg, store: Store) -> pd.DataFrame:
    L = store.load("listings_elig")
    prof = store.load("perfil_absa")[["id"] + list(cfg.ASPECT_SEEDS)]
    rows = []
    for var in ("sem_shrinkage", "com_shrinkage"):
        R = store.load(f"rating_sintetico__{var}")
        rows += [_compressao(R["R_off"], "R_off (nota oficial)", var),
                 _compressao(R["R_syn_raw"], "R_syn_raw", var)]
        # dentro de R_off = 5,0: R_syn espalha os imóveis? (percentil de R_syn na amostra toda)
        top = R[R["R_off"] == 5.0].copy()
        pr = R["R_syn_raw"].rank(pct=True).loc[top.index]
        q = pr.quantile([.1, .25, .5, .75, .9])
        row = {"variante": var, "medida": "Dentro de R_off = 5,0: percentil de R_syn", "n": len(top),
               "media": pr.mean(), "dp": pr.std(), "p5": pr.quantile(.05), "p25": q[.25], "mediana": q[.5],
               "p75": q[.75], "p95": pr.quantile(.95),
               "valores_distintos(2 casas)": int(top["R_syn_raw"].round(2).nunique()),
               "prop_no_valor_mais_comum": float(top["R_syn_raw"].round(2).value_counts(normalize=True).iloc[0])}
        rows.append(row)
        # concordância de R_syn com cada subnota DENTRO de R_off = 5,0 (subnotas também saturadas -> reportar variação)
        D = top.merge(L, on="id")
        for a, sub in cfg.ASPECT_TO_SUBSCORE.items():
            if sub == "review_scores_rating":
                continue
            d = D[["R_syn_raw", sub]].dropna()
            ok = d[sub].nunique() > 1
            rows.append({"variante": var, "medida": f"Dentro de R_off = 5,0: spearman R_syn × {sub}", "n": len(d),
                         "media": stats.spearmanr(d["R_syn_raw"], d[sub])[0] if ok else np.nan,
                         "prop_no_valor_mais_comum": float((d[sub] == 5).mean()),
                         "valores_distintos(2 casas)": int(d[sub].round(2).nunique())})
    T = pd.DataFrame(rows)
    T = T.rename(columns={"media": "media_ou_rho"})
    return T


def selecao(cfg, store: Store) -> pd.DataFrame:
    L = store.load("listings_elig")
    Rs = set(store.load("rating_sintetico")["id"])
    prof_ids = set(store.load("perfil_absa")["id"])
    L = L.assign(tem_perfil=L["id"].isin(prof_ids), tem_rsyn=L["id"].isin(Rs),
                 na_analise_a=L["id"].isin(Rs) & L["price_num"].notna() & L["estimated_occupancy_l365d"].notna()
                 & L["estimated_revenue_l365d"].notna() & L["number_of_reviews_ltm"].notna())
    num = ["number_of_reviews", "number_of_reviews_ltm", "reviews_per_month", "review_scores_rating",
           "estimated_occupancy_l365d", "estimated_revenue_l365d", "price_num"]
    L[num] = L[num].astype(float)  # price_num vem como Float64 anulável (pd.NA quebra comparações)
    rows = []
    for nome, inc in [("R_syn: incluídos × excluídos (entre os elegíveis)", L["tem_rsyn"]),
                      ("Análise A: incluídos × excluídos (entre os com R_syn)", L["na_analise_a"])]:
        base = L if nome.startswith("R_syn") else L[L["tem_rsyn"]]
        i = inc.loc[base.index]
        for v in num:
            a, b = base.loc[i, v].dropna(), base.loc[~i, v].dropna()
            sd = np.sqrt((a.var() + b.var()) / 2)
            rows.append({"comparacao": nome, "variavel": v, "n_incl": len(a), "n_excl": len(b),
                         "media_incl": a.mean(), "media_excl": b.mean(), "mediana_incl": a.median(), "mediana_excl": b.median(),
                         "dif_padronizada": (a.mean() - b.mean()) / sd if sd > 0 else np.nan})
        for rt in sorted(base["room_type"].unique()):
            a, b = (base.loc[i, "room_type"] == rt), (base.loc[~i, "room_type"] == rt)
            rows.append({"comparacao": nome, "variavel": f"prop room_type = {rt}", "n_incl": len(a), "n_excl": len(b),
                         "media_incl": a.mean(), "media_excl": b.mean()})
    return pd.DataFrame(rows)


def run(cfg, store: Store) -> None:
    with stage("Complementar — descritivo do teto e seleção"):
        T = descritivo_teto(cfg, store)
        store.save("descritivo_teto", T)
        log.info("Compressão e empates (R_off vs R_syn):\n%s",
                 T[T["medida"].str.startswith(("R_off", "R_syn"))].set_index(["variante", "medida"])[
                     ["n", "media_ou_rho", "dp", "valores_distintos(2 casas)", "prop_no_valor_mais_comum", "prop_em_empate_exato",
                      "entropia_normalizada", "coef_variacao"]].round(3).to_string())
        log.info("Dentro de R_off = 5,0:\n%s", T[T["medida"].str.startswith("Dentro")].set_index(["variante", "medida"])[
            ["n", "media_ou_rho", "dp", "p5", "mediana", "p95", "prop_no_valor_mais_comum"]].round(3).to_string())
        S = selecao(cfg, store)
        store.save("selecao", S)
        log.info("Seleção:\n%s", S.round(3).to_string(index=False))
        store.metric("complementar", n_linhas_descritivo=len(T), n_linhas_selecao=len(S))
