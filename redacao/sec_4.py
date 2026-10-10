"""Seção 4 do texto unificado: a medição é confiável?"""
from __future__ import annotations

from doc_base import *  # noqa: F401,F403


def _val(s) -> pd.DataFrame:
    return L(s, "validacao_construto").set_index("aspecto")


def secao4() -> str:
    man = L(sA, "cmp_manual_modelos").set_index("modelo")
    sg = L(sA, "cmp_segundo_anotador_resumo").set_index("medida")
    spa = L(sA, "cmp_segundo_anotador_por_aspecto").set_index("aspecto_anotador1")
    seg_txt = (f"Um segundo anotador rotulou, sem ver as classificações do primeiro nem dos modelos, {n(sg.loc['n frases rotuladas pelos dois', 'valor'])} frases da amostra. A concordância no sentimento é de {pc(sg.loc['sentimento: concordância simples', 'valor'], 0)} (kappa de Cohen {f(sg.loc['sentimento: kappa de Cohen', 'valor'])}, IC {ic(sg.loc['sentimento: kappa de Cohen', 'ic_inf'], sg.loc['sentimento: kappa de Cohen', 'ic_sup'])}; "
               f"kappa ponderado linear {f(sg.loc['sentimento: kappa ponderado linear', 'valor'])}) e, no aspecto, de {pc(sg.loc['aspecto: concordância simples', 'valor'], 0)} (kappa {f(sg.loc['aspecto: kappa de Cohen', 'valor'])}, IC {ic(sg.loc['aspecto: kappa de Cohen', 'ic_inf'], sg.loc['aspecto: kappa de Cohen', 'ic_sup'])}). "
               f"Os dois anotadores concordam bem no sentimento e só moderadamente no aspecto, o que é coerente com a classificação acima: a concordância é baixa justamente em satisfação geral ({pc(spa.loc['satisfacao_geral', 'concordancia'], 0)}, n = {n(spa.loc['satisfacao_geral', 'n'])}, em geral confundida com o grupo geral) e em limpeza ({pc(spa.loc['limpeza', 'concordancia'], 0)}, n = {n(spa.loc['limpeza', 'n'])}), "
               f"e é alta em custo-benefício e precisão do anúncio ({pc(spa.loc['custo_beneficio', 'concordancia'], 0)} nos dois). A amostra de 100 frases é pequena, e as concordâncias por aspecto têm de 4 a 20 frases.")
    pcl = L(sA, "cmp_manual_por_classe")
    idi = L(sA, "cmp_manual_idioma")
    dif = L(sA, "cmp_manual_diferenca")
    regra = L(sA, "cmp_regra_modelo_principal").iloc[0]
    aspt = L(sA, "cmp_manual_aspecto").set_index("medida")
    asp = aspt["valor"]
    pa = L(sA, "cmp_manual_aspecto_por_classe").set_index("aspecto_previsto")
    conc = L(sA, "cmp_concordancia")
    conf = L(sA, "cmp_confusao_polaridade").set_index("ca")
    ca = L(sA, "cmp_concordancia_aspecto").set_index("aspecto")
    D = L(sA, "cmp_descritivas").set_index("modelo")
    va, vb = _val(sA), _val(sB)
    totc = conc[(conc["nivel"] == "sentença") & (conc["grupo"] == "total")].iloc[0]
    tot_a = conc[(conc["nivel"] == "anúncio × aspecto") & (conc["grupo"] == "total")].iloc[0]
    sent_g = {r.grupo: r for r in conc[conc["nivel"] == "sentença"].itertuples()}
    d_tot = dif[(dif["escopo"] == "total")].set_index("medida")
    d_pt = dif[(dif["escopo"] == "só português")].set_index("medida")
    k, ac = "kappa ponderado linear populacional", "acurácia populacional"
    nef = man["n_efetivo_ponderado"].iloc[0]
    idx = idi.set_index(["idioma", "modelo"])
    pt_a, pt_b = idx.loc[("pt", "A")], idx.loc[("pt", "B")]
    cl = pcl.set_index(["modelo", "classe_prevista"])
    lang = L(sA, "lang_dist").set_index("idioma")["prop_avaliacoes"]
    a_pop2 = "acurácia de aspecto ponderada (estratos aspecto × polaridade)"
    a_pop1 = "acurácia de aspecto ponderada (só pela participação do aspecto)"

    t41 = tabela(["Medida", "A", "B"], [
        ["Acurácia na amostra", pc(man.loc["A", "acuracia_amostra"], 1), pc(man.loc["B", "acuracia_amostra"], 1)],
        ["F1 macro na amostra", f(man.loc["A", "f1_macro_amostra"]), f(man.loc["B", "f1_macro_amostra"])],
        ["Kappa de Cohen na amostra", f(man.loc["A", "kappa_amostra"]), f(man.loc["B", "kappa_amostra"])],
        ["Kappa ponderado linear na amostra", f(man.loc["A", "kappa_linear_amostra"]), f(man.loc["B", "kappa_linear_amostra"])],
        ["Spearman, rótulo humano × estrelas esperadas", f(man.loc["A", "spearman_rotulo_estrelas"]), f(man.loc["B", "spearman_rotulo_estrelas"])],
        ["Acurácia ponderada pela população", pc(man.loc["A", "acuracia_populacao"], 1), pc(man.loc["B", "acuracia_populacao"], 1)],
        ["Kappa ponderado pela população", f(man.loc["A", "kappa_populacao"]), f(man.loc["B", "kappa_populacao"])],
        ["Kappa ponderado linear pela população", f(man.loc["A", "kappa_linear_populacao"]), f(man.loc["B", "kappa_linear_populacao"])]])
    t_cl = tabela(["Polaridade prevista", "A: frases", "A: acerto", "B: frases", "B: acerto"],
                  [[c, n(cl.loc[("A", c), "n_previstas"]), pc(cl.loc[("A", c), "acerto"], 1), n(cl.loc[("B", c), "n_previstas"]), pc(cl.loc[("B", c), "acerto"], 1)] for c in ("negativo", "neutro", "positivo")])
    nomes = {"pt": "português", "en": "inglês", "es": "espanhol", "demais": "demais idiomas"}
    t_idi = tabela(["Idioma", "Frases", "A: acurácia (amostra)", "B: acurácia (amostra)", "A: acurácia ponderada", "B: acurácia ponderada"],
                   [[nomes[g], n(idx.loc[(g, "A"), "n"]), pc(idx.loc[(g, "A"), "acuracia_amostra"], 1), pc(idx.loc[(g, "B"), "acuracia_amostra"], 1),
                     pc(idx.loc[(g, "A"), "acuracia_ponderada"], 1), pc(idx.loc[(g, "B"), "acuracia_ponderada"], 1)] for g in ("pt", "en", "es", "demais")])
    t_asp = tabela(["Aspecto previsto", "Frases rotuladas", "Precisão da atribuição"],
                   [[ROT.get(a, "Fora do perfil (`geral`)"), n(pa.loc[a, "n"]), pc(pa.loc[a, "precisao"], 0)] for a in sorted(pa.index, key=lambda a: -pa.loc[a, "precisao"])])

    t42 = tabela(["Nível", "Grupo", "n", "Spearman das estrelas", "Pearson das estrelas", "Kappa linear das polaridades"],
                 [[r.nivel, r.grupo, n(r.n), f(r.spearman_estrelas), f(r.pearson_estrelas), f(r.kappa_ponderado_linear_polaridade)] for r in conc.itertuples()], "|---|---|---:|---:|---:|---:|")
    mx, mn = ca["spearman_estrelas"].idxmax(), ca["spearman_estrelas"].idxmin()

    linhas = [[ROT[a], SUB[a], n(va.loc[a, "n"]), f(va.loc[a, "spearman"]), f(va.loc[a, "pearson"]), f(vb.loc[a, "spearman"]), f(vb.loc[a, "pearson"])] for a in ASP if a in va.index]
    t_val = tabela(["Aspecto", "Subnota", "n", "Spearman (A)", "Pearson (A)", "Spearman (B)", "Pearson (B)"], linhas, "|---|---|---:|---:|---:|---:|---:|")
    vol_a = L(sA, "val_volume")
    k30, kk = "v ≤ 30 (sentimento usa todas as avaliações)", "v > 30 (só as 30 mais recentes)"
    pva = vol_a[vol_a["faixa"].isin([k30, kk])].pivot_table(index="aspecto", columns="faixa", values="spearman")
    dmax = (pva[k30] - pva[kk]).abs()
    conv_a, conv_b = L(sA, "val_convergente").set_index("aspecto"), L(sB, "val_convergente").set_index("aspecto")
    auc_a, auc_b = L(sA, "val_auc_kendall").set_index("aspecto"), L(sB, "val_auc_kendall").set_index("aspecto")
    ac_col = "AUC(sentimento maior quando subnota=5)"
    rel_a, rel_b = L(sA, "val_confiabilidade").set_index("aspecto"), L(sB, "val_confiabilidade").set_index("aspecto")
    rec_a = L(sA, "val_recortes")
    rg = rec_a[rec_a["recorte"].str.startswith("idioma")]["spearman"]
    rt = rec_a[rec_a["recorte"].str.startswith("tipo")]["spearman"]
    prim_a = int((conv_a["posto_da_correspondente(1=maior)"] == 1).sum())
    prim_b = int((conv_b["posto_da_correspondente(1=maior)"] == 1).sum())
    pcol = "spearman_parcial_controlando_nota_global"
    rcol = "spearman_corrigido_atenuacao_lado_sentimento"

    lc = L(sA, "lda_concordancia_sentencas").set_index("medida")["valor"]
    lp = L(sA, "lda_perfil_correlacao").dropna(subset=["spearman_perfil_bertopic_lda"]).set_index("aspecto")
    lv = L(sA, "lda_validade").dropna(subset=["spearman_lda"]).set_index("aspecto")
    li = L(sA, "lda_importancia_comparacao").set_index("aspecto")
    rho_l = float(metrica("etapa23", "spearman_ordenacao_importancia"))
    mapa = L(sA, "lda_shared_mapa")
    t_lda = tabela(["Aspecto (LDA)", "Spearman do perfil BERTopic × LDA", "Spearman com a subnota (LDA)", "Spearman com a subnota (BERTopic)", "Parcela do R² (LDA)", "Parcela do R² (BERTopic)"],
                   [[ROT[a], f(lp.loc[a, "spearman_perfil_bertopic_lda"]), f(lv.loc[a, "spearman_lda"]) if a in lv.index else "— (sem subnota)", f(lv.loc[a, "spearman_bertopic"]) if a in lv.index else "—",
                     pc(li.loc[a, "lda"], 1), pc(li.loc[a, "bertopic_mesmos_aspectos"], 1)] for a in lp.index])
    mapeados = mapa[mapa["mapeamento_provisorio"] != "misto"]

    rows, conf_ok = [], []
    for a in ASP:
        prec = pa.loc[a, "precisao"] if a in pa.index else np.nan
        tem = a in SUB
        ra_, rb_ = (va.loc[a, "spearman"], vb.loc[a, "spearman"]) if tem else (np.nan, np.nan)
        ok = bool(tem and prec >= 0.60 and ra_ >= 0.20 and rb_ >= 0.20)
        if ok:
            motivo = "precisão ≥ 0,60 e correlação ≥ 0,20 com a subnota nos dois modelos"
        elif not tem:
            motivo = "sem subnota correspondente: não validável"
        elif prec < 0.60:
            motivo = "precisão de atribuição < 0,60"
        else:
            motivo = "correlação < 0,20 com a subnota em ao menos um modelo"
        if ok:
            conf_ok.append(a)
        rows.append([ROT[a], pc(prec, 0), f(ra_) if tem else "—", f(rb_) if tem else "—", "confiável" if ok else "cautela", motivo])
    t_cls = tabela(["Aspecto", "Precisão da atribuição (amostra)", "Spearman com a subnota (A)", "Spearman com a subnota (B)", "Classificação", "Critério"], rows, "|---|---:|---:|---:|---|---|")
    caut = [ROT[a] for a in ASP if a not in conf_ok]
    ic_lo, ic_hi = aspt.loc[a_pop2, "ic_inf"], aspt.loc[a_pop2, "ic_sup"]

    return f"""## 4. A medição é confiável?
{abas("Avaliacao_Rotuladas_AB", "Aspecto_Rotuladas", "Comparacao_Sentimento_AB", "Diferenca_B_menos_A", "Config", "Validacao_Construto", "LadoALado_validacao_construto", "Val_Volume_Convergente", "Val_Confiab_AUC", "Val_Recortes", "Checagem_LDA")}
A seção 3 define como o texto é medido; antes de usar essas medidas para dizer algo sobre a nota, é preciso saber o quanto elas merecem confiança. Esta seção busca a resposta em cinco tipos de evidência, da mais direta à mais indireta:
frases rotuladas por um pesquisador, concordância entre os dois modelos, uma regra pré-registrada para escolher o modelo principal, concordância com as subnotas oficiais e uma checagem com um método de tópicos diferente. Fecha classificando
cada aspecto, e as seções seguintes respeitam essa classificação.

### 4.1 Evidência direta: frases rotuladas
{abas("Avaliacao_Rotuladas_AB", "Aspecto_Rotuladas", "Resumo_AB")}
O pesquisador rotulou, sem ver as classificações automáticas, {n(man.loc['A', 'n'])} frases: sentimento (negativo, neutro ou positivo) e aspecto principal. A amostra foi estratificada pelo aspecto e pela polaridade previstos pelo modelo A (cerca de um terço de frases
de cada polaridade por aspecto) e, portanto, é **rica em frases difíceis**: no corpus, {pc(D.loc['A', 'prop_sentencas_positiva'], 1)} das sentenças são positivas segundo A. Por isso há duas leituras de cada métrica: na amostra, e ponderada pela população, em que cada frase pesa o
tamanho do seu estrato original (aspecto × polaridade previstos por A); os pesos são os mesmos para A e B, e o tamanho efetivo da amostra ponderada é de apenas {f(nef, 0)} frases, de modo que os intervalos são largos.

{t41}

Para os dois modelos o erro mais comum é classificar como neutras frases que o pesquisador considera positivas: quando A prevê "positivo" acerta {pc(cl.loc[('A', 'positivo'), 'acerto'], 1)}, mas quando prevê "neutro" acerta apenas {pc(cl.loc[('A', 'neutro'), 'acerto'], 1)}. B classifica
mais frases como positivas ({n(cl.loc[('B', 'positivo'), 'n_previstas'])} contra {n(cl.loc[('A', 'positivo'), 'n_previstas'])} de {n(man.loc['A', 'n'])}) e acerta menos nas previstas como neutras e negativas:

{t_cl}

A amostra e a população **discordam sobre qual modelo é melhor**, e é preciso descrever as duas. Na amostra, B tem acurácia maior ({pc(man.loc['B', 'acuracia_amostra'], 1)} contra {pc(man.loc['A', 'acuracia_amostra'], 1)}; em português, {pc(pt_b['acuracia_amostra'], 1)} contra {pc(pt_a['acuracia_amostra'], 1)}),
porque a amostra foi construída a partir das previsões de A e concentra as frases em que A erra (as que A chama de neutras). Ponderando pela população, A é melhor: a acurácia é {pc(man.loc['A', 'acuracia_populacao'], 1)} contra {pc(man.loc['B', 'acuracia_populacao'], 1)} e o kappa ponderado linear é
{f(man.loc['A', 'kappa_linear_populacao'])} contra {f(man.loc['B', 'kappa_linear_populacao'])}. Por idioma:

{t_idi}

O português, idioma de {pc(lang['pt'], 0)} das avaliações, é o de menor acerto na amostra para o modelo A.

**Aspecto.** A atribuição de aspecto não depende do modelo de sentimento. Acerta {pc(asp['acurácia de aspecto na amostra'], 1)} na amostra (kappa {f(asp['kappa de Cohen do aspecto na amostra'])}); ponderando só pela participação de cada aspecto no corpus a estimativa é
{pc(asp[a_pop1], 0)}, e com os estratos aspecto × polaridade, {pc(asp[a_pop2], 0)} (IC 95% por bootstrap [{f(100 * ic_lo, 0)}%; {f(100 * ic_hi, 0)}%]), uma estimativa instável (células com poucas frases e pesos muito desiguais): lida na população, a acurácia de aspecto fica
**entre {pc(asp[a_pop1], 0)} e {pc(asp[a_pop2], 0)}**. O acerto é parecido nas três polaridades previstas ({pc(asp['acurácia de aspecto na amostra, polaridade prevista neg'], 0)}, {pc(asp['acurácia de aspecto na amostra, polaridade prevista neu'], 0)} e {pc(asp['acurácia de aspecto na amostra, polaridade prevista pos'], 0)}), mas muito diferente conforme o tópico:
{pc(asp['acurácia de aspecto, tópico direto'], 0)} nas frases de tópico direto ({n(aspt.loc['acurácia de aspecto, tópico direto', 'n'])}) e {pc(asp['acurácia de aspecto, tópico reatribuído (outlier)'], 0)} nas de tópico reatribuído por similaridade ({n(aspt.loc['acurácia de aspecto, tópico reatribuído (outlier)', 'n'])}).
A precisão varia muito entre aspectos, com cerca de 27 frases rotuladas por aspecto (intervalos de ±0,18):

{t_asp}

### 4.2 Concordância entre os dois modelos
{abas("Comparacao_Sentimento_AB")}
Com a evidência direta limitada a 297 frases, o corpus inteiro permite comparar os modelos entre si. Nas {n(totc['n'])} sentenças, a correlação de postos das estrelas esperadas de A e B é {f(totc['spearman_estrelas'])} e o kappa ponderado linear das
polaridades é {f(totc['kappa_ponderado_linear_polaridade'])}; por idioma, o kappa é {f(sent_g['pt'].kappa_ponderado_linear_polaridade)} em português, {f(sent_g['en'].kappa_ponderado_linear_polaridade)} em inglês e {f(sent_g['es'].kappa_ponderado_linear_polaridade)} em espanhol. No nível anúncio × aspecto,
a concordância é maior ({f(tot_a['spearman_estrelas'])} de Spearman; kappa {f(tot_a['kappa_ponderado_linear_polaridade'])}), porque a média de várias frases reduz o ruído: varia de {f(ca.loc[mn, 'spearman_estrelas'])} ({ROT[mn]}) a {f(ca.loc[mx, 'spearman_estrelas'])} ({ROT[mx]}). Os dois modelos ordenam as frases e os
anúncios de modo semelhante, mas não são intercambiáveis: das {n(conf.loc['A positivo'].sum())} sentenças que A chama de positivas, B concorda em {n(conf.loc['A positivo', 'B positivo'])}; das {n(conf.loc['A neutro'].sum())} que A chama de neutras, B chama {n(conf.loc['A neutro', 'B positivo'])} de positivas. Concordância completa:

{t42}

### 4.3 Regra pré-registrada e modelo principal
{abas("Diferenca_B_menos_A", "Config")}
Antes de rodar o modelo B, registramos a regra de escolha do modelo principal: **B seria o principal se o intervalo de 95% (bootstrap estratificado) da diferença B − A no kappa ponderado linear populacional de sentimento excluísse zero a favor de B; caso contrário, o principal seria A**,
com o outro modelo sempre reportado como robustez. O resultado: a diferença B − A é {f(regra['diferenca_B_menos_A'], 3)} (IC 95% {ic(regra['ic_inf'], regra['ic_sup'], 3)}), isto é, o intervalo exclui zero, mas **a favor de A**. Pela regra, o modelo principal é **{regra['modelo_principal']}**. Na acurácia populacional a diferença é
{f(d_tot.loc[ac, 'B_menos_A'], 3)} {ic(d_tot.loc[ac, 'dif_ic_inf'], d_tot.loc[ac, 'dif_ic_sup'], 3)}, e só em português, no kappa ponderado linear, {f(d_pt.loc[k, 'B_menos_A'], 3)} {ic(d_pt.loc[k, 'dif_ic_inf'], d_pt.loc[k, 'dif_ic_sup'], 3)}, intervalo que inclui zero. A seção 4.1 mostra
por que a escolha não é óbvia (B é melhor na amostra, A na população); a regra foi fixada antes de ver os resultados justamente para não escolher o resultado mais conveniente. Daqui em diante o modelo principal é A, e os resultados de B aparecem lado a lado nas abas com sufixo `_mB` e nas abas `LadoALado_*`.

### 4.4 Validade de construto: concordância com as subnotas oficiais
{abas("Validacao_Construto", "LadoALado_validacao_construto", "Val_Volume_Convergente", "Val_Confiab_AUC", "Val_Recortes")}
A evidência indireta mais importante é a concordância com as subnotas que os próprios hóspedes deram. Para cada aspecto com subnota correspondente, correlacionamos, no nível do anúncio, o sentimento do aspecto com a subnota (não há limiar de aprovação; interessam a força e o sinal),
e a satisfação geral com a nota global:

{t_val}

Todos os coeficientes são positivos e significativos nos dois modelos; a concordância é moderada, de {f(va['spearman'].min())} a {f(va['spearman'].max())} em A e de {f(vb['spearman'].min())} a {f(vb['spearman'].max())} em B, sem um modelo sistematicamente melhor (B é um pouco maior em check-in e comunicação; A, em limpeza,
custo-benefício e, sobretudo, satisfação geral). Ela deve ser lida à luz de que as subnotas também são comprimidas (muitos empates em 5,0), o que atenua as correlações. Cinco verificações de robustez:

- **Por volume de avaliações.** No modelo A, a concordância dos anúncios com até 30 avaliações (em que o sentimento usa todas) difere da dos anúncios com mais de 30 em no máximo {f(dmax.max())} ({ROT[dmax.idxmax()]}), sem padrão sistemático; em B o resultado é análogo.
- **Convergente e discriminante.** A subnota correspondente é a mais correlacionada com o aspecto em {n(prim_a)} de 7 casos em A e em {n(prim_b)} de 7 em B (nos demais fica em segundo ou terceiro lugar, porque as subnotas são muito correlacionadas entre si, o chamado efeito halo). Controlando a nota global
  (correlação parcial), resta informação específica em limpeza ({f(conv_a.loc['limpeza', pcol])}), localização ({f(conv_a.loc['localizacao', pcol])}), check-in ({f(conv_a.loc['checkin', pcol])}) e comunicação ({f(conv_a.loc['comunicacao', pcol])}), e quase nenhuma em custo-benefício ({f(conv_a.loc['custo_beneficio', pcol])}) e precisão ({f(conv_a.loc['precisao', pcol])}).
- **Subnotas saturadas.** A probabilidade de o sentimento ser maior nos anúncios de subnota 5 do que nos de subnota menor (AUC) vai de {f(auc_a[ac_col].min())} a {f(auc_a[ac_col].max())} em A e de {f(auc_b[ac_col].min())} a {f(auc_b[ac_col].max())} em B.
- **Idioma e tipo de acomodação.** No modelo A, as correlações são positivas em português, inglês e espanhol (de {f(rg.min())} a {f(rg.max())}) e em casa/apartamento inteiro e quarto privado (de {f(rt.min())} a {f(rt.max())}), o que sustenta o uso de modelos multilíngues.
- **Atenuação.** A confiabilidade split-half do sentimento por aspecto (metades das avaliações de cada anúncio, com Spearman-Brown) é baixa: de {f(rel_a['confiabilidade_SB'].min())} a {f(rel_a['confiabilidade_SB'].max())} em A e de {f(rel_b['confiabilidade_SB'].min())} a {f(rel_b['confiabilidade_SB'].max())} em B. Correlações corrigidas por essa atenuação
  (de {f(rel_a[rcol].min())} a {f(rel_a[rcol].max())} em A; em B, até {f(rel_b[rcol].max())}) são apenas ilustrativas, porque com confiabilidades tão baixas a correção é instável e corrige só o lado do sentimento.

### 4.5 Checagem com um segundo método de tópicos (LDA)
{abas("Checagem_LDA", "Topicos_LDA")}
Para saber se os resultados por aspecto dependem do método de tópicos, atribuímos cada sentença ao tópico dominante do LDA ({n(len(mapa))} tópicos) e comparamos. O mapa tópico LDA → aspecto foi **confirmado pelo pesquisador** (`data/mapa_lda_para_confirmar.xlsx`, sem alterações): só recebe aspecto o tópico cuja leitura das palavras de maior peso, aspecto mais similar aos termos-semente
e margem entre o primeiro e o segundo aspecto (≥ 0,05) concordam; senão é "misto" e fica fora do perfil. Apenas {n(len(mapeados))} dos {n(len(mapa))} tópicos receberam aspecto (comodidades, comunicação, satisfação geral e localização), e {pc(lc['prop_sentencas_misto_no_lda'], 0)} das sentenças caem em tópicos mistos, de modo que o LDA só permite checar esses quatro aspectos.
Entre as sentenças com aspecto nos dois métodos, {pc(lc['prop_mesmo_aspecto_entre_as_com_aspecto_nos_dois'], 1)} recebem o mesmo aspecto.

{t_lda}

O sinal da validade de construto se mantém nos três aspectos que têm subnota (localização, comunicação e satisfação geral), com correlações do mesmo tamanho nos dois mais específicos e menores em satisfação geral. Na decomposição do R² da nota global, comodidades fica em primeiro nos dois métodos; satisfação geral e comunicação trocam de posição (correlação de postos {f(rho_l)}, com apenas quatro aspectos).

### 4.6 O que é confiável e o que pede cautela
{abas("Aspecto_Rotuladas", "Validacao_Construto", "LadoALado_validacao_construto", "Segundo_Anotador")}
Resumindo as evidências, classificamos cada aspecto com um critério descritivo, fixado antes das seções seguintes: **confiável** se a precisão de atribuição na amostra é de ao menos 0,60 e a correlação com a subnota correspondente é de ao menos 0,20 nos dois modelos; **cautela** nos demais casos.

{t_cls}

São confiáveis: {', '.join(ROT[a] for a in conf_ok)}. Pedem cautela: {', '.join(caut)}. Duas consequências valem para as seções 5 a 7. Primeiro, o aspecto de maior peso na seção 5, comodidades, pede cautela (atribuição imprecisa e sem subnota para validar); por isso a leitura prática da seção 5 se apoia nos tópicos finos de queixa e
elogio, cuja atribuição é melhor (tópicos diretos, {pc(asp['acurácia de aspecto, tópico direto'], 0)} de acerto de aspecto), e os pesos por aspecto são apresentados como indicativos. Segundo, nenhum resultado por aspecto deve ser lido sem a classificação ao lado. {seg_txt}
"""
