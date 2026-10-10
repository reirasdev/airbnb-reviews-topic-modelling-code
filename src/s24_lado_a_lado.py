"""Etapa 24 — Tabelas lado a lado A × B e análises que dependem dos DOIS modelos (itens 2.4, 2.5, 2.6 na interseção, 2.9, 2.10 e aba-resumo).

Pressupõe que as etapas 5 a 17 já rodaram para A (sem sufixo) e para B (`--sentimento B`, sufixo `__B`). Todas as saídas levam o prefixo cmp_ (compartilhadas).
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from scipy import stats

from .s8_s9_analises import run_analise_a
from .utils import Store, stage

log = logging.getLogger("pipeline")

# (tabela, colunas-chave). As colunas numéricas viram <col>__A e <col>__B; as de texto que não são chave vêm de A.
BLOCOS = [
    ("validacao_construto", ["aspecto", "subnota"]), ("val_volume", ["aspecto", "subnota", "faixa"]), ("val_convergente", ["aspecto"]),
    ("val_auc_kendall", ["aspecto"]), ("val_confiabilidade", ["aspecto"]), ("val_recortes", ["recorte", "aspecto"]),
    ("imp_lmg", ["alvo", "aspecto"]), ("imp_betas", ["termo"]), ("imp_gbm", ["aspecto"]), ("imp_logit", ["termo"]),
    ("imp_segmentos", ["segmento", "aspecto"]), ("imp_sensibilidade", ["variante", "aspecto"]),
    ("analise_a_modelos", ["desfecho", "escopo", "modelo"]), ("analise_a_diferencas", ["desfecho", "escopo", "comparacao"]), ("analise_a_coefs", ["desfecho", "escopo", "termo"]),
    ("analise_b_faixas", ["faixa_R_off"]), ("analise_b_isotonica", ["escopo", "preditor"]),
    ("sensibilidade", ["variante", "bloco", "desfecho", "escopo", "medida"]), ("descritivo_teto", ["variante", "medida"]),
    ("sazon_aspecto", ["defasagem", "evento", "aspecto", "medida"]), ("sazon_topico", ["defasagem", "evento", "topic"]), ("sazon_criterio", ["evento"]),
    ("perfil_cobertura", ["aspecto"]),
]


def lado(sA: Store, sB: Store, nome: str, keys: list[str]) -> pd.DataFrame:
    a, b = sA.load(nome), sB.load(nome)
    if a.duplicated(keys).any() or b.duplicated(keys).any():
        log.warning("%s: chave %s não é única; o lado a lado pode duplicar linhas", nome, keys)
    num = [c for c in a.columns if c not in keys and pd.api.types.is_numeric_dtype(a[c]) and c in b.columns]
    txt = [c for c in a.columns if c not in keys and c not in num]
    x = a[keys + txt + num].rename(columns={c: f"{c}__A" for c in num})
    y = b[keys + num].rename(columns={c: f"{c}__B" for c in num})
    m = x.merge(y, on=keys, how="outer")
    cols = keys + txt + [f"{c}__{t}" for c in num for t in ("A", "B")]
    return m[cols]


def _cobertura(s: Store, cfg) -> pd.DataFrame:
    P = s.load("perfil_absa")
    return pd.DataFrame({"aspecto": list(cfg.ASPECT_SEEDS), "anuncios_com_aspecto": [int(P[a].notna().sum()) for a in cfg.ASPECT_SEEDS],
                         "sentimento_medio_do_aspecto": [float(P[a].mean()) for a in cfg.ASPECT_SEEDS],
                         "sentimento_dp_entre_anuncios": [float(P[a].std()) for a in cfg.ASPECT_SEEDS]})


def _resumo_rsyn(s: Store, cfg) -> dict:
    R, L = s.load("rating_sintetico"), s.load("listings_elig")
    n = len(R)
    pr_off, pr_syn = stats.rankdata(R["R_off"]) / n, stats.rankdata(R["R_syn_raw"]) / n
    top = R[R["R_off"] == 5.0]
    pct_top = pd.Series(pr_syn, index=R.index).loc[top.index]
    D = top.merge(L, on="id")
    out = {"anuncios_com_R_syn": n, "anuncios_nota_5_com_R_syn": len(top), "prop_valor_modal_R_syn(2 casas)": float(R["R_syn_raw"].round(2).value_counts(normalize=True).iloc[0]),
           "prop_valor_modal_R_off(2 casas)": float(R["R_off"].round(2).value_counts(normalize=True).iloc[0]), "spearman_R_syn_R_off": float(stats.spearmanr(R["R_syn_raw"], R["R_off"])[0]),
           "prop_muda_>=10pp_de_posto": float((np.abs(100 * (pr_syn - pr_off)) >= cfg.RANK_SHIFT_PCT).mean()),
           "nota5_dp_do_percentil_de_R_syn": float(pct_top.std()), "nota5_percentil_p5": float(pct_top.quantile(.05)), "nota5_percentil_p50": float(pct_top.quantile(.5)),
           "nota5_percentil_p95": float(pct_top.quantile(.95))}
    for a, sub in cfg.ASPECT_TO_SUBSCORE.items():
        if sub != "review_scores_rating":
            d = D[["R_syn_raw", sub]].dropna()
            out[f"nota5_spearman_R_syn_x_{sub}"] = float(stats.spearmanr(d["R_syn_raw"], d[sub])[0])
    return out


def _resumo_ab(sA: Store, cfg) -> pd.DataFrame:
    """Aba-resumo: os resultados principais lado a lado, A × B (cada linha aponta a tabela de origem)."""
    rows = []

    def add(bloco, medida, a, b, fonte):
        rows.append({"bloco": bloco, "medida": medida, "A": a, "B": b, "fonte": fonte})

    if sA.exists("cmp_descritivas"):
        D = sA.load("cmp_descritivas").set_index("modelo")
        for c, nome in (("estrelas_media_texto", "estrelas médias (por texto único)"), ("prop_sentencas_ge_4_estrelas", "% de sentenças com >= 4 estrelas"),
                        ("prop_sentencas_negativa", "% de sentenças negativas"), ("prop_sentencas_positiva", "% de sentenças positivas")):
            add("Sentimento", nome, D.loc["A", c], D.loc["B", c], "cmp_descritivas")
    if sA.exists("cmp_manual_modelos"):
        M = sA.load("cmp_manual_modelos").set_index("modelo")
        for c, nome in (("acuracia_populacao", "acurácia populacional (frases rotuladas)"), ("kappa_linear_populacao", "kappa ponderado linear populacional"), ("acuracia_amostra", "acurácia na amostra"),
                        ("kappa_linear_amostra", "kappa ponderado linear na amostra")):
            add("Validação manual", nome, M.loc["A", c], M.loc["B", c], "cmp_manual_modelos")
    V = sA.load("cmp_ladoalado_validacao_construto")
    for r in V.itertuples():
        add("Validade de construto", f"Spearman {r.aspecto} × {r.subnota}", r.spearman__A, r.spearman__B, "validacao_construto")
    L = sA.load("cmp_ladoalado_imp_lmg")
    for r in L[L["alvo"].str.startswith("nota_global")].itertuples():
        add("Importância (LMG, nota global)", f"parcela do R² — {r.aspecto}", r.parcela_do_R2__A, r.parcela_do_R2__B, "imp_lmg")
    g = sA.load("cmp_ladoalado_imp_gbm")
    add("Importância", "R² fora da amostra do GBM", g["R2_oos_GBM__A"].iloc[0], g["R2_oos_GBM__B"].iloc[0], "imp_gbm")
    lg = sA.load("cmp_ladoalado_imp_logit")
    add("Importância", "AUC fora da amostra (nota >= 4,9)", lg["AUC_oos__A"].iloc[0], lg["AUC_oos__B"].iloc[0], "imp_logit")
    T = sA.load("cmp_rsyn_resumo")
    for r in T.itertuples():
        if pd.notna(r.B):
            add("Rating sintético", r.medida, r.A, r.B, "cmp_rsyn_resumo")
    Dd = sA.load("cmp_ladoalado_analise_a_diferencas")
    for des in ("estimated_occupancy_l365d", "estimated_revenue_l365d", "number_of_reviews_ltm"):
        for esc in ("amostra completa", "teto: R_off >= 5.0"):
            for comp in ("M1 R_off − M0 controles", "M3 R_off + R_syn − M1 R_off"):
                x = Dd[(Dd["desfecho"] == des) & (Dd["escopo"] == esc) & (Dd["comparacao"] == comp)]
                if len(x):
                    add("Poder explicativo (ganho de R² fora da amostra)", f"{des} | {esc} | {comp}", x["delta_r2_medio__A"].iloc[0], x["delta_r2_medio__B"].iloc[0], "analise_a_diferencas")
    if sA.exists("cmp_queixas_sobreposicao"):
        q = sA.load("cmp_queixas_sobreposicao").iloc[0]
        add("Queixas", "tópicos em comum entre as 15 queixas de maior peso (A × B)", float(q["em_comum"]), float(q["em_comum"]), "cmp_queixas_sobreposicao")
    return pd.DataFrame(rows)


def run(cfg, store: Store) -> None:
    with stage("Etapa 24 — Lado a lado A × B e análises com os dois modelos"):
        sA, sB = Store(cfg, suffix=""), Store(cfg, suffix="__B")
        sA.save("perfil_cobertura", _cobertura(sA, cfg))
        sB.save("perfil_cobertura", _cobertura(sB, cfg))
        for nome, keys in BLOCOS:
            try:
                sA.save(f"cmp_ladoalado_{nome}", lado(sA, sB, nome, keys))
            except Exception as e:  # tabela ausente em um dos lados: registra e segue
                log.warning("lado a lado %s: %s", nome, e)

        # 2.5 resumo do R_syn por modelo + concordância entre os R_syn de A e B
        ra, rb = _resumo_rsyn(sA, cfg), _resumo_rsyn(sB, cfg)
        RA, RB = sA.load("rating_sintetico"), sB.load("rating_sintetico")
        comum = RA[["id", "R_syn_raw"]].merge(RB[["id", "R_syn_raw"]], on="id", suffixes=("_A", "_B"))
        T = pd.DataFrame({"medida": list(ra), "A": list(ra.values()), "B": [rb.get(k) for k in ra]})
        T.loc[len(T)] = ["spearman_R_syn_A_x_R_syn_B (anúncios em comum)", float(stats.spearmanr(comum["R_syn_raw_A"], comum["R_syn_raw_B"])[0]), np.nan]
        T.loc[len(T)] = ["anuncios_com_R_syn_nos_dois_modelos", float(len(comum)), np.nan]
        sA.save("cmp_rsyn_resumo", T)

        # 2.6 Análise A na interseção (mesmos anúncios para os dois modelos)
        ids = set(RA["id"]) & set(RB["id"])
        out = []
        for nome, R, st_ in (("A", RA, sA), ("B", RB, sB)):
            sA.save(f"cmp_rating_inter_{nome}", R[R["id"].isin(ids)].reset_index(drop=True))
            M, Dd, C = run_analise_a(cfg, sA, f"cmp_rating_inter_{nome}", persist=False)
            sA.save(f"cmp_inter_modelos_{nome}", M)
            sA.save(f"cmp_inter_diferencas_{nome}", Dd)
            sA.save(f"cmp_inter_coefs_{nome}", C)
            out.append(Dd.assign(modelo_sentimento=nome))
        Dd = pd.concat(out)
        keys = ["desfecho", "escopo", "comparacao"]
        w = Dd.pivot_table(index=keys, columns="modelo_sentimento", values=["delta_r2_medio", "p2.5", "p97.5", "n"]).reset_index()
        w.columns = ["__".join([c for c in col if c]) if isinstance(col, tuple) else col for col in w.columns]
        sA.save("cmp_inter_diferencas", w)

        # 2.9 comparações múltiplas: coeficientes de R_syn dentro da amostra (desfechos × escopos), BH por modelo
        rows = []
        for nome, s in (("A", sA), ("B", sB)):
            C = s.load("analise_a_coefs")
            C = C[C["termo"].str.startswith("R_syn")].copy()
            p = C["p"].to_numpy()
            o = np.argsort(p)
            q = np.empty_like(p)
            q[o] = np.minimum.accumulate((p[o] * len(p) / (np.arange(len(p)) + 1))[::-1])[::-1]
            C["q_BH"] = np.minimum(q, 1)
            C["modelo_sentimento"] = nome
            C["n_testes_na_familia"] = len(C)
            rows.append(C[["modelo_sentimento", "desfecho", "escopo", "n", "termo", "coef", "ep_HC3", "p", "q_BH", "n_testes_na_familia"]])
        sA.save("cmp_comparacoes_multiplas", pd.concat(rows, ignore_index=True))

        # 2.10 seleção no teto: anúncios de nota 5,0 com e sem R_syn (independe do modelo de sentimento: R_syn exige aspectos com >= 2 frases)
        L = sA.load("listings_elig")
        Sx = sA.load("sentences")[["listing_id", "lang"]]
        pt = Sx.assign(pt=(Sx["lang"] == "pt")).groupby("listing_id")["pt"].mean().rename("prop_pt")
        L = L.merge(pt, left_on="id", right_index=True, how="left")
        top = L[L["review_scores_rating"] == 5.0].copy()
        top["com_Rsyn"] = top["id"].isin(RA["id"])
        top["pt_predominante"] = top["prop_pt"] >= 0.5
        rows = []
        for v in ("number_of_reviews", "price_num", "prop_pt"):
            a, b = top.loc[top["com_Rsyn"], v].dropna(), top.loc[~top["com_Rsyn"], v].dropna()
            sd = np.sqrt((a.var() + b.var()) / 2)
            rows.append({"variavel": v, "categoria": "(numérica)", "n_com_Rsyn": len(a), "n_sem_Rsyn": len(b), "com_Rsyn_media": a.mean(), "sem_Rsyn_media": b.mean(),
                         "com_Rsyn_mediana": a.median(), "sem_Rsyn_mediana": b.median(), "dif_padronizada": (a.mean() - b.mean()) / sd if sd > 0 else np.nan, "p": float(stats.mannwhitneyu(a, b).pvalue)})
        for v, cats in (("room_type", sorted(top["room_type"].unique())), ("pt_predominante", [True, False]),
                        ("neighbourhood_cleansed", list(top["neighbourhood_cleansed"].value_counts().head(8).index))):
            tab = pd.crosstab(top[v], top["com_Rsyn"])
            p = float(stats.chi2_contingency(tab)[1]) if tab.shape[0] > 1 and (tab.sum(axis=1) > 0).all() else np.nan
            for c in cats:
                m = top[v] == c
                rows.append({"variavel": v, "categoria": str(c), "n_com_Rsyn": int((m & top["com_Rsyn"]).sum()), "n_sem_Rsyn": int((m & ~top["com_Rsyn"]).sum()),
                             "com_Rsyn_media": float(m[top["com_Rsyn"]].mean()), "sem_Rsyn_media": float(m[~top["com_Rsyn"]].mean()), "p": p})
        Sel = pd.DataFrame(rows)
        Sel.insert(0, "resumo", "")
        Sel.loc[0, "resumo"] = f"Nota 5,0: {len(top)} anúncios; {int(top['com_Rsyn'].sum())} ({100 * top['com_Rsyn'].mean():.1f}%) com R_syn"
        sA.save("cmp_selecao_teto", Sel)

        # 2.4 sobreposição das queixas de maior peso
        rows, listas = [], {}
        for nome, s in (("A", sA), ("B", sB)):
            Q = s.load("imp_topicos_queixas")
            Q = Q[(Q["q_BH"] < 0.05) & (Q["efeito_pontos_percentil_nota"] < 0)].head(15)
            listas[nome] = Q
        ta, tb = set(listas["A"]["topic"]), set(listas["B"]["topic"])
        resumo = pd.DataFrame([{"top_N": 15, "em_A": len(ta), "em_B": len(tb), "em_comum": len(ta & tb), "jaccard": len(ta & tb) / max(1, len(ta | tb))}])
        Lq = pd.concat([listas["A"][["topic", "top_words", "aspecto", "prevalencia", "efeito_pontos_percentil_nota"]].assign(lista="A", posto=range(1, len(listas["A"]) + 1)),
                        listas["B"][["topic", "top_words", "aspecto", "prevalencia", "efeito_pontos_percentil_nota"]].assign(lista="B", posto=range(1, len(listas["B"]) + 1))])
        sA.save("cmp_queixas_sobreposicao", resumo)
        sA.save("cmp_queixas_listas", Lq)
        log.info("Resumo do R_syn A × B:\n%s", T.round(4).to_string(index=False))
        log.info("Seleção no teto:\n%s", Sel.round(3).to_string(index=False))
        log.info("Comparações múltiplas (R_syn):\n%s", pd.concat(rows if False else [sA.load("cmp_comparacoes_multiplas")]).round(4).to_string(index=False))
        log.info("Sobreposição das 15 queixas de maior peso:\n%s", resumo.round(3).to_string(index=False))
        sA.metric("etapa24", anuncios_comuns_com_Rsyn=len(ids))
