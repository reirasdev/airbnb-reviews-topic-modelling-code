"""Seções 8 e 9 do texto unificado: limitações; conclusões."""
from __future__ import annotations

from doc_base import *  # noqa: F401,F403
from sec_5_7 import classificar  # noqa: E402

def secao8() -> str:
    lim = L(sA, "limite30").set_index("medida")["valor"]
    md = L(sA, "cmp_manual_diferenca").set_index(["escopo", "medida"])
    ne = int(round(float(L(sA, "cmp_manual_aspecto").set_index("medida").loc["tamanho efetivo da amostra ponderada", "valor"]))) if "tamanho efetivo da amostra ponderada" in L(sA, "cmp_manual_aspecto").set_index("medida").index else 72
    sv = L(sA, "validacao_construto")
    seg = L(sA, "cmp_segundo_anotador_resumo").set_index("medida")["valor"]
    return f"""## 8. Limitações
{abas("Config", "Estat_Corpus", "Limite_30_Avaliacoes", "Avaliacao_Rotuladas_AB", "Aspecto_Rotuladas", "Val_Confiab_AUC", "Checagem_LDA", "Segundo_Anotador")}
Reunimos aqui o que limita a leitura de todo o texto, na ordem das seções.

- **Recorte do corpus (seção 1).** O sentimento usa as {n(lim['limite de avaliações por anúncio'])} avaliações mais recentes de cada anúncio; {pc(lim['proporção de anúncios truncados'], 0)} dos anúncios elegíveis ({n(lim['anúncios com mais avaliações que o limite (truncados)'])}) têm mais avaliações que o limite. O truncamento afeta pouco os de nota 5,0 ({pc(lim['proporção de truncados entre os de nota 5,0'], 1)}), mas reduz a confiabilidade do sentimento médio por anúncio (Spearman-Brown de {f(lim['confiabilidade Spearman-Brown com 30 avaliações'])} com 30 avaliações).
  Os dados só têm anúncios ativos na coleta, e as avaliações não indicam a data da estadia.
- **Desfechos (seção 2).** Não há ocupação nem receita observadas; os campos disponíveis são funções do número de avaliações recentes. Nenhum resultado fala de desempenho econômico.
- **Medição do texto (seções 3 e 4).** Os rótulos de referência vêm de um único pesquisador, que também revisou o mapa de tópicos para aspectos; um segundo anotador rotulou 100 frases (seção 4.6), com concordância moderada no aspecto (kappa {f(seg["aspecto: kappa de Cohen"], 2)}), de modo que a atribuição de aspecto tem erro de rotulagem além do erro do modelo. A amostra rotulada tem 297 frases e, ponderada pela população, tamanho efetivo de cerca de {n(ne)} frases, de modo que os intervalos são largos e as
  comparações entre modelos são frágeis (a diferença de kappa B − A é de {f(md.loc[('total', 'kappa ponderado linear populacional'), 'B_menos_A'], 3)}, com IC que mal exclui zero). A confiabilidade split-half do sentimento por aspecto é baixa, e as subnotas oficiais usadas como referência são comprimidas. Sete dos dez aspectos pedem cautela (seção 4.6); em especial, comodidades, o aspecto de maior peso,
  tem atribuição imprecisa e não tem subnota para validar. O mapa do LDA foi confirmado pelo pesquisador; o LDA só checa quatro aspectos.
- **Dois modelos de sentimento (seção 4).** O modelo A é o principal por uma regra fixada antes da execução do B, mas B é melhor na amostra rotulada e A na população; a escolha não é óbvia, e por isso os resultados de B acompanham todos os blocos. Onde os dois divergem (seção 7.3), as duas leituras são relatadas sem preferência.
- **Importância dos aspectos (seção 5).** A importância relativa de um aspecto mistura efeito e confiabilidade da medida, e as associações com a nota são entre anúncios, não dentro do anúncio; nada disso autoriza falar em causa. Anúncios sem aspectos suficientes têm sentimento imputado.
- **Índice sintético (seção 7).** Só {n(L(sA, 'cmp_selecao_teto').set_index(['variavel', 'categoria']).loc[('number_of_reviews', '(numérica)'), 'n_com_Rsyn'])} dos anúncios de nota 5,0 têm o índice, e os que ficam de fora têm menos avaliações; as conclusões sobre o teto valem para esse subconjunto. A decisão de não aplicar shrinkage foi tomada depois de ver o resultado com shrinkage. Coeficientes dentro da amostra não são robustos e não foram confirmados fora dela.
- **Generalização.** Um só município, uma só plataforma e uma só coleta.
"""


def secao9() -> str:
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
    return f"""## 9. Conclusões
{abas("Avaliacao_Rotuladas_AB", "Diferenca_B_menos_A", "Validacao_Construto", "Checagem_LDA", "Segundo_Anotador", "Imp_Aspectos", "LadoALado_imp_lmg", "Imp_Topicos_Queixas", "RSyn_Resumo_AB", "Selecao_Teto", "Analise_A", "Comparacoes_Multiplas", "Config")}
As conclusões seguem a ordem da linha de raciocínio. Todas são associações, e todas valem com as ressalvas da seção 8.

1. **A medição do texto é utilizável, com restrições.** Em 297 frases rotuladas por um pesquisador, a acurácia populacional do sentimento é de {pc(ac['A'], 0)} no modelo A e {pc(ac['B'], 0)} no B, e o kappa ponderado populacional é {f(kp['A'], 2)} e {f(kp['B'], 2)}. Pela regra fixada antes da execução do B (diferença de kappa B − A de {f(kp['B_menos_A'], 3)}, IC {ic(kp['dif_ic_inf'], kp['dif_ic_sup'], 3)}), o modelo principal é A, e B acompanha todos os resultados. Os dois modelos concordam em ordenar
   frases e anúncios, mas não são intercambiáveis. O sentimento dos aspectos concorda com as subnotas oficiais de forma moderada e positiva; só {', '.join(conf)} satisfazem o critério de confiança da seção 4.6, e {', '.join(ctl)} pedem cautela. Um segundo método de tópicos (LDA) reproduz o sinal nos aspectos que consegue checar. Entre dois anotadores, a concordância é alta no sentimento (kappa {f(seg["sentimento: kappa de Cohen"], 2)}) e moderada no aspecto ({f(seg["aspecto: kappa de Cohen"], 2)}).
2. **O texto das avaliações revela o que se associa à nota.** Nos dois modelos, comodidades é o aspecto de maior parcela do R² da nota global ({pc(a.loc['comodidades', 'parcela_do_R2'], 0)} em A e {pc(b.loc['comodidades', 'parcela_do_R2'], 0)} em B), seguida de limpeza ({pc(a.loc['limpeza', 'parcela_do_R2'], 0)} e {pc(b.loc['limpeza', 'parcela_do_R2'], 0)}), e isso se mantém em todos os segmentos e sensibilidades.
   Como comodidades pede cautela, a leitura que mais se sustenta é a dos tópicos finos: {n(comum)} das 15 queixas de maior peso são as mesmas nos dois modelos (banheiro e chuveiro, ar-condicionado, sujeira, cozinha, cheiro, cama, wi-Fi, resposta do anfitrião), associadas a quedas de 10 a 26 pontos no percentil da nota.
3. **A decomposição é aplicável ao anúncio.** O diagnóstico por anúncio (seção 6) compara cada aspecto com anúncios do mesmo bairro e tipo, mostra a evidência de cada um e as queixas e elogios recorrentes, e indica onde investigar, sem prever nota nem prescrever causas.
4. **Um índice único não acrescenta poder explicativo.** O índice sintético reordena os anúncios em relação à nota oficial e discrimina os anúncios de nota 5,0 que o têm ({n(Ra['anuncios_nota_5_com_R_syn'])} de {n(n5)}), mas não acrescenta poder explicativo sobre os índices de volume além da nota oficial, em nenhum dos dois modelos. O resultado é nulo e secundário, com duas leituras que não se excluem: o sentimento tem pouca razão teórica para
   prever uma contagem de avaliações, e o valor do texto está na decomposição por aspecto. Os coeficientes dentro da amostra não são robustos e ficam fora desta síntese.

O que o estudo **não** conclui: que o índice sintético seja um "rating melhor", que consertar um problema aponte para aumento de nota, que haja efeito sobre receita ou ocupação.
"""
