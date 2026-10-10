"""Seções 5 a 7 do texto unificado: o que o texto revela sobre a nota; aplicação; um índice único acrescenta algo?"""
from __future__ import annotations

from doc_base import *  # noqa: F401,F403
from scipy import stats as _st  # noqa: E402


def classificar() -> dict[str, str]:
    """Mesmo critério da seção 4.6: precisão de atribuição >= 0,60 e correlação >= 0,20 com a subnota nos dois modelos."""
    pa = L(sA, "cmp_manual_aspecto_por_classe").set_index("aspecto_previsto")["precisao"]
    va, vb = L(sA, "validacao_construto").set_index("aspecto")["spearman"], L(sB, "validacao_construto").set_index("aspecto")["spearman"]
    return {a: ("confiável" if (a in SUB and pa[a] >= 0.60 and va[a] >= 0.20 and vb[a] >= 0.20) else "cautela") for a in ASP}


def _pal(w: str, k: int = 4) -> str:
    return ", ".join(w.split(", ")[:k])


def secao5() -> str:
    cls = classificar()
    LA, LB = L(sA, "imp_lmg"), L(sB, "imp_lmg")
    ng = "nota_global (review_scores_rating)"
    a, b = LA[LA["alvo"] == ng].set_index("aspecto"), LB[LB["alvo"] == ng].set_index("aspecto")
    ordem = list(a.sort_values("parcela_do_R2", ascending=False).index)
    t_lmg = tabela(["Aspecto", "Parcela do R² (A)", "Parcela do R² (B)", "Classificação (seção 4.6)"], [[ROT[x], pc(a.loc[x, "parcela_do_R2"], 1), pc(b.loc[x, "parcela_do_R2"], 1), cls[x]] for x in ordem], "|---|---:|---:|---|")
    rho_ab = _st.spearmanr(a["parcela_do_R2"], b["parcela_do_R2"].reindex(a.index))[0]
    sub_rows = []
    for alvo in LA["alvo"].unique():
        if alvo.startswith("nota_global"):
            continue
        asp = alvo.split(" ")[0]
        d, db = LA[LA["alvo"] == alvo].set_index("aspecto"), LB[LB["alvo"] == alvo].set_index("aspecto")
        top = d["parcela_do_R2"].idxmax()
        sub_rows.append([alvo.split("(")[1].rstrip(")").replace("review_scores_", ""), f(d["R2_total"].iloc[0], 3), ROT[asp], pc(d.loc[asp, "parcela_do_R2"], 1), pc(db.loc[asp, "parcela_do_R2"], 1), ROT[top]])
    t_sub = tabela(["Subnota", "R² total (A)", "Aspecto correspondente", "Sua parcela (A)", "Sua parcela (B)", "Aspecto de maior parcela (A)"], sub_rows, "|---|---:|---|---:|---:|---|")
    gA, gB = L(sA, "imp_gbm"), L(sB, "imp_gbm")
    lgA, lgB = L(sA, "imp_logit"), L(sB, "imp_logit")
    orA, orB = lgA.set_index("termo"), lgB.set_index("termo")
    perm = gA.set_index("aspecto")["queda_R2_oos_por_permutacao"].sort_values(ascending=False)
    sgA, sgB = L(sA, "imp_segmentos"), L(sB, "imp_segmentos")
    snA, snB = L(sA, "imp_sensibilidade"), L(sB, "imp_sensibilidade")
    topA_seg = sgA.sort_values("parcela_do_R2", ascending=False).groupby("segmento").head(1)
    topB_seg = sgB.sort_values("parcela_do_R2", ascending=False).groupby("segmento").head(1)
    topA_sen = snA.sort_values("parcela_do_R2", ascending=False).groupby("variante").head(1)
    topB_sen = snB.sort_values("parcela_do_R2", ascending=False).groupby("variante").head(1)
    como_seg = sgA[sgA["aspecto"] == "comodidades"]["parcela_do_R2"]
    como_segB = sgB[sgB["aspecto"] == "comodidades"]["parcela_do_R2"]
    qA, eA = L(sA, "imp_topicos_queixas"), L(sA, "imp_topicos_elogios")
    qB = L(sB, "imp_topicos_queixas")
    qa = qA[(qA["q_BH"] < 0.05) & (qA["efeito_pontos_percentil_nota"] < 0)].head(13)
    qb15 = qB[(qB["q_BH"] < 0.05) & (qB["efeito_pontos_percentil_nota"] < 0)].head(15)
    qa15 = qA[(qA["q_BH"] < 0.05) & (qA["efeito_pontos_percentil_nota"] < 0)].head(15)
    comum = set(qa15["topic"]) & set(qb15["topic"])
    so_a = qa15[~qa15["topic"].isin(comum)]
    so_b = qb15[~qb15["topic"].isin(comum)]
    ea = eA[(eA["q_BH"] < 0.05) & (eA["efeito_pontos_percentil_nota"] > 0)].sort_values("impacto_x_prevalencia", ascending=False).head(6)
    t_q = tabela(["Tópico (palavras de maior peso)", "Aspecto (classificação)", "Anúncios com menção", "Efeito no percentil da nota", "q (BH)"],
                 [[_pal(r.top_words), f"{ROT.get(r.aspecto, r.aspecto)} ({cls.get(r.aspecto, '—')})", pc(r.prevalencia, 0), f(r.efeito_pontos_percentil_nota, 1) + " pontos", f(r.q_BH, 3)] for r in qa.itertuples()], "|---|---|---:|---:|---:|")
    t_e = tabela(["Tópico (palavras de maior peso)", "Aspecto (classificação)", "Anúncios com menção", "Efeito no percentil da nota", "q (BH)"],
                 [[_pal(r.top_words), f"{ROT.get(r.aspecto, r.aspecto)} ({cls.get(r.aspecto, '—')})", pc(r.prevalencia, 0), f(r.efeito_pontos_percentil_nota, 1, True) + " pontos", f(r.q_BH, 3)] for r in ea.itertuples()], "|---|---|---:|---:|---:|")
    qs = qA[(qA["q_BH"] < 0.05) & (qA["efeito_pontos_percentil_nota"] < 0)]
    n_q_sig, n_q, n_e_sig, n_e = len(qs), len(qA), int(((eA["q_BH"] < 0.05) & (eA["efeito_pontos_percentil_nota"] > 0)).sum()), len(eA)
    return f"""## 5. O que o texto revela sobre a nota
{abas("Imp_Aspectos", "Imp_Modelos", "Imp_Segmentos_Sens", "Imp_Topicos_Queixas", "Imp_Topicos_Elogios", "LadoALado_imp_lmg", "LadoALado_imp_gbm", "LadoALado_imp_logit", "LadoALado_imp_segmentos", "LadoALado_imp_sensibilidade")}
Estabelecido quais medidas merecem confiança (seção 4.6), esta seção apresenta a contribuição central do estudo: **o que o texto das avaliações revela sobre a nota que o anúncio recebe**. Primeiro, quais aspectos mais se associam à nota global e a cada subnota; depois, quais tópicos finos concentram as queixas
e os elogios. Tudo é associação, não causa.

### 5.1 Importância dos aspectos
{abas("Imp_Aspectos", "Imp_Modelos", "Imp_Segmentos_Sens", "LadoALado_imp_lmg", "LadoALado_imp_gbm", "LadoALado_imp_logit", "LadoALado_imp_segmentos", "LadoALado_imp_sensibilidade")}
A análise usa os {n(a['n'].iloc[0])} anúncios com texto, inclusive os de pouco texto (o sentimento não observado de um aspecto é imputado pela média, e isso evita exigir três aspectos por anúncio), e toma como alvo o percentil da nota (a nota é comprimida no topo). A decomposição
LMG (média de Shapley) reparte o R² da regressão da nota global sobre o sentimento dos dez aspectos; o R² total é de {f(a['R2_total'].iloc[0], 3)} em A e {f(b['R2_total'].iloc[0], 3)} em B. Parcela de cada aspecto:

{t_lmg}

**Comodidades** responde por {pc(a.loc['comodidades', 'parcela_do_R2'], 1)} do R² em A e {pc(b.loc['comodidades', 'parcela_do_R2'], 1)} em B, seguida por limpeza ({pc(a.loc['limpeza', 'parcela_do_R2'], 1)} e {pc(b.loc['limpeza', 'parcela_do_R2'], 1)}); satisfação geral e comunicação vêm depois. Localização, custo-benefício e segurança quase não contribuem para a
**nota global**, embora localização seja o aspecto que mais explica a sua própria subnota (tabela abaixo): o hóspede avalia o local em separado, e a nota global parece refletir mais o que ele viveu dentro do imóvel. A ordem das parcelas é muito parecida entre os modelos (correlação de postos {f(rho_ab)}); a diferença mais
visível é a satisfação geral, que pesa menos em B. Ressalvas da seção 4.6: comodidades e satisfação geral estão na classe "cautela", e a importância relativa de um aspecto mistura efeito e confiabilidade da medida (aspectos pouco citados, como segurança e custo-benefício, são medidos com mais erro e imputados na maioria dos anúncios).

Para cada subnota, o aspecto correspondente está entre os que mais a explicam (modelo A, com a parcela também em B):

{t_sub}

Dois modelos mais flexíveis dão a mesma leitura. Um GBM com valores ausentes tem R² fora da amostra de {f(gA['R2_oos_GBM'].iloc[0], 3)} em A e {f(gB['R2_oos_GBM'].iloc[0], 3)} em B (regressão linear com imputação: {f(gA['R2_oos_OLS_imputado'].iloc[0], 3)} e {f(gB['R2_oos_OLS_imputado'].iloc[0], 3)}); a queda de R² por permutação é maior em
{ROT[perm.index[0]]} ({f(perm.iloc[0], 3)}), {ROT[perm.index[1]]} ({f(perm.iloc[1], 3)}) e {ROT[perm.index[2]]} ({f(perm.iloc[2], 3)}) no modelo A. Na regressão logística para "nota ≥ 4,9" (que {pc(lgA['prop_nota_alta'].iloc[0], 0)} dos anúncios têm; AUC fora da amostra {f(lgA['AUC_oos'].iloc[0], 3)} em A e {f(lgB['AUC_oos'].iloc[0], 3)} em B), um desvio-padrão a mais de sentimento
multiplica as chances de nota alta por {f(orA.loc['s_comodidades', 'odds_ratio_por_DP'])} em comodidades, {f(orA.loc['s_limpeza', 'odds_ratio_por_DP'])} em limpeza, {f(orA.loc['s_satisfacao_geral', 'odds_ratio_por_DP'])} em satisfação geral e {f(orA.loc['s_comunicacao', 'odds_ratio_por_DP'])} em comunicação (A); em B, {f(orB.loc['s_comodidades', 'odds_ratio_por_DP'])}, {f(orB.loc['s_limpeza', 'odds_ratio_por_DP'])}, {f(orB.loc['s_satisfacao_geral', 'odds_ratio_por_DP'])} e {f(orB.loc['s_comunicacao', 'odds_ratio_por_DP'])}.

O resultado é estável. Comodidades é o aspecto de maior parcela em {n((topA_seg['aspecto'] == 'comodidades').sum())} dos {n(len(topA_seg))} segmentos (tipo de acomodação, idioma predominante e os seis maiores bairros) em A e em {n((topB_seg['aspecto'] == 'comodidades').sum())} dos {n(len(topB_seg))} em B, com parcela de {pc(como_seg.min(), 0)} a {pc(como_seg.max(), 0)} (A) e de
{pc(como_segB.min(), 0)} a {pc(como_segB.max(), 0)} (B); e é o de maior parcela em {n((topA_sen['aspecto'] == 'comodidades').sum())} das {n(len(topA_sen))} sensibilidades (todos os anúncios, só tópicos diretos, até 30 avaliações, ao menos 3 aspectos, sem satisfação geral como preditor) em A e em {n((topB_sen['aspecto'] == 'comodidades').sum())} das {n(len(topB_sen))} em B.

### 5.2 Queixas e elogios por tópico
{abas("Imp_Topicos_Queixas", "Imp_Topicos_Elogios", "RSyn_Resumo_AB")}
A leitura prática está nos tópicos finos, cuja atribuição de aspecto é mais precisa (tópicos diretos). Para cada tópico, comparamos o percentil da nota entre anúncios com e sem ao menos uma menção negativa (ou positiva) no tópico, controlando o volume de avaliações e de frases; as {n(n_q)} queixas e {n(n_e)} elogios com
amostra suficiente foram testados com correção de Benjamini-Hochberg ({n(n_q_sig)} queixas e {n(n_e_sig)} elogios com q < 0,05 no sentido esperado). Queixas de maior peso (efeito × prevalência), modelo A:

{t_q}

Chamam atenção as queixas de instalações e manutenção (banheiro, ar-condicionado, cozinha, cama, wi-Fi, reparos), de limpeza (sujeira, cheiro) e de resposta do anfitrião, que se associam a quedas de 10 a 26 pontos no percentil da nota entre os anúncios que as recebem. Entre as **15 queixas de maior peso**, {n(len(comum))} coincidem nos dois modelos: a lista é robusta à escolha do modelo
(em A e não em B: {'; '.join(_pal(w, 3) for w in so_a['top_words']) or 'nenhuma'}; em B e não em A: {'; '.join(_pal(w, 3) for w in so_b['top_words']) or 'nenhuma'}). Elogios mais associados a notas altas, modelo A:

{t_e}

A queixa genérica ("decepcionado, problemas") e os elogios genéricos (sentir-se em casa, voltar) pertencem a satisfação geral, aspecto de cautela, e servem sobretudo como termômetro.

### 5.3 Cuidados de interpretação
Sem rótulo causal: um anúncio com queixa de banheiro tem nota menor, mas isto não quer dizer que consertar o banheiro eleve a nota. O "efeito" é a diferença média, na cidade, entre anúncios com e sem a menção, controlada por volume. A atribuição de aspecto acerta entre {pc(L(sA, 'cmp_manual_aspecto').set_index('medida').loc['acurácia de aspecto ponderada (só pela participação do aspecto)', 'valor'], 0)} e
{pc(L(sA, 'cmp_manual_aspecto').set_index('medida').loc['acurácia de aspecto ponderada (estratos aspecto × polaridade)', 'valor'], 0)} na população (seção 4.1), e a importância por aspecto fica abaixo da dos tópicos, o que reforça a leitura por tópico.
"""


def secao6() -> str:
    cls = classificar()
    B = L(sA, "benchmark_bairro_tipo")
    C = L(sA, "benchmark_cidade_tipo")
    ok = [ROT[a] for a in ASP if cls[a] == "confiável"]
    return f"""## 6. Aplicação: diagnóstico por anúncio
{abas("Benchmark_Bairro_Tipo")}
A seção 5 diz o que se associa à nota; esta mostra como um anfitrião ou uma empresa gestora usa isso. A ferramenta `diagnostico.py` gera, a pedido, o relatório de **um** anúncio: o sentimento médio em cada aspecto e a posição (percentil) entre anúncios do mesmo bairro e tipo de acomodação (ou do tipo na cidade, quando o bairro
tem poucos anúncios); a evidência de cada aspecto (poucas frases, evidência baixa, sem rótulo de força ou atenção); as queixas e os elogios recorrentes do anúncio, com a associação média, na cidade, desses tópicos com o percentil da nota (seção 5.2); e a evolução do sentimento nas avaliações mais recentes. A ferramenta funciona
também para anúncios novos, marcando a evidência como baixa em vez de omitir o aspecto.

Para a comparação, a Etapa 17 construiu tabelas de referência: {n(len(B))} grupos de bairro e tipo de acomodação com ao menos 30 anúncios e {n(len(C))} grupos por tipo na cidade (aba `Benchmark_Bairro_Tipo`), com mediana e quartis do sentimento por aspecto e da nota. O relatório respeita a classificação da seção 4.6: a nota metodológica que o acompanha informa a precisão
da atribuição por aspecto, e os aspectos de cautela não devem orientar decisões isoladamente (os confiáveis são {', '.join(ok)}). Três exemplos anonimizados (um anúncio de nota alta, um de nota baixa e um com poucas avaliações) estão em `redacao/exemplos_diagnostico/`: no de nota baixa, o relatório aponta
comodidades e satisfação geral muito abaixo dos pares e as queixas de banheiro e cozinha; no de poucas avaliações, a maior parte dos aspectos aparece com evidência baixa. O relatório prioriza onde investigar, e não prevê nota nem prescreve causas.
"""


def _d(s: Store) -> pd.DataFrame:
    return L(s, "analise_a_diferencas")


def secao7() -> str:
    R = L(sA, "cmp_rsyn_resumo").set_index("medida")
    Ra = R["A"]
    Rb = R["B"]
    sel = L(sA, "cmp_selecao_teto")
    sel_n = sel.set_index(["variavel", "categoria"])
    lim = L(sA, "limite30").set_index("medida")["valor"]
    limb = L(sB, "limite30").set_index("medida")["valor"]
    dA, dB = _d(sA), _d(sB)
    desf = [("estimated_occupancy_l365d", "Índice de ocupação"), ("estimated_revenue_l365d", "Índice de receita (log)"), ("number_of_reviews_ltm", "Avaliações em 12 meses (log)")]
    escs = [("amostra completa", "amostra completa"), ("teto: R_off >= 4.8", "nota ≥ 4,8"), ("teto: R_off >= 4.9", "nota ≥ 4,9"), ("teto: R_off >= 5.0", "nota = 5,0")]

    def g(df, des, esc, comp):
        r = df[(df["desfecho"] == des) & (df["escopo"] == esc) & (df["comparacao"] == comp)]
        return r.iloc[0] if len(r) else None

    c1, c2, c3 = "M1 R_off − M0 controles", "M2 R_syn − M1 R_off", "M3 R_off + R_syn − M1 R_off"
    lin = []
    nexcl = {"A": 0, "B": 0}
    for des, dn in desf:
        for esc, en in escs:
            x1, x2, x3, y3 = g(dA, des, esc, c1), g(dA, des, esc, c2), g(dA, des, esc, c3), g(dB, des, esc, c3)
            for tag, r in (("A", x3), ("B", y3)):
                if r is not None and (r["p2.5"] > 0 or r["p97.5"] < 0):
                    nexcl[tag] += 1
            lin.append([dn, en, f(x1["delta_r2_medio"], 4, True) + " " + ic(x1["p2.5"], x1["p97.5"], 4, True), f(x2["delta_r2_medio"], 4, True) + " " + ic(x2["p2.5"], x2["p97.5"], 4, True),
                        f(x3["delta_r2_medio"], 4, True) + " " + ic(x3["p2.5"], x3["p97.5"], 4, True), f(y3["delta_r2_medio"], 4, True) + " " + ic(y3["p2.5"], y3["p97.5"], 4, True)])
    t_pe = tabela(["Desfecho", "Escopo", "M1 − M0: nota oficial (A)", "M2 − M1: R_syn no lugar da nota (A)", "M3 − M1: R_syn além da nota (A)", "M3 − M1 (B)"], lin, "|---|---|---|---|---|---|")
    mdl = L(sA, "analise_a_modelos")
    r2_ocup = mdl[(mdl["desfecho"] == "estimated_occupancy_l365d") & (mdl["escopo"] == "amostra completa")].set_index("modelo")["r2_oos_medio"]
    inter = L(sA, "cmp_inter_diferencas")
    ic3 = inter[inter["comparacao"] == c3]
    dif_inter = (ic3["delta_r2_medio__A"] - ic3["delta_r2_medio__B"]).abs().max()
    CM = L(sA, "cmp_comparacoes_multiplas")
    cm = CM.pivot_table(index=["desfecho", "escopo"], columns="modelo_sentimento", values=["coef", "p", "q_BH"])
    lin2 = []
    nm = {"estimated_occupancy_l365d": "Índice de ocupação", "estimated_revenue_l365d": "Índice de receita (log)", "number_of_reviews_ltm": "Avaliações em 12 meses (log)"}
    en = dict(escs)
    for (des, esc), r in cm.iterrows():
        lin2.append([nm[des], en[esc], f(r[("coef", "A")], 3, True), f(r[("p", "A")], 4), f(r[("q_BH", "A")], 4), f(r[("coef", "B")], 3, True), f(r[("p", "B")], 4), f(r[("q_BH", "B")], 4)])
    lin2.sort(key=lambda x: (list(nm.values()).index(x[0]), [e for _, e in escs].index(x[1])))
    t_cm = tabela(["Desfecho", "Escopo", "Coef. de R_syn (A)", "p (A)", "q (A)", "Coef. de R_syn (B)", "p (B)", "q (B)"], lin2)
    sigA = int((CM[(CM["modelo_sentimento"] == "A")]["q_BH"] < 0.05).sum())
    sigB = int((CM[(CM["modelo_sentimento"] == "B")]["q_BH"] < 0.05).sum())
    nfam = int(CM["n_testes_na_familia"].iloc[0])
    sinais_ceil_A = CM[(CM["modelo_sentimento"] == "A") & (CM["escopo"] == "teto: R_off >= 5.0")].set_index("desfecho")
    # análise B
    fa, fb = L(sA, "analise_b_faixas"), L(sB, "analise_b_faixas")
    t_b = tabela(["Faixa da nota oficial", "n", "ρ de R_syn × desfecho residual (A)", "ρ de R_syn × desfecho residual (B)", "ρ da nota oficial × desfecho residual", "ρ de R_syn × nota oficial (A)", "% que muda ≥ 10 pp de posto (A)"],
                 [[r.faixa_R_off.replace("[", "[").replace(", ", "; "), n(r.n), f(r.spearman_Rsyn_vs_desempenho_residual, 3), f(fb.set_index("faixa_R_off").loc[r.faixa_R_off, "spearman_Rsyn_vs_desempenho_residual"], 3),
                   f(r.spearman_Roff_vs_desempenho_residual, 3), f(r.spearman_Rsyn_vs_Roff, 3), pc(r.prop_mudanca_relevante, 0)] for r in fa.itertuples()], "|---|---:|---:|---:|---:|---:|---:|")
    ia, ib = L(sA, "analise_b_isotonica").set_index(["escopo", "preditor"])["r2_oos_isotonica_medio"], L(sB, "analise_b_isotonica").set_index(["escopo", "preditor"])["r2_oos_isotonica_medio"]
    # sensibilidade
    sa, sb = L(sA, "sensibilidade"), L(sB, "sensibilidade")
    nomes_v = {"sem_shrinkage": "Sem shrinkage (principal)", "com_shrinkage": "Com shrinkage (m = 23)", "sem_shrinkage_sem_satisfacao": "Sem shrinkage, sem satisfação geral", "com_shrinkage_sem_satisfacao": "Com shrinkage, sem satisfação geral",
               "sem_shrinkage_v30": "Sem shrinkage, só anúncios com até 30 avaliações", "com_shrinkage_v30": "Com shrinkage, só anúncios com até 30 avaliações"}

    def sv(df, v, des):
        r = df[(df["variante"] == v) & (df["bloco"] == "A: delta R2 OOS") & (df["medida"] == c3) & (df["escopo"] == "teto: R_off >= 5.0") & (df["desfecho"] == des)].iloc[0]
        br = df[(df["variante"] == v) & (df["bloco"] == "B: por faixa de R_off") & (df["escopo"] == "faixa = 5,0")].pivot_table(index="variante", columns="medida", values="valor").iloc[0]
        return r, br

    lin3 = []
    for v, nv in nomes_v.items():
        r1, br = sv(sa, v, "number_of_reviews_ltm")
        r0, _ = sv(sa, v, "estimated_occupancy_l365d")
        s1, sbr = sv(sb, v, "number_of_reviews_ltm")
        lin3.append([nv, f(r0["valor"], 4, True), f(r1["valor"], 4, True) + " " + ic(r1["ic_inf"], r1["ic_sup"], 4, True), f(br["spearman R_syn × desempenho bruto"], 2, True), f(br["spearman R_syn × desempenho residual"], 2, True),
                     f(s1["valor"], 4, True), f(sbr["spearman R_syn × desempenho bruto"], 2, True)])
    t_sens = tabela(["Variante", "Δ R² índice de ocupação (A)", "Δ R² avaliações 12 m (A) [IC]", "ρ bruto (A)", "ρ residual (A)", "Δ R² avaliações 12 m (B)", "ρ bruto (B)"], lin3, "|---|---:|---:|---:|---:|---:|---:|")
    sub5 = [k for k in Ra.index if k.startswith("nota5_spearman_R_syn_x_")]
    t_sel = tabela(["Característica (nota 5,0)", "Com R_syn", "Sem R_syn"], [
        ["Anúncios", n(sel_n.loc[("number_of_reviews", "(numérica)"), "n_com_Rsyn"]), n(sel_n.loc[("number_of_reviews", "(numérica)"), "n_sem_Rsyn"])],
        ["Avaliações totais (mediana)", f(sel_n.loc[("number_of_reviews", "(numérica)"), "com_Rsyn_mediana"], 0), f(sel_n.loc[("number_of_reviews", "(numérica)"), "sem_Rsyn_mediana"], 0)],
        ["Preço (mediana)", f(sel_n.loc[("price_num", "(numérica)"), "com_Rsyn_mediana"], 0), f(sel_n.loc[("price_num", "(numérica)"), "sem_Rsyn_mediana"], 0)],
        ["Casa ou apartamento inteiro", pc(sel_n.loc[("room_type", "Entire home/apt"), "com_Rsyn_media"], 0), pc(sel_n.loc[("room_type", "Entire home/apt"), "sem_Rsyn_media"], 0)],
        ["Quarto privado", pc(sel_n.loc[("room_type", "Private room"), "com_Rsyn_media"], 0), pc(sel_n.loc[("room_type", "Private room"), "sem_Rsyn_media"], 0)],
        ["Português predominante", pc(sel_n.loc[("pt_predominante", "True"), "com_Rsyn_media"], 0), pc(sel_n.loc[("pt_predominante", "True"), "sem_Rsyn_media"], 0)]], "|---|---:|---:|")

    return f"""## 7. Um índice único acrescenta algo?
{abas("RSyn_Resumo_AB", "Descritivo_Teto", "Selecao_Teto", "Analise_A", "Analise_A_mB", "Analise_A_Intersecao", "Comparacoes_Multiplas", "Analise_B", "Analise_B_mB", "Sensibilidade", "Sensibilidade_mB", "Limite_30_Avaliacoes")}
Com a seção 5 estabelecida, resta uma pergunta secundária: o que se ganha ao resumir o perfil de aspectos em **um número**, um índice sintético que substitua a nota oficial? É um resultado secundário, e um resultado nulo seria legítimo: a decomposição por aspecto da seção 5 é a contribuição do estudo, e o índice sintético apenas a testa.

### 7.1 Construção
O índice sintético (R_syn) é a média igual dos sentimentos dos aspectos disponíveis do anúncio, em estrelas de 1 a 5, exigindo ao menos {CONFIG.MIN_ASPECTS} aspectos específicos com evidência (a satisfação geral entra na média, mas não conta para o mínimo). Há {n(Ra['anuncios_com_R_syn'])} anúncios com R_syn.
A especificação principal **não** aplica shrinkage (encolhimento empírico-bayesiano com m = 23, a mediana de avaliações), por uma razão teórica: o encolhimento puxa os anúncios de poucas avaliações para a média global e, com isso, correlaciona o índice com o volume de avaliações justamente onde a nota é 5,0 (os anúncios de nota 5,0 têm mediana de
{f(lim['mediana de avaliações totais, nota 5,0 com R_syn'], 0)} avaliações, contra {f(lim['mediana de avaliações totais, nota < 5,0 com R_syn'], 0)} nos demais): entre eles, a correlação de postos do índice com o log do volume é {f(lim['Spearman R_syn com shrinkage × log(avaliações totais), anúncios de nota 5,0'])} com shrinkage e {f(lim['Spearman R_syn sem shrinkage × log(avaliações totais), anúncios de nota 5,0'])} sem ({f(limb['Spearman R_syn com shrinkage × log(avaliações totais), anúncios de nota 5,0'])} e {f(limb['Spearman R_syn sem shrinkage × log(avaliações totais), anúncios de nota 5,0'])} em B).
Registramos que **essa decisão foi tomada depois de ver o resultado** com shrinkage; por isso as duas versões são reportadas (seção 7.5).

### 7.2 Compressão da nota oficial e reordenamento
{abas("RSyn_Resumo_AB", "Selecao_Teto")}
A nota oficial concentra {pc(Ra['prop_valor_modal_R_off(2 casas)'], 1)} dos anúncios com R_syn no valor 5,0; o valor mais comum do índice sintético concentra {pc(Ra['prop_valor_modal_R_syn(2 casas)'], 1)} em A e {pc(Rb['prop_valor_modal_R_syn(2 casas)'], 1)} em B. A correlação de postos entre R_syn e a nota oficial é {f(Ra['spearman_R_syn_R_off'])} em A e {f(Rb['spearman_R_syn_R_off'])} em B; {pc(Ra['prop_muda_>=10pp_de_posto'], 0)} (A) e
{pc(Rb['prop_muda_>=10pp_de_posto'], 0)} (B) dos anúncios mudam 10 pontos percentuais de posto ou mais entre os dois rankings. Os R_syn de A e de B têm correlação de postos {f(R.loc['spearman_R_syn_A_x_R_syn_B (anúncios em comum)', 'A'])}. Entre os anúncios de nota exatamente 5,0 com R_syn ({n(Ra['anuncios_nota_5_com_R_syn'])}), o índice espalha os anúncios entre o percentil
{f(100 * Ra['nota5_percentil_p5'], 0)} e o {f(100 * Ra['nota5_percentil_p95'], 0)} (5º a 95º; B: {f(100 * Rb['nota5_percentil_p5'], 0)} e {f(100 * Rb['nota5_percentil_p95'], 0)}) e concorda fracamente, mas de forma positiva, com as seis subnotas (correlação de postos de {f(min(Ra[k] for k in sub5))} a {f(max(Ra[k] for k in sub5))} em A e de {f(min(Rb[k] for k in sub5))} a {f(max(Rb[k] for k in sub5))} em B; as subnotas também são saturadas).

**Quem entra no teto.** Essa discriminação vale para os anúncios de nota 5,0 **que têm R_syn**: {n(Ra['anuncios_nota_5_com_R_syn'])} dos {n(sel_n.loc[('number_of_reviews', '(numérica)'), 'n_com_Rsyn'] + sel_n.loc[('number_of_reviews', '(numérica)'), 'n_sem_Rsyn'])} anúncios de nota 5,0 ({pc(Ra['anuncios_nota_5_com_R_syn'] / (sel_n.loc[('number_of_reviews', '(numérica)'), 'n_com_Rsyn'] + sel_n.loc[('number_of_reviews', '(numérica)'), 'n_sem_Rsyn']), 1)}). Os que ficam de fora são sobretudo os de pouquíssimas avaliações, que são justamente os mais comprimidos:

{t_sel}

### 7.3 Poder explicativo sobre os índices de volume
{abas("Analise_A", "Analise_A_mB", "Analise_A_Intersecao", "Comparacoes_Multiplas", "Descritivo_Teto")}
Os controles são o volume total de avaliações (log), o preço (log), o tipo de acomodação e o bairro; **não** se controla pelas avaliações dos últimos 12 meses (seção 2). A validação é fora da amostra, com 5 dobras repetidas 5 vezes, mesma semente e mesmas dobras em todos os modelos. M0 são os controles; M1 acrescenta a nota oficial; M2 acrescenta o R_syn
no lugar da nota; M3 acrescenta os dois. No índice de ocupação, na amostra completa, os controles têm R² fora da amostra de {f(r2_ocup['M0 controles'], 3)}, e a nota oficial o eleva a {f(r2_ocup['M1 R_off'], 3)}. Ganho de R² fora da amostra (média entre dobras e intervalo de 2,5% a 97,5% entre dobras):

{t_pe}

A nota oficial acrescenta um poder explicativo pequeno, mas detectável (nos três desfechos, na amostra completa); o R_syn, no lugar dela, explica menos; e **o R_syn não acrescenta poder explicativo além da nota oficial**: o intervalo de M3 − M1 exclui zero em {n(nexcl['A'])} das {n(len(lin))} comparações em A e em {n(nexcl['B'])} em B. Restritos aos {n(Ra['anuncios_com_R_syn_nos_dois_modelos'])}
anúncios com R_syn nos dois modelos, as diferenças M3 − M1 entre A e B são de no máximo {f(dif_inter, 4)} (aba `Analise_A_Intersecao`).

**Coeficientes dentro da amostra.** Em M3, o coeficiente padronizado de R_syn (erro-padrão robusto HC3) aparece significativo em vários desfechos e escopos; reunimos os {n(nfam)} de cada modelo em uma família e aplicamos Benjamini-Hochberg:

{t_cm}

Com a correção, {n(sigA)} de {n(nfam)} coeficientes têm q < 0,05 em A e {n(sigB)} em B. Eles **não são robustos**: mudam de sinal conforme o escopo (negativos na amostra completa, positivos em parte dos tetos) e conforme o modelo de sentimento (por exemplo, no índice de ocupação da amostra completa, o coeficiente não é significativo em A e é negativo e significativo em B), e não se
confirmam fora da amostra (os ganhos M3 − M1 acima têm intervalos que incluem zero na quase totalidade das comparações). Por isso ficam fora da síntese e das conclusões.

### 7.4 Monotonicidade e reordenamento
{abas("Analise_B", "Analise_B_mB")}
O R_syn reordena os anúncios em relação à nota oficial (seção 7.2); a pergunta é se essa reordenação se associa ao desfecho. Correlação de postos entre cada medida e o índice de ocupação residualizado nos controles, por faixa da nota oficial:

{t_b}

Para os dois modelos, a associação do R_syn com o desfecho residual é pequena e muda de sinal entre faixas, e na faixa de nota 5,0 é próxima de zero. A regressão isotônica (relação monótona crescente, avaliada fora da amostra) tem R² de {f(ia[('amostra completa', 'R_off')], 3)} para a nota oficial e {f(ia[('amostra completa', 'R_syn_raw')], 3)} para o R_syn na amostra completa (B: {f(ib[('amostra completa', 'R_syn_raw')], 3)}),
e nos tetos é ≈ 0 para ambos (nota 5,0: {f(ia[('teto: R_off >= 5.0', 'R_syn_raw')], 3)} para o R_syn em A).

### 7.5 Sensibilidade
{abas("Sensibilidade", "Sensibilidade_mB", "Limite_30_Avaliacoes")}
Ganho de R² do R_syn além da nota oficial no teto (nota = 5,0) e correlação de postos do índice com o desfecho (índice de ocupação) dentro da faixa de nota 5,0, para as seis variantes (shrinkage; com e sem satisfação geral; todos os anúncios ou só os de até 30 avaliações):

{t_sens}

O ρ bruto de {f(sa[(sa['variante'] == 'com_shrinkage') & (sa['bloco'] == 'B: por faixa de R_off') & (sa['escopo'] == 'faixa = 5,0') & (sa['medida'] == 'spearman R_syn × desempenho bruto')]['valor'].iloc[0], 2, True)} com shrinkage é um artefato do encolhimento (seção 7.1); sem ele, e com o desfecho residualizado nos controles, o ρ é próximo de zero em todas as variantes. Excluir a satisfação geral
quase não muda os resultados. O limite de {n(lim['limite de avaliações por anúncio'])} avaliações por anúncio afeta {pc(lim['proporção de anúncios truncados'], 0)} dos anúncios elegíveis ({n(lim['anúncios com mais avaliações que o limite (truncados)'])}), mas só {pc(lim['proporção de truncados entre os de nota 5,0'], 1)} dos de nota 5,0; a confiabilidade do sentimento médio por anúncio é de {f(lim['confiabilidade Spearman-Brown com 30 avaliações'])}
com {n(lim['limite de avaliações por anúncio'])} avaliações, {f(lim['confiabilidade Spearman-Brown com 60 avaliações'])} com 60 e {f(lim['confiabilidade Spearman-Brown com 120 avaliações'])} com 120, e não há deriva temporal relevante (estrelas médias de {f(lim['estrelas médias das 10 avaliações mais recentes'], 3)} nas 10 avaliações mais recentes e {f(lim['estrelas médias das 20 avaliações mais antigas'], 3)} nas 20 mais antigas).

### 7.6 Como ler o resultado
O resultado é nulo e secundário: o índice sintético não acrescenta poder explicativo sobre os índices de volume além da nota oficial, em nenhum dos dois modelos de sentimento. Há duas leituras, que não se excluem. A primeira é que **o sentimento do texto tem pouca razão teórica para prever uma contagem de avaliações**: os desfechos disponíveis são índices de volume (seção 2), e o nulo é em
parte consequência do desfecho que a base permite. A segunda é que **o valor do texto está na decomposição por aspecto da seção 5, e não em substituir a nota**: a nota oficial já resume bem a satisfação geral do hóspede, e o texto acrescenta o porquê. Em nenhum ponto este estudo apresenta o R_syn como "rating melhor".
"""
