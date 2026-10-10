"""Seções 8 a 10 do texto unificado: sazonalidade exploratória; limitações; conclusões."""
from __future__ import annotations

from doc_base import *  # noqa: F401,F403
from sec_5_7 import classificar  # noqa: E402

EV = {"carnaval": "Carnaval", "reveillon": "Réveillon", "semana_santa": "Semana Santa", "rock_in_rio": "Rock in Rio", "corpus_christi": "Corpus Christi",
      "todo_mundo_no_rio": "Todo Mundo no Rio (2024)", "feriado_curto": "Feriados curtos"}
ORDEM = ["rock_in_rio", "corpus_christi", "reveillon", "todo_mundo_no_rio", "carnaval", "semana_santa", "feriado_curto"]


def _neg(df):
    return df[df["medida"].str.startswith("propor")]


def secao8() -> str:
    V = L(sA, "sazon_volume")
    v14, v7 = V[V["defasagem"] == 14].set_index("evento"), V[V["defasagem"] == 7].set_index("evento")
    t_v = tabela(["Evento", "Defasagem 14 dias [IC 95%]", "Defasagem 7 dias [IC 95%]"], [[EV[e], f"{f(v14.loc[e, 'razao'])} {ic(v14.loc[e, 'ic_inf'], v14.loc[e, 'ic_sup'])}", f"{f(v7.loc[e, 'razao'])} {ic(v7.loc[e, 'ic_inf'], v7.loc[e, 'ic_sup'])}"] for e in ORDEM], "|---|---|---|")
    NA, NB = L(sA, "sazon_negativa_geral"), L(sB, "sazon_negativa_geral")
    na, nb = NA[NA["defasagem"] == 14].set_index("evento"), NB[NB["defasagem"] == 14].set_index("evento")
    t_n = tabela(["Evento", "Razão de chances de frase negativa (A) [IC 95%]", "q (A)", "Razão de chances (B) [IC 95%]", "q (B)"],
                 [[EV[e], f"{f(na.loc[e, 'razao'])} {ic(na.loc[e, 'ic_inf'], na.loc[e, 'ic_sup'])}", f(na.loc[e, "q_BH"], 3), f"{f(nb.loc[e, 'razao'])} {ic(nb.loc[e, 'ic_inf'], nb.loc[e, 'ic_sup'])}", f(nb.loc[e, "q_BH"], 3)] for e in ORDEM], "|---|---|---:|---|---:|")
    sig_a = [EV[e] for e in ORDEM if na.loc[e, "q_BH"] < 0.05]
    sig_b = [EV[e] for e in ORDEM if nb.loc[e, "q_BH"] < 0.05]
    AA = _neg(L(sA, "sazon_aspecto"))
    BB = _neg(L(sB, "sazon_aspecto"))
    AA, BB = AA[AA["defasagem"] == 14], BB[BB["defasagem"] == 14]
    m = AA.merge(BB, on=["evento", "aspecto"], suffixes=("_A", "_B"))
    sa, sb = m["q_BH_A"] < 0.05, m["q_BH_B"] < 0.05
    mesmo = (m["razao_A"] > 1) == (m["razao_B"] > 1)
    ambos = m[sa & sb & mesmo]
    soA, soB = m[sa & ~sb], m[sb & ~sa]
    opostos = m[sa & sb & ~mesmo]
    t_ab = tabela(["Evento", "Aspecto", "Razão de chances (A) [IC]", "Razão de chances (B) [IC]"],
                  [[EV[r.evento], ROT[r.aspecto], f"{f(r.razao_A)} {ic(r.ic_inf_A, r.ic_sup_A)}", f"{f(r.razao_B)} {ic(r.ic_inf_B, r.ic_sup_B)}"] for r in ambos.itertuples()], "|---|---|---|---|")
    cr = L(sA, "cmp_ladoalado_sazon_criterio").set_index("evento")
    cb_a = [EV[e] for e in ORDEM if cr.loc[e, "criterio_b_conteudo__A"]]
    cb_b = [EV[e] for e in ORDEM if cr.loc[e, "criterio_b_conteudo__B"]]
    ex_a = soA[soA["evento"] == "carnaval"]
    ex_txt = "; ".join(f"{ROT[r.aspecto]} (razão de chances {f(r.razao_A)} em A e {f(r.razao_B)} em B)" for r in ex_a.itertuples())
    return f"""## 8. Sazonalidade e eventos (análise exploratória)
{abas("Sazon_Volume", "Sazon_NegativaGeral", "Sazon_NegativaGeral_mB", "Sazon_Criterio", "Sazon_Criterio_mB", "LadoALado_sazon_aspecto", "LadoALado_sazon_criterio", "Config")}
Esta seção é **exploratória** e vem depois das demais porque não sustenta nenhuma conclusão das seções 5 a 7; ela mostra uma aplicação do mesmo texto a uma pergunta diferente, a de como o conteúdo das avaliações muda em períodos de grande procura. Três limitações valem para tudo o que segue. A data da avaliação não é a da estadia (as avaliações foram atribuídas a cada evento por uma janela entre o
dia seguinte ao início da estadia e 14 dias depois do fim, prazo máximo para avaliar), de modo que há erro de atribuição. Os dados só incluem avaliações de anúncios ainda ativos na coleta, e os anos mais antigos ficam sub-representados. Os eventos têm poucas edições dentro do período (o *Todo Mundo no Rio* tem uma, e o conteúdo do Carnaval vem de duas). O plano e os critérios foram congelados antes dos resultados (histórico de decisões), mas a
comparação de conteúdo por aspecto e por tópico envolve muitos testes, corrigidos por Benjamini-Hochberg, e deve ser lida como geração de hipóteses.

### 8.1 Volume de avaliações
A medida é o volume diário de **avaliações escritas** na janela do evento em relação ao de dias comuns do mesmo ano-mês (GLM de Poisson com efeitos fixos de ano-mês e dia da semana, erro-padrão robusto HAC; 2020 e 2021 excluídos). Ela indica estadias que terminaram no período, e **não** a ocupação dos imóveis. Em todos os eventos o volume é maior do que em dias comuns:

{t_v}

A defasagem de 7 dias dá razões maiores porque considera só os dias logo após o check-out, onde o efeito se concentra; a de 14 dias inclui mais dias comuns. No *Todo Mundo no Rio*, o limite inferior com 14 dias fica praticamente em 1, e a evidência é mais fraca.

### 8.2 Tom geral das avaliações: não replica entre os modelos
Em uma checagem exploratória (binomial diário, janelas de 14 dias), a proporção de frases negativas no corpus inteiro nas janelas de evento, em relação a dias comuns, é menor em {', '.join(sig_a) if sig_a else 'nenhum evento'} com o modelo A. Com o modelo B, o resultado não aparece (eventos com q < 0,05: {', '.join(sig_b) if sig_b else 'nenhum'}):

{t_n}

Portanto, a menor proporção de frases negativas nos eventos de música **depende do modelo de sentimento** e não deve ser tratada como achado; a interpretação que havíamos aventado (público mais jovem e tolerante a ruído) fica sem sustentação empírica neste ponto. O modelo B classifica mais frases como positivas que o A (seção 4.2), e é plausível que a diferença entre janelas dependa do limiar entre neutro e negativo.

### 8.3 Conteúdo por aspecto
Para cada evento e aspecto, comparou-se a proporção de frases negativas dentro do aspecto com a de dias comuns (razão de chances; janelas de 14 dias; {n(len(m))} combinações). Com q < 0,05, {n(sa.sum())} combinações aparecem em A e {n(sb.sum())} em B; **só {n(len(ambos))} aparecem nos dois com o mesmo sentido**, {n(len(opostos))} com sentidos opostos, {n(len(soA))} apenas em A e {n(len(soB))} apenas em B. As que coincidem:

{t_ab}

Por exemplo, os aumentos de queixa no Carnaval que aparecem só em A: {ex_txt or 'nenhum'}. O critério de conteúdo definido de antemão (ao menos um aspecto ou tópico com aumento de queixa relevante e significativo) é satisfeito em {', '.join(cb_a) if cb_a else 'nenhum evento'} com A e em {', '.join(cb_b) if cb_b else 'nenhum evento'} com B: o conteúdo é **sensível ao modelo**, e só as combinações da tabela acima podem ser tomadas como indicativas.
"""


def secao9() -> str:
    lim = L(sA, "limite30").set_index("medida")["valor"]
    md = L(sA, "cmp_manual_diferenca").set_index(["escopo", "medida"])
    ne = int(round(float(L(sA, "cmp_manual_aspecto").set_index("medida").loc["tamanho efetivo da amostra ponderada", "valor"]))) if "tamanho efetivo da amostra ponderada" in L(sA, "cmp_manual_aspecto").set_index("medida").index else 72
    sv = L(sA, "validacao_construto")
    seg = L(sA, "cmp_segundo_anotador_resumo").set_index("medida")["valor"]
    return f"""## 9. Limitações
{abas("Config", "Estat_Corpus", "Limite_30_Avaliacoes", "Avaliacao_Rotuladas_AB", "Aspecto_Rotuladas", "Val_Confiab_AUC", "Checagem_LDA", "Segundo_Anotador")}
Reunimos aqui o que limita a leitura de todo o texto, na ordem das seções.

- **Recorte do corpus (seção 1).** O sentimento usa as {n(lim['limite de avaliações por anúncio'])} avaliações mais recentes de cada anúncio; {pc(lim['proporção de anúncios truncados'], 0)} dos anúncios elegíveis ({n(lim['anúncios com mais avaliações que o limite (truncados)'])}) têm mais avaliações que o limite. O truncamento afeta pouco os de nota 5,0 ({pc(lim['proporção de truncados entre os de nota 5,0'], 1)}), mas reduz a confiabilidade do sentimento médio por anúncio (Spearman-Brown de {f(lim['confiabilidade Spearman-Brown com 30 avaliações'])} com 30 avaliações).
  Os dados só têm anúncios ativos na coleta, e as avaliações não indicam a data da estadia.
- **Desfechos (seção 2).** Não há ocupação nem receita observadas; os campos disponíveis são funções do número de avaliações recentes. Nenhum resultado fala de desempenho econômico.
- **Medição do texto (seções 3 e 4).** Os rótulos de referência vêm de um único pesquisador, que também revisou o mapa de tópicos para aspectos; um segundo anotador rotulou 100 frases (seção 4.6), com concordância moderada no aspecto (kappa {f(seg["aspecto: kappa de Cohen"], 2)}), de modo que a atribuição de aspecto tem erro de rotulagem além do erro do modelo. A amostra rotulada tem 297 frases e, ponderada pela população, tamanho efetivo de cerca de {n(ne)} frases, de modo que os intervalos são largos e as
  comparações entre modelos são frágeis (a diferença de kappa B − A é de {f(md.loc[('total', 'kappa ponderado linear populacional'), 'B_menos_A'], 3)}, com IC que mal exclui zero). A confiabilidade split-half do sentimento por aspecto é baixa, e as subnotas oficiais usadas como referência são comprimidas. Sete dos dez aspectos pedem cautela (seção 4.6); em especial, comodidades, o aspecto de maior peso,
  tem atribuição imprecisa e não tem subnota para validar. O mapa do LDA é **provisório** e depende de confirmação do pesquisador; o LDA só checa quatro aspectos.
- **Dois modelos de sentimento (seção 4).** O modelo A é o principal por uma regra fixada antes da execução do B, mas B é melhor na amostra rotulada e A na população; a escolha não é óbvia, e por isso os resultados de B acompanham todos os blocos. Onde os dois divergem (seções 7.3 e 8), as duas leituras são relatadas sem preferência.
- **Importância dos aspectos (seção 5).** A importância relativa de um aspecto mistura efeito e confiabilidade da medida, e as associações com a nota são entre anúncios, não dentro do anúncio; nada disso autoriza falar em causa. Anúncios sem aspectos suficientes têm sentimento imputado.
- **Índice sintético (seção 7).** Só {n(L(sA, 'cmp_selecao_teto').set_index(['variavel', 'categoria']).loc[('number_of_reviews', '(numérica)'), 'n_com_Rsyn'])} dos anúncios de nota 5,0 têm o índice, e os que ficam de fora têm menos avaliações; as conclusões sobre o teto valem para esse subconjunto. A decisão de não aplicar shrinkage foi tomada depois de ver o resultado com shrinkage. Coeficientes dentro da amostra não são robustos e não foram confirmados fora dela.
- **Sazonalidade (seção 8).** Exploratória, com poucas edições por evento e conteúdo sensível ao modelo; o feriado municipal de São Sebastião (20 de janeiro) foi confirmado pelo pesquisador e entra com janela de 19 a 21 de janeiro.
- **Generalização.** Um só município, uma só plataforma e uma só coleta.
"""


def secao10() -> str:
    seg = L(sA, "cmp_segundo_anotador_resumo").set_index("medida")["valor"]
    cls = classificar()
    LA, LB = L(sA, "imp_lmg"), L(sB, "imp_lmg")
    ng = "nota_global (review_scores_rating)"
    a, b = LA[LA["alvo"] == ng].set_index("aspecto"), LB[LB["alvo"] == ng].set_index("aspecto")
    md = L(sA, "cmp_manual_diferenca").set_index(["escopo", "medida"])
    ac = md.loc[("total", "acurácia populacional")] if ("total", "acurácia populacional") in md.index else md.iloc[0]
    kp = md.loc[("total", "kappa ponderado linear populacional")]
    Ra, Rb = L(sA, "cmp_rsyn_resumo").set_index("medida")["A"], L(sA, "cmp_rsyn_resumo").set_index("medida")["B"]
    qA, qB = L(sA, "imp_topicos_queixas"), L(sB, "imp_topicos_queixas")
    qa15 = qA[(qA["q_BH"] < 0.05) & (qA["efeito_pontos_percentil_nota"] < 0)].head(15)
    qb15 = qB[(qB["q_BH"] < 0.05) & (qB["efeito_pontos_percentil_nota"] < 0)].head(15)
    comum = len(set(qa15["topic"]) & set(qb15["topic"]))
    conf = [ROT[x] for x in ASP if cls[x] == "confiável"]
    ctl = [ROT[x] for x in ASP if cls[x] != "confiável"]
    sel = L(sA, "cmp_selecao_teto").set_index(["variavel", "categoria"])
    n5 = sel.loc[("number_of_reviews", "(numérica)"), "n_com_Rsyn"] + sel.loc[("number_of_reviews", "(numérica)"), "n_sem_Rsyn"]
    return f"""## 10. Conclusões
{abas("Avaliacao_Rotuladas_AB", "Diferenca_B_menos_A", "Validacao_Construto", "Checagem_LDA", "Segundo_Anotador", "Imp_Aspectos", "LadoALado_imp_lmg", "Imp_Topicos_Queixas", "RSyn_Resumo_AB", "Selecao_Teto", "Analise_A", "Comparacoes_Multiplas", "Sazon_Volume", "Config")}
As conclusões seguem a ordem da linha de raciocínio. Todas são associações, e todas valem com as ressalvas da seção 9.

1. **A medição do texto é utilizável, com restrições.** Em 297 frases rotuladas por um pesquisador, a acurácia populacional do sentimento é de {pc(ac['A'], 0)} no modelo A e {pc(ac['B'], 0)} no B, e o kappa ponderado populacional é {f(kp['A'], 2)} e {f(kp['B'], 2)}. Pela regra fixada antes da execução do B (diferença de kappa B − A de {f(kp['B_menos_A'], 3)}, IC {ic(kp['dif_ic_inf'], kp['dif_ic_sup'], 3)}), o modelo principal é A, e B acompanha todos os resultados. Os dois modelos concordam em ordenar
   frases e anúncios, mas não são intercambiáveis. O sentimento dos aspectos concorda com as subnotas oficiais de forma moderada e positiva; só {', '.join(conf)} satisfazem o critério de confiança da seção 4.6, e {', '.join(ctl)} pedem cautela. Um segundo método de tópicos (LDA, mapa provisório) reproduz o sinal nos aspectos que consegue checar. Entre dois anotadores, a concordância é alta no sentimento (kappa {f(seg["sentimento: kappa de Cohen"], 2)}) e moderada no aspecto ({f(seg["aspecto: kappa de Cohen"], 2)}).
2. **O texto das avaliações revela o que se associa à nota.** Nos dois modelos, comodidades é o aspecto de maior parcela do R² da nota global ({pc(a.loc['comodidades', 'parcela_do_R2'], 0)} em A e {pc(b.loc['comodidades', 'parcela_do_R2'], 0)} em B), seguida de limpeza ({pc(a.loc['limpeza', 'parcela_do_R2'], 0)} e {pc(b.loc['limpeza', 'parcela_do_R2'], 0)}), e isso se mantém em todos os segmentos e sensibilidades.
   Como comodidades pede cautela, a leitura que mais se sustenta é a dos tópicos finos: {n(comum)} das 15 queixas de maior peso são as mesmas nos dois modelos (banheiro e chuveiro, ar-condicionado, sujeira, cozinha, cheiro, cama, wi-Fi, resposta do anfitrião), associadas a quedas de 10 a 26 pontos no percentil da nota.
3. **A decomposição é aplicável ao anúncio.** O diagnóstico por anúncio (seção 6) compara cada aspecto com anúncios do mesmo bairro e tipo, mostra a evidência de cada um e as queixas e elogios recorrentes, e indica onde investigar, sem prever nota nem prescrever causas.
4. **Um índice único não acrescenta poder explicativo.** O índice sintético reordena os anúncios em relação à nota oficial e discrimina os anúncios de nota 5,0 que o têm ({n(Ra['anuncios_nota_5_com_R_syn'])} de {n(n5)}), mas não acrescenta poder explicativo sobre os índices de volume além da nota oficial, em nenhum dos dois modelos. O resultado é nulo e secundário, com duas leituras que não se excluem: o sentimento tem pouca razão teórica para
   prever uma contagem de avaliações, e o valor do texto está na decomposição por aspecto. Os coeficientes dentro da amostra não são robustos e ficam fora desta síntese.

O que o estudo **não** conclui: que o índice sintético seja um "rating melhor", que consertar um problema aponte para aumento de nota, que haja efeito sobre receita ou ocupação, ou que os eventos alterem o tom das avaliações (seção 8, exploratória e sensível ao modelo).
"""
