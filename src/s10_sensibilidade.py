"""Sensibilidade do rating sintético (fora das 9 etapas da spec; robustez pedida após os resultados principais).

Variantes de R_syn_raw, mesma amostra de imóveis e mesmos folds/seed:
  sem_shrinkage   = ESPECIFICAÇÃO PRINCIPAL: média dos aspectos sem encolhimento, com satisfacao_geral
  com_shrinkage   = média bayesiana (spec original)
  *_sem_satisfacao = R_syn só de aspectos específicos
  *_v30           = só imóveis com v <= 30 (sentimento usa todas as avaliações)
Resultado: tabela `sensibilidade` (aba Sensibilidade do Excel); NÃO sobrescreve os resultados principais.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from scipy import stats

from .s5_s7_rating import build_rating
from .s8_s9_analises import run_analise_a, run_analise_b
from .utils import Store, stage

log = logging.getLogger("pipeline")

VARIANTS = {
    "sem_shrinkage": ((), False),                       # ESPECIFICAÇÃO PRINCIPAL (config RSYN_SHRINK=False)
    "com_shrinkage": ((), True),                        # como na spec original (média bayesiana)
    "sem_shrinkage_sem_satisfacao": (("satisfacao_geral",), False),
    "com_shrinkage_sem_satisfacao": (("satisfacao_geral",), True),
    # imóveis com v <= MAX_REVIEWS_PER_LISTING: o sentimento usa TODAS as avaliações (sem descompasso com a nota oficial)
    "sem_shrinkage_v30": ((), False, 30),
    "com_shrinkage_v30": ((), True, 30),
}


def run(cfg, store: Store) -> None:
    with stage("Sensibilidade — variantes de R_syn"):
        rows = []
        for name, spec in VARIANTS.items():
            excl, shrink = spec[0], spec[1]
            max_v = spec[2] if len(spec) > 2 else None
            R, m, _ = build_rating(cfg, store, exclude=excl, shrink=shrink, max_v=max_v)
            tab = f"rating_sintetico__{name}"
            store.save(tab, R)
            _, Dd, _ = run_analise_a(cfg, store, tab, persist=False)
            B, I = run_analise_b(cfg, store, tab, persist=False)
            base = {"variante": name, "exclui": ",".join(excl) or "-", "shrinkage": shrink, "n_rating": len(R),
                    "spearman_Rsyn_Roff": stats.spearmanr(R["R_syn_raw"], R["R_off"])[0],
                    "spearman_Rsyn_volume": stats.spearmanr(R["R_syn_raw"], np.log1p(R["v"]))[0],
                    "dp_Rsyn": R["R_syn_raw"].std()}
            for _, r in Dd[Dd["comparacao"].isin(["M3 R_off + R_syn − M1 R_off", "M2 R_syn − M1 R_off"])].iterrows():
                rows.append({**base, "bloco": "A: delta R2 OOS", "desfecho": r["desfecho"], "escopo": r["escopo"],
                             "n": r["n"], "medida": r["comparacao"], "valor": r["delta_r2_medio"],
                             "ic_inf": r["p2.5"], "ic_sup": r["p97.5"]})
            for _, r in B.iterrows():
                for med, col in [("spearman R_syn × desempenho residual", "spearman_Rsyn_vs_desempenho_residual"),
                                 ("spearman R_syn × desempenho bruto", "spearman_Rsyn_vs_desempenho_bruto")]:
                    rows.append({**base, "bloco": "B: por faixa de R_off", "desfecho": cfg.PRIMARY_OUTCOME,
                                 "escopo": f"faixa {r['faixa_R_off']}", "n": r["n"], "medida": med, "valor": r[col]})
            for _, r in I.iterrows():
                rows.append({**base, "bloco": "B: isotônica", "desfecho": cfg.PRIMARY_OUTCOME, "escopo": r["escopo"],
                             "n": r["n"], "medida": f"R2 OOS isotônica ({r['preditor']})", "valor": r["r2_oos_isotonica_medio"]})
        S = pd.DataFrame(rows)
        store.save("sensibilidade", S)
        key = S[(S["bloco"] == "B: por faixa de R_off") & (S["escopo"] == "faixa = 5,0")]
        log.info("Faixa R_off = 5,0 — Spearman de R_syn com desempenho, por variante:\n%s",
                 key.pivot_table(index="variante", columns="medida", values="valor").round(3).to_string())
        ka = S[(S["bloco"] == "A: delta R2 OOS") & (S["medida"] == "M3 R_off + R_syn − M1 R_off")
               & (S["desfecho"] == cfg.PRIMARY_OUTCOME)]
        log.info("ΔR² OOS (M3 − M1), ocupação, por variante e escopo:\n%s",
                 ka.pivot_table(index="variante", columns="escopo", values="valor").round(5).to_string())
        log.info("Associação de R_syn com R_off e volume:\n%s",
                 S.drop_duplicates("variante").set_index("variante")[["spearman_Rsyn_Roff", "spearman_Rsyn_volume", "dp_Rsyn"]]
                 .round(3).to_string())
        store.metric("sensibilidade", variantes=list(VARIANTS))
