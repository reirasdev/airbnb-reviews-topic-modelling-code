#!/usr/bin/env python3
"""Verifica os numeros novos do texto revisado (ajustes do orientador, 14/10/2026) contra as abas _v2 e as tabelas do cache.

Cada linha: (descricao, valor escrito no texto, valor calculado, casas decimais). Imprime OK ou FALHA e termina com codigo 1 se houver falha.
Uso (Python com pandas e pyarrow), da raiz do repositorio:  python redacao/verificar_numeros_v2.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
V2 = REPO / "outputs" / "ajustes_v2"
CACHE = REPO / "outputs" / "cache" / "375f221f" / "tables"
r = lambda n: pd.read_parquet(V2 / f"{n}.parquet")
c = lambda n: pd.read_parquet(CACHE / f"{n}.parquet")
checks: list[tuple[str, float, float, int]] = []


def add(desc, texto, calc, casas=1):
    checks.append((desc, float(texto), float(calc), casas))


# ---------------------------------------------------------------- M2: Wilson e dois anotadores (Tabela 6)
W = r("Classificacao_IC_v2").set_index("aspecto")
tab6 = {"limpeza": (67, 48, 81, 2, 6), "localizacao": (74, 55, 87, 7, 8), "custo_beneficio": (74, 55, 87, 5, 8), "checkin": (56, 37, 72, 3, 4),
        "comunicacao": (44, 28, 63, 2, 3), "precisao": (70, 52, 84, 5, 5), "satisfacao_geral": (41, 25, 59, 1, 4), "ruido_conforto": (44, 28, 63, 4, 5),
        "seguranca": (48, 31, 66, 5, 6), "comodidades": (44, 28, 63, 3, 6)}
for a, (p, lo, hi, amb, um) in tab6.items():
    add(f"Tabela 6 {a} precisao", p, 100 * W.loc[a, "precisao"], 0)
    add(f"Tabela 6 {a} Wilson inf", lo, 100 * W.loc[a, "wilson_inf"], 0)
    add(f"Tabela 6 {a} Wilson sup", hi, 100 * W.loc[a, "wilson_sup"], 0)
    add(f"Tabela 6 {a} ambos", amb, W.loc[a, "ambos_concordam_com_modelo"], 0)
    add(f"Tabela 6 {a} ao menos um", um, W.loc[a, "pelo_menos_um_concorda"], 0)
    add(f"Tabela 6 {a} n=9", 9, W.loc[a, "n_100"], 0)
P = r("Concord_anotadores_v2").set_index("aspecto_anotador1").loc["limpeza"]
add("limpeza concordancia entre anotadores n", 6, P["n"], 0)
add("limpeza concordancia entre anotadores %", 33, 100 * P["concordancia"], 0)
add("limpeza Wilson inf", 10, 100 * P["wilson_inf"], 0)
add("limpeza Wilson sup", 70, 100 * P["wilson_sup"], 0)
add("comodidades Wilson (discussao) inf", 28, 100 * W.loc["comodidades", "wilson_inf"], 0)
add("comodidades Wilson (discussao) sup", 63, 100 * W.loc["comodidades", "wilson_sup"], 0)
add("n geral na amostra de 100", 10, W.loc["geral", "n_100"], 0)

# ---------------------------------------------------------------- R2: queixas com duas menções
Q = r("Queixas_min2_v2")
S = r("Queixas_min2_resumo_v2").set_index("modelo")
qa = Q[(Q.modelo == "A") & (Q.topic == 18)].iloc[0]
add("banheiro n base", 3955, qa["n_base"], 0)
add("banheiro n min2", 1009, qa["n_min2"], 0)
add("testadas base A", 68, S.loc["A", "testadas_base"], 0)
add("testadas min2 A", 13, S.loc["A", "testadas_min2"], 0)
add("top15 testaveis A", 11, S.loc["A", "top15_base_testadas_em_min2"], 0)
add("top15 mantem sinal e q A", 11, S.loc["A", "top15_base_com_q05_e_sinal_igual_em_min2"], 0)
add("media base A", -18.9, S.loc["A", "efeito_medio_base_nas_testadas"], 1)
add("media min2 A", -20.9, S.loc["A", "efeito_medio_min2_nas_testadas"], 1)
add("variacao min A", -5.3, S.loc["A", "variacao_min_top15"], 1)
add("variacao max A", 0.1, S.loc["A", "variacao_max_top15"], 1)
add("top15 testaveis B", 10, S.loc["B", "top15_base_testadas_em_min2"], 0)
add("media base B", -20.0, S.loc["B", "efeito_medio_base_nas_testadas"], 1)
add("media min2 B", -23.2, S.loc["B", "efeito_medio_min2_nas_testadas"], 1)
add("coincidencia A e B min2", 10, S.loc["A", "coincidencia_top15_A_B_min2"], 0)
nt = Q[(Q.modelo == "A") & Q.n_min2_se_nao_testada.notna() & (Q.rank_base <= 15)]["n_min2_se_nao_testada"]
add("nao testadas A: minimo", 52, nt.min(), 0)
add("nao testadas A: maximo", 86, nt.max(), 0)
add("nao testadas A: quantidade", 4, len(nt), 0)
pc = c("cmp_manual_por_classe")
a_neg = pc[(pc.modelo == "A") & (pc.classe_prevista == "negativo")].iloc[0]
add("A previsto negativo: n", 84, a_neg["n_previstas"], 0)
add("A previsto negativo: acerto %", 62, 100 * a_neg["acerto"], 0)
add("A previsto negativo: acertos (52 de 84)", 52, round(a_neg["acerto"] * a_neg["n_previstas"]), 0)

# ---------------------------------------------------------------- R3: comodidades em subaspectos (Tabela 9)
L = r("LMG_comodidades_v2")
g = lambda m, k, p: L[(L.modelo == m) & L.variante.str.contains(k) & (L.preditor == p)].iloc[0]
subs = {"banheiro_chuveiro": (25, 6.1, 6.8, 9.9, 10.5), "climatizacao": (12, 1.2, 1.5, 3.5, 4.5), "cozinha_utensilios": (20, 3.9, 4.7, 6.6, 7.5),
        "cama_colchao": (10, 1.7, 2.0, 4.6, 5.6), "internet": (5, 0.7, 0.7, 1.5, 1.7), "manutencao_reparos": (9, 3.5, 4.0, 7.8, 8.2), "demais_comodidades": (62, 8.1, 10.1, 8.1, 10.4)}
for p, (pr, a2, b2, a1, b1) in subs.items():
    add(f"Tab 9 {p} prop", pr, 100 * g("A", "2 sent", p)["proporcao_anuncios_com_dado_proprio"], 0)
    add(f"Tab 9 {p} A2", a2, 100 * g("A", "2 sent", p)["parcela_do_R2"])
    add(f"Tab 9 {p} B2", b2, 100 * g("B", "2 sent", p)["parcela_do_R2"])
    add(f"Tab 9 {p} A1", a1, 100 * g("A", "1 sent", p)["parcela_do_R2"])
    add(f"Tab 9 {p} B1", b1, 100 * g("B", "1 sent", p)["parcela_do_R2"])
S7 = "Soma dos 7 subaspectos de comodidades"
for m, k, v in (("A", "2 sent", 25.2), ("B", "2 sent", 29.8), ("A", "1 sent", 42.1), ("B", "1 sent", 48.3)):
    add(f"Tab 9 soma {m} {k}", v, 100 * g(m, k, S7)["parcela_do_R2"])
for m, k, v in (("A", "2 sent", 0.266), ("B", "2 sent", 0.231), ("A", "1 sent", 0.304), ("B", "1 sent", 0.272)):
    add(f"Tab 9 R2 total {m} {k}", v, g(m, k, "limpeza")["R2_total"], 3)
add("limpeza A 2 sent", 25.3, 100 * g("A", "2 sent", "limpeza")["parcela_do_R2"])
add("limpeza B 2 sent", 25.3, 100 * g("B", "2 sent", "limpeza")["parcela_do_R2"])
add("satisfacao A 2 sent", 23.5, 100 * g("A", "2 sent", "satisfacao_geral")["parcela_do_R2"])
add("limpeza A 1 sent", 19.0, 100 * g("A", "1 sent", "limpeza")["parcela_do_R2"])
add("limpeza B 1 sent", 18.2, 100 * g("B", "1 sent", "limpeza")["parcela_do_R2"])
add("comodidades original A", 42.5, 100 * g("A", "original", "comodidades")["parcela_do_R2"])
add("comodidades original B", 47.8, 100 * g("B", "original", "comodidades")["parcela_do_R2"])
add("33 topicos de comodidades", 33, len(r("Mapa_comodidades_v2")), 0)
add("17 topicos em demais", 17, (r("Mapa_comodidades_v2").subaspecto == "demais_comodidades").sum(), 0)

# ---------------------------------------------------------------- R4: indicadores de ausencia
A4 = r("LMG_ausencia_v2").set_index(["modelo", "aspecto"])
add("R2 total orig A", 0.320, A4.loc[("A", "limpeza"), "R2_total_original"], 3)
add("R2 total ind A", 0.382, A4.loc[("A", "limpeza"), "R2_total_com_indicadores"], 3)
add("R2 total orig B", 0.291, A4.loc[("B", "limpeza"), "R2_total_original"], 3)
add("R2 total ind B", 0.358, A4.loc[("B", "limpeza"), "R2_total_com_indicadores"], 3)
for (m, a), (s, t) in {("A", "comodidades"): (34.3, 41.8), ("B", "comodidades"): (37.3, 45.6)}.items():
    add(f"R4 sentimento {m} {a}", s, 100 * A4.loc[(m, a), "parcela_sentimento_com_indicadores"])
    add(f"R4 soma {m} {a}", t, 100 * A4.loc[(m, a), "parcela_sentimento_mais_indicador"])
add("R4 limpeza A", 15.6, 100 * A4.loc[("A", "limpeza"), "parcela_sentimento_com_indicadores"])
add("R4 limpeza B", 14.5, 100 * A4.loc[("B", "limpeza"), "parcela_sentimento_com_indicadores"])
add("R4 satisfacao A", 13.4, 100 * A4.loc[("A", "satisfacao_geral"), "parcela_sentimento_com_indicadores"])
add("R4 satisfacao B", 7.2, 100 * A4.loc[("B", "satisfacao_geral"), "parcela_sentimento_com_indicadores"])
add("R4 indicador comodidades A", 7.4, 100 * A4.loc[("A", "comodidades"), "parcela_indicador_de_ausencia"])
add("R4 indicador comodidades B", 8.2, 100 * A4.loc[("B", "comodidades"), "parcela_indicador_de_ausencia"])

# ---------------------------------------------------------------- sensibilidade ate 30 avaliacoes (Seção 5.1) e demais
for suf, m, com, lim in (("", "A", 41.2, 18.5), ("__B", "B", 46.8, 18.2)):
    d = c(f"imp_sensibilidade{suf}")
    d = d[d.variante.str.startswith("v <= 30")].set_index("aspecto")
    add(f"<=30 comodidades {m}", com, 100 * d.loc["comodidades", "parcela_do_R2"])
    add(f"<=30 limpeza {m}", lim, 100 * d.loc["limpeza", "parcela_do_R2"])
add("<=30 n anuncios", 19623, d["n"].iloc[0], 0)
L0 = c("listings_elig")
rt = L0.review_scores_rating.dropna()
add("percentil da nota 5,0", 83.8, 100 * rt.rank(pct=True)[rt == 5].iloc[0])
add("valores distintos da nota", 143, rt.nunique(), 0)
add("anuncios com nota 5,0", 9373, (rt == 5).sum(), 0)
add("% nota 5,0 entre elegiveis", 32.4, 100 * (rt == 5).mean())

# ---------------------------------------------------------------- Figura 2, Tabela 16 e percentil do indice
F2 = r("Fig2_resumo_v2").set_index("medida")
add("% 5,0 entre 22.564", 22.8, F2.loc["% = 5,0", "nota_oficial"])
add("n com indice", 22564, F2.loc["n", "nota_oficial"], 0)
T12 = r("Tabela12_completa_v2")
add("Tabela 16: linhas", 12, len(T12), 0)
add("M1-M0 A ocupacao amostra completa", 0.0079, T12.iloc[0]["A_M1_menos_M0"], 4)
add("M3-M1 B receita amostra completa", 0.0014, T12.iloc[4]["B_M3_menos_M1"], 4)
dt = c("descritivo_teto")
dt = dt[dt["medida"].str.contains("percentil de R_syn")].iloc[0]
add("percentil do indice p5", 27, 100 * dt["p5"], 0)
add("percentil do indice p95", 98, 100 * dt["p95"], 0)

falhas = 0
for d, t, v, casas in checks:
    ok = abs(v - t) < 0.5 * 10 ** (-casas) + 1e-9
    falhas += not ok
    print(("OK    " if ok else "FALHA ") + f"{d}: texto={t} calculado={v:.6g}")
print(f"\n{len(checks)} conferencias; {falhas} falhas")
sys.exit(1 if falhas else 0)
