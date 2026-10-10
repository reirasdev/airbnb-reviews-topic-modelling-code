"""Seções 1 a 3 do texto unificado: dados, o que os dados permitem medir, como o texto é medido."""
from __future__ import annotations

from doc_base import *  # noqa: F401,F403


def secao1() -> str:
    E = L(sA, "corpus_stats").set_index("metrica")["valor"]
    lang = L(sA, "lang_dist").set_index("idioma")["prop_avaliacoes"]
    R = L(sA, "rating_sintetico")
    Lel = L(sA, "listings_elig")
    top5 = Lel[Lel["review_scores_rating"] == 5.0]
    com5 = int((R["R_off"] == 5.0).sum())
    return f"""## 1. Dados e amostra
{abas("Estat_Corpus", "Selecao_Teto", "Rating_Sintetico", "Descritivo_Teto", "Resumo_AB", "Config")}
Este capítulo apresenta a base e o recorte usados em todas as análises seguintes. O estudo parte de {n(E['imoveis_total'])} anúncios do Airbnb no Rio de Janeiro (Inside Airbnb) e {n(E['avaliacoes_total'])}
avaliações textuais. Dos anúncios, {n(E['imoveis_com_nota'])} têm nota oficial e subnotas (limpeza, localização, check-in, comunicação, custo-benefício e precisão); exigindo nota maior que zero e ao menos duas
avaliações, restaram **{n(E['imoveis_elegiveis(nota>0, v>=MIN_REVIEWS)'])} anúncios elegíveis**.

Para conter o custo computacional, o sentimento foi calculado sobre as **{CONFIG.MAX_REVIEWS_PER_LISTING} avaliações mais recentes de cada anúncio**: {n(E['avaliacoes_usadas'])} avaliações (depois de remover
{n(E['avaliacoes_automaticas_removidas'])} avaliação automática e {n(E['avaliacoes_duplicadas_removidas'])} duplicatas), divididas em **{n(E['sentencas'])} sentenças** ({n(E['textos_unicos'])} textos únicos;
{f(E['sentencas_por_avaliacao(media)'])} sentenças por avaliação e {f(E['tokens_por_sentenca(media)'], 1)} tokens por sentença). Idiomas das avaliações usadas (detectados por avaliação): português {pc(lang['pt'], 1)},
inglês {pc(lang['en'], 1)}, espanhol {pc(lang['es'], 1)}, francês {pc(lang['fr'], 1)}, alemão {pc(lang['de'], 1)} e italiano {pc(lang['it'], 1)}; o corpus não foi separado por idioma.

A nota oficial é fortemente comprimida: entre os {n(len(R))} anúncios com índice sintético (seção 7), {pc((R['R_off'] == 5).mean(), 1)} têm nota exatamente 5,0 (média {f(R['R_off'].mean())}; desvio-padrão {f(R['R_off'].std())}).
Entre os {n(len(Lel))} elegíveis, {n(len(top5))} têm nota 5,0 ({pc(len(top5) / len(Lel), 1)}); desses, {n(com5)} ({pc(com5 / len(top5), 1)}) têm índice sintético, porque o índice exige evidência textual em ao menos três aspectos.
"""


def secao2() -> str:
    F = L(sA, "formula_ocupacao")
    fl = F.set_index("formula")
    ex = fl.loc["min(255, ltm × 2 × max(3, minimum_nights))"]
    rec = fl.loc["receita = preço × ocupação"]
    zero = fl.loc["ltm = 0 ⇒ ocupação = 0"]
    CF = L(sA, "coef_forma_flexivel")
    c5 = CF[CF["escopo"] == "R_off = 5,0"].set_index("controles")
    base, flex = c5.iloc[0], c5.iloc[1]
    inv = L(sA, "investigacao_coef_correlacoes")
    rho = inv[(inv["escopo"] == "R_off = 5,0") & (inv["variavel"] == "log_ltm")]["spearman_com_ocupacao"].iloc[0]
    return f"""## 2. O que os dados permitem medir
{abas("Formula_Ocupacao", "REF_Investigacao_Coef")}
A seção anterior descreveu o que existe na base; esta delimita o que ela permite concluir, porque isso determina qual é o objeto central do estudo. Os dados trazem a nota e as subnotas oficiais (escala de 1 a 5) e o
texto das avaliações, mas **não trazem ocupação nem receita observadas**. Os campos `estimated_occupancy_l365d` e `estimated_revenue_l365d` são estimativas da Inside Airbnb que verificamos ser funções exatas de
variáveis do próprio anúncio: `ocupação = min(255, avaliações nos últimos 12 meses × 2 × max(3, estadia mínima))` reproduz o campo em {pc(ex['prop_exata'], 1)} dos {n(ex['n'])} anúncios, e
`receita = preço × ocupação` em {pc(rec['prop_exata'], 1)} dos {n(rec['n'])} anúncios com preço; sem avaliação nos últimos 12 meses a ocupação é zero em {pc(zero['prop_exata'], 1)} dos {n(zero['n'])} casos.
Na faixa de nota 5,0, a correlação de postos entre a ocupação estimada e as avaliações dos últimos 12 meses é {f(rho)}.

Por isso, daqui em diante esses campos são chamados de **índices de volume recente de avaliações**, e as expressões "desempenho econômico", "ocupação" e "receita" não são usadas para eles sem essa qualificação. Um corolário
metodológico: controlar a análise pelo número de avaliações dos últimos 12 meses equivale a controlar o próprio desfecho. Uma versão anterior da análise o fazia e obteve, na faixa de nota 5,0, um coeficiente de R_syn
de {f(base['coef_R_syn_z'])} noite por desvio-padrão (p = {f(base['p'], 4)}); ele desaparece com uma forma funcional flexível ({f(flex['coef_R_syn_z'])}; p = {f(flex['p'])}) e é zero com a fórmula exata, e
a análise foi refeita sem esse controle (seção 7). **Consequência anunciada:** o objeto central do estudo são a nota, as subnotas e o texto das avaliações; o volume de avaliações entra apenas como desfecho auxiliar, em três
formas: o índice de ocupação, o índice de receita (em log) e o número de avaliações dos últimos 12 meses (em log), este último sem construção algébrica.
"""


def secao3() -> str:
    D = L(sA, "cmp_descritivas").set_index("modelo")
    man = L(sA, "cmp_manual_modelos").set_index("modelo")
    comp_b = metrica("etapa3_bertopic", "n_topicos")
    outl_fit, outl_fin, cv_b = metrica("etapa3_bertopic", "outliers_fit_pct"), metrica("etapa3_bertopic", "outliers_final_pct_textos"), metrica("etapa3_bertopic", "c_v_medio")
    k_lda, cv_lda = metrica("etapa3_lda", "K_escolhido"), metrica("etapa3_lda", "c_v_medio")
    rev = pd.read_excel(CONFIG.MAPPING_CSV.replace(".csv", ".xlsx"))
    acei, alt, disc = int((rev["aspecto_usuario"] == rev["sugestao"]).sum()), int((rev["aspecto_usuario"] != rev["sugestao"]).sum()), int(rev["alterado_por_claude"].sum())
    n_sat = int((rev["aspecto_confirmado"] == "satisfacao_geral").sum())
    sh = metrica("etapa5", "sentencas_por_aspecto")
    cob = metrica("etapa5", "cobertura_por_aspecto")
    n_perfil = metrica("etapa5", "imoveis_com_perfil")
    linhas = [[ROT[a], pc(sh[a], 1), n(cob[a])] for a in sorted(ASP, key=lambda a: -sh[a])] + [["Fora do perfil (`geral`)", pc(sh["geral"], 1), "—"]]
    return f"""## 3. Como o texto é medido
{abas("Config", "Comparacao_Sentimento_AB", "Avaliacao_Rotuladas_AB", "Topicos_BERTopic", "Topicos_LDA", "Mapa_Topico_Aspecto", "Mapa_Revisao", "Resumo_Log", "LadoALado_perfil_cobertura")}
Delimitado o objeto, esta seção descreve como o texto vira medida: sentimento por frase, tópicos, aspectos e perfil por anúncio. A medição é feita em quatro passos e cada um é avaliado na seção 4.

**Sentimento, com dois modelos.** Como a escolha do modelo pode alterar as conclusões, usamos dois, de natureza diferente. O modelo **A** (`{CONFIG.SENTIMENT_MODEL}`) é um modelo multilíngue genérico, treinado em
tweets, com três classes (negativo, neutro, positivo); convertemos a saída em estrelas esperadas, 1·P(neg) + 3·P(neu) + 5·P(pos). O modelo **B** (`{CONFIG.SENTIMENT_MODEL_B}`) é multilíngue e foi treinado em avaliações
de produtos e serviços, com cinco classes (1 a 5 estrelas); as estrelas esperadas são a soma de k·P(k). A polaridade discreta de A é a classe mais provável das três; a de B é negativa se a classe mais provável tem 1 ou 2 estrelas,
neutra se tem 3 e positiva se tem 4 ou 5. Ambos foram aplicados às mesmas {n(D.loc['A', 'sentencas'])} sentenças ({n(D.loc['A', 'textos_unicos'])} textos únicos). As estrelas médias por texto único são {f(D.loc['A', 'estrelas_media_texto'])}
em A e {f(D.loc['B', 'estrelas_media_texto'])} em B; a proporção de sentenças com quatro estrelas ou mais é {pc(D.loc['A', 'prop_sentencas_ge_4_estrelas'], 1)} em A e {pc(D.loc['B', 'prop_sentencas_ge_4_estrelas'], 1)} em B, e a
distribuição das polaridades (negativa, neutra, positiva) é {pc(D.loc['A', 'prop_sentencas_negativa'], 1)}, {pc(D.loc['A', 'prop_sentencas_neutra'], 1)} e {pc(D.loc['A', 'prop_sentencas_positiva'], 1)} em A, e
{pc(D.loc['B', 'prop_sentencas_negativa'], 1)}, {pc(D.loc['B', 'prop_sentencas_neutra'], 1)} e {pc(D.loc['B', 'prop_sentencas_positiva'], 1)} em B: nos dois, a maior parte das frases é positiva, o que reproduz no texto o viés de
positividade da plataforma. As análises usam a **ordenação** do sentimento, não o seu nível; por isso importa que as estrelas esperadas ordenem as frases como um leitor humano: a correlação de postos entre o rótulo manual
(−1, 0, +1) e as estrelas esperadas é {f(man.loc['A', 'spearman_rotulo_estrelas'])} em A e {f(man.loc['B', 'spearman_rotulo_estrelas'])} em B (seção 4.1).

**Tópicos.** As frases foram agrupadas por **BERTopic** (embeddings multilíngues `paraphrase-multilingual-MiniLM-L12-v2`, UMAP e HDBSCAN, ajustado em uma amostra de {n(CONFIG.BERTOPIC_FIT_SAMPLE)} sentenças e aplicado às demais),
que encontrou **{n(comp_b)} tópicos**; {f(outl_fit, 1)}% das frases da amostra de ajuste ficaram como ruído, reduzidos a {f(outl_fin, 1)}% dos textos depois da reatribuição ao centroide mais próximo. A coerência C_v média dos tópicos do BERTopic é
{f(cv_b, 3)}. O **LDA** (K = {k_lda}, escolhido por C_v máximo numa grade de {CONFIG.LDA_K_GRID[0]} a {CONFIG.LDA_K_GRID[-1]}) tem C_v médio {f(cv_lda, 3)}; esses valores descrevem cada método e não os colocam em disputa. O papel do LDA neste estudo é
o de uma checagem (seção 4.5).

**Mapa tópico → aspecto.** Cada tópico do BERTopic foi mapeado a um de dez aspectos (limpeza, localização, check-in, comunicação, custo-benefício, ruído e conforto, segurança, precisão do anúncio, comodidades e satisfação geral, este
último para elogio ou queixa genérica); o código sugeriu o aspecto pela similaridade com termos-semente multilíngues e a decisão foi do pesquisador, tópico a tópico: dos {n(len(rev))} tópicos, {n(acei)} mantiveram a sugestão automática,
{n(alt)} foram alterados pelo pesquisador e {n(disc)} reclassificados depois de discussão; {n(n_sat)} tópicos ficaram em satisfação geral. Cada frase herda o aspecto do seu tópico.

**Perfil por anúncio.** Para cada anúncio e aspecto, o perfil é a média do sentimento das frases do aspecto, exigindo ao menos {CONFIG.MIN_SENT_PER_ASPECT} frases; {n(n_perfil)} anúncios têm perfil. Participação de cada aspecto nas sentenças e número de
anúncios com o aspecto disponível:

{tabela(["Aspecto", "Frases do corpus", "Anúncios com o aspecto"], linhas)}
"""
