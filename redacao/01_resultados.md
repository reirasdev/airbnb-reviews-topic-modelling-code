# Resultados (rascunho v2 para a dissertação)

> **Estrutura v2 (2026-10-04):** organizada pelas perguntas de pesquisa de `00_enquadramento.md` (adequação, importância, aplicação,
> sazonalidade e resultado complementar). A versão anterior, escrita como teste de hipótese, está no git (tag `estrategia-v1-tese-final`).
> Números vindos das abas do Excel e de `historico/HISTORICO_DECISOES.md` (execuções `run_20261004_144225` a `run_20261004_203720`).
> Trechos **[conferir]** dependem de informação externa ao pipeline. **Todas as medidas são de associação**, sem linguagem causal.
> **Planilha de apoio:** `resultados_20261004_215620.xlsx`; cada seção abre indicando as abas correspondentes (*Abas da planilha*). Seção 6 (sazonalidade) é opcional: o texto completo e as tabelas ficam em `03_sazonalidade_eventos.md`.

## 1. Dados e amostra

*Abas da planilha:* `Estat_Corpus`, `Config`, `Resumo_Log`.


O estudo usa 42.013 anúncios do Airbnb no Rio de Janeiro e 995.072 avaliações textuais. Dos anúncios, 33.140 têm nota oficial e subnotas;
após exigir nota maior que zero e ao menos duas avaliações, restaram **28.890 anúncios elegíveis**. Para conter o custo computacional, o
sentimento foi calculado sobre as **30 avaliações mais recentes de cada anúncio**: 475.858 avaliações (após remover 1 avaliação automática e 311
duplicatas), divididas em **1.512.063 sentenças** (1.366.091 textos únicos; 3,18 sentenças por avaliação, 12,4 tokens por sentença). Idiomas das
avaliações usadas: português 66,2%, inglês 15,5%, espanhol 14,2%, francês 2,4%, alemão 1,1%, italiano 0,3%. O corpus não foi separado por idioma.
A nota oficial é fortemente comprimida: 22,8% dos anúncios analisados têm nota exatamente 5,0 (média 4,82; desvio-padrão 0,22).

## 2. Medição: sentimento, tópicos e aspectos

*Abas da planilha:* `Topicos_BERTopic`, `Topicos_LDA`, `Mapa_Topico_Aspecto` (tópico → aspecto), `Perfil_ABSA` (sentimento por anúncio e aspecto).


**Sentimento.** Um único modelo multilíngue (`cardiffnlp/twitter-xlm-roberta-base-sentiment`, três classes) foi aplicado a cada sentença e convertido em
estrelas esperadas, 1·P(neg) + 3·P(neu) + 5·P(pos), na mesma escala 1–5 das notas. A média é 4,19 estrelas (mediana 4,64); 75,1% das sentenças têm 4
estrelas ou mais e 5,6% têm 2 ou menos, reproduzindo no texto o viés de positividade da plataforma. O modelo foi treinado em tweets (deslocamento de domínio).

**Tópicos.** O **BERTopic** (embeddings `paraphrase-multilingual-MiniLM-L12-v2`, UMAP + HDBSCAN, ajustado em 200.000 sentenças e aplicado às demais) encontrou **185
tópicos** (29,8% de ruído na amostra de ajuste, reduzidos a 1,0% após reatribuição por similaridade ao centroide); coerência C_v média 0,388. Tópicos em
português, inglês e espanhol aparecem juntos (ex.: "praia, beach, playa, restaurantes, mar"). O **LDA** (linha de base; K escolhido por C_v máximo numa grade de 5 a 40) ficou com
K = 10 e C_v 0,625 (K = 5: 0,612; 15: 0,594; 20: 0,575; 25: 0,525; 30: 0,537; 40: 0,516). A comparação é só indicativa: o LDA produz poucos tópicos amplos, o que favorece o
C_v. Para aspectos, a granularidade do BERTopic é a relevante. *Nota:* uma primeira execução mutilava palavras acentuadas por causa do pré-processamento padrão da
biblioteca; foi corrigida (`language="multilingual"`) e o C_v daquela execução (0,358) foi descartado (`historico/v1_etapa3_bertopic_sem_acentos/RESUMO.md`).

**Mapeamento tópico → aspecto.** O código sugeriu o aspecto pela similaridade de cosseno entre o centroide do tópico e o vetor do aspecto (termos-semente multilíngues); a decisão
foi humana, tópico a tópico. A sugestão automática concentrava tópicos em `localização` e tratava elogio genérico como aspecto; a revisão (105 tópicos mantidos, 80 alterados
pelo pesquisador, 66 reclassificados depois) criou o aspecto **`satisfacao_geral`** (elogio ou queixa genérica: "recomendo", "voltarei", "adorei"). Distribuição das sentenças por
aspecto: satisfação geral 27,1%; comunicação 19,2%; localização 18,3%; comodidades 13,0%; limpeza 7,7%; precisão 5,2%; ruído/conforto 2,5%; check-in 2,3%; segurança 1,3%;
custo-benefício 1,0%; fora do perfil 2,5%. Para cada anúncio e aspecto, o perfil é a média do sentimento das sentenças do aspecto (mínimo de duas).

## 3. Pergunta 1 — O sentimento por aspecto é adequado às notas e subnotas oficiais?

*Abas da planilha:* `Validacao_Construto`, `Val_Volume_Convergente`, `Val_Matriz`, `Val_Confiab_AUC`, `Val_Recortes`, `Val_Manual`.


### 3.1 Concordância por aspecto

*Abas da planilha:* `Validacao_Construto`.


Correlação, no nível do anúncio, entre o sentimento do aspecto e a subnota oficial correspondente (sem limiar de aprovação; interessa a força e o sinal):

| Aspecto | Subnota oficial | n | Spearman | Pearson |
|---|---|---:|---:|---:|
| Limpeza | cleanliness | 19.095 | 0,453 | 0,579 |
| Check-in | checkin | 8.919 | 0,419 | 0,401 |
| Satisfação geral | rating (nota global) | 26.378 | 0,341 | 0,523 |
| Comunicação | communication | 25.418 | 0,296 | 0,436 |
| Localização | location | 24.101 | 0,240 | 0,312 |
| Custo-benefício | value | 3.552 | 0,237 | 0,261 |
| Precisão | accuracy | 16.638 | 0,168 | 0,218 |

Todos os coeficientes são positivos e significativos (p < 0,001). A concordância é **moderada**, e deve ser lida considerando que as subnotas oficiais também são comprimidas (muitos empates em
5,0), o que atenua as correlações. Ruído/conforto, segurança e comodidades não têm subnota e não puderam ser validados.

### 3.2 Robustez da concordância

*Abas da planilha:* `Val_Volume_Convergente` (por volume e convergente/discriminante), `Val_Matriz`, `Val_Confiab_AUC` (confiabilidade, AUC e Kendall), `Val_Recortes` (idioma e tipo).


- **Por volume (Spearman, ≤ 30 avaliações, em que o sentimento usa todas, vs > 30):** limpeza 0,44 vs 0,46; check-in 0,49 vs 0,37; comunicação 0,27 vs 0,29; localização 0,23 vs 0,29; custo-benefício 0,26 vs 0,23;
  precisão 0,17 vs 0,16; satisfação geral 0,33 vs 0,35. O corte de 30 avaliações não enfraquece a concordância de modo sistemático.
- **Convergente/discriminante.** A subnota correspondente é a mais correlacionada com o aspecto em 5 de 7 casos e a segunda em limpeza e precisão (as subnotas são muito correlacionadas entre si, efeito halo). Controlando a nota
  global (correlação parcial), resta informação específica em limpeza (0,17), localização (0,22), check-in (0,23) e comunicação (0,15), e quase nenhuma em custo-benefício (0,08) e precisão (0,04).
- **Subnotas saturadas.** Probabilidade de o sentimento ser maior em anúncios com subnota 5 do que nos de subnota < 5 (AUC): limpeza 0,69; check-in 0,65; comunicação 0,65; satisfação geral 0,66; custo-benefício 0,62;
  localização 0,60; precisão 0,57. Kendall tau-b de 0,12 a 0,32.
- **Entre idiomas e tipos.** Padrão semelhante em inglês, espanhol e português (limpeza 0,39/0,45/0,35; check-in 0,43/0,44/0,38; precisão 0,17/0,15/0,16), o que sustenta o uso de um modelo multilíngue; e entre
  casa/apartamento inteiro e quarto privado (limpeza 0,45 e 0,46; localização 0,24 e 0,25).
- **Atenuação.** A confiabilidade split-half do sentimento por aspecto é baixa (0,10 a 0,40 após Spearman-Brown). Correlações corrigidas por essa atenuação (0,57 a 0,96) são **ilustrativas e instáveis** (com confiabilidades tão
  baixas a correção é muito sensível) e corrigem apenas o lado do sentimento.

### 3.3 Validação manual (297 frases rotuladas pelo pesquisador, rótulo cego)

*Abas da planilha:* `Val_Manual` (métricas, matrizes de confusão e desempenho por classe).


Amostra estratificada por aspecto previsto (~27 por aspecto) e por polaridade prevista (um terço de cada), portanto **rica em frases difíceis**: 81,5% das frases do corpus são previstas como positivas, e na amostra só
um terço. Por isso as acurácias da amostra (59% e 54,5%) subestimam o desempenho no corpus. Ponderando cada frase pelo tamanho do seu estrato (aspecto × polaridade) na população, a **acurácia de sentimento estimada é de 87%
(IC 95% bootstrap 82% a 91%) e a de aspecto de 67% (56% a 76%)**; o tamanho efetivo da amostra ponderada é de apenas ~72 frases, então os intervalos são largos e o procedimento depende do esquema de pesos. A precisão por aspecto
previsto é uma estimativa direta; o recall e as acurácias da amostra não representam a população.

- **Sentimento (3 classes):** na amostra, acurácia 58,9%; F1 macro 0,57; kappa 0,39 (0,48 ponderado linear); **ponderado pela população, acurácia 87% e kappa 0,55 (IC 0,44 a 0,64)**; Spearman com as estrelas do modelo 0,64. Por idioma: francês 0,92 (n = 12), inglês 0,65 (63), espanhol 0,62 (45), **português
  0,52 (166)**. O erro é **conservador**: das 174 frases positivas, o modelo classifica 60 como neutras e 21 como negativas, e nunca chamou de positiva uma frase negativa (0 de 77); quando diz "positivo" acerta 95%, quando diz
  "negativo", 62%. As estrelas comprimem o nível, mas preservam a ordenação.
- **Aspecto:** na amostra, acurácia 54,5%; kappa 0,50; ponderada pela população, 67%. Precisão por aspecto previsto: custo-benefício 0,74; localização 0,74; precisão 0,70; limpeza 0,67; check-in 0,56; segurança 0,48; comodidades 0,44; comunicação 0,44; ruído/conforto
  0,44; satisfação geral 0,41. Frases cujo tópico original era ruído e foi reatribuído têm acerto de aspecto de 38%, contra 65% nos tópicos diretos; a similaridade ao centroide não separa acertos de erros, e mandar essas frases
  para `geral` seria pior (19%).

### 3.4 Síntese da pergunta 1

*Abas da planilha:* síntese dos resultados das abas acima.


O sentimento por aspecto é **moderadamente adequado** às notas e subnotas: positivo e significativo em todos os aspectos, estável entre volumes, idiomas e tipos, e com informação específica além do halo da nota global em limpeza,
localização, check-in e comunicação. A concordância é limitada pelo ruído da medição (na validação manual, sentimento 59% e aspecto 55% de acerto na amostra estratificada, e ~87% e ~67% ponderados pela população; confiabilidade split-half baixa) e pela compressão das subnotas. Os aspectos mais
confiáveis são custo-benefício, localização, precisão, limpeza e check-in (em precisão de atribuição); os demais devem ser lidos com cautela.

## 4. Pergunta 2 — Quais aspectos e tópicos mais se associam à nota?

*Abas da planilha:* `Imp_Aspectos`, `Imp_Modelos`, `Imp_Segmentos_Sens`, `Imp_Topicos_Queixas`, `Imp_Topicos_Elogios`.


Análise no nível do anúncio (28.889 anúncios com texto, **incluindo os de pouco texto**: o sentimento não observado de um aspecto é imputado pela média). O alvo é o percentil da nota (a nota é comprimida no teto).

### 4.1 Importância dos aspectos para a nota global

*Abas da planilha:* `Imp_Aspectos` (decomposição LMG e betas), `Imp_Modelos` (GBM, permutação e regressão logística), `Imp_Segmentos_Sens` (segmentos e sensibilidades).


Decomposição LMG/Shapley do R² (R² total = 0,32): **comodidades 42,5%**, **limpeza 19,6%**, **satisfação geral 17,5%**, **comunicação 11,3%**, check-in 3,4%, ruído/conforto 3,1%, precisão 1,7%, localização 0,6%, custo-benefício
0,3%, segurança 0,1%. O padrão é estável nas sensibilidades (≥ 3 aspectos, ≤ 30 avaliações, só tópicos diretos, sem satisfação geral como preditor) e entre segmentos (casa inteira/quarto privado, idioma predominante, os 6 maiores
bairros: comodidades entre 37% e 43% em todos). Para cada subnota, o aspecto correspondente está entre os mais importantes (localização explica 42% do R² da subnota de localização; limpeza 33% da de limpeza), mas **a nota
global quase não depende do sentimento sobre localização**. Um GBM com valores ausentes tem R² fora da amostra de 0,44 (OLS 0,39); a queda de R² por permutação é maior em comodidades (0,23), limpeza (0,08) e satisfação geral (0,07).
Na regressão logística para "nota ≥ 4,9" (51% dos anúncios; AUC fora da amostra 0,82), um desvio-padrão a mais de sentimento multiplica as chances por 2,46 em comodidades, 1,91 em limpeza, 1,48 em satisfação geral, 1,37 em comunicação
e 1,25 em check-in.

### 4.2 Queixas e elogios por tópico

*Abas da planilha:* `Imp_Topicos_Queixas`, `Imp_Topicos_Elogios`.


Apenas tópicos diretos (precisão de aspecto ~65%). O "efeito" compara o percentil da nota entre anúncios com e sem ao menos uma menção negativa (ou positiva) no tópico, controlando volume de avaliações e de frases; q de
Benjamini-Hochberg (57 de 68 queixas e 145 de 181 elogios com q < 0,05). Queixas que mais pesam (efeito × prevalência):

| Tópico (palavras-chave) | Aspecto | Anúncios com menção | Efeito no percentil da nota |
|---|---|---:|---:|
| Banheiro, chuveiro, água | Comodidades | 14% | −20 pontos |
| Ar-condicionado, calor | Comodidades | 13% | −18 |
| Sujeira, limpeza | Limpeza | 7% | −26 |
| Queixa genérica (decepção, problemas) | Satisfação geral | 9% | −20 |
| Cozinha, utensílios | Comodidades | 7% | −19 |
| Resposta do anfitrião, problema | Comunicação | 5% | −23 |
| Barulho | Ruído e conforto | 11% | −10 |
| Cheiro, mofo | Limpeza | 5% | −22 |
| Cama, colchão | Comodidades | 5% | −18 |
| Claridade, cortinas | Ruído e conforto | 5% | −16 |
| Manutenção, reparos | Comodidades | 3% | −21 |
| Wi-Fi | Comodidades | 3% | −19 |
| Fechadura eletrônica | Check-in | 3% | −20 |

Elogios mais associados: o anfitrião (84% dos anúncios; +8,5 pontos), sentir-se em casa (34%; +10,9), intenção de voltar (44%; +8,2) e limpeza/organização (34%; +4,8). O efeito médio de uma queixa, por aspecto, é de −20 pontos
em custo-benefício, −17 em check-in, −15 em comodidades e −14 em limpeza.

### 4.3 Cuidados de interpretação

*Abas da planilha:* interpretação dos resultados das abas `Imp_*`.


(i) É associação, não causa. (ii) A importância relativa mistura efeito e confiabilidade da medida: aspectos pouco citados (segurança, custo-benefício) são medidos com mais erro e imputados na maioria dos anúncios. (iii)
`comodidades` é um aspecto largo (33 tópicos); a leitura prática está na análise por tópico. (iv) A precisão da atribuição de aspecto varia de 0,41 a 0,74. (v) O R² cai para 0,24 quando só se usam tópicos diretos, por haver menos frases.

## 5. Pergunta 3 — Diagnóstico para anfitriões e empresas gestoras

*Abas da planilha:* `Benchmark_Bairro_Tipo`; exemplos de relatório em `redacao/exemplos_diagnostico/`.


A ferramenta `diagnostico.py` gera, a pedido, o relatório de **um** anúncio: sentimento por aspecto e posição (percentil) entre anúncios do mesmo bairro e tipo (ou do tipo na cidade, se o bairro tiver menos de 30), evidência por
aspecto (poucas frases = baixa), queixas e elogios recorrentes com a associação média na cidade (seção 4.2), evolução das 10 avaliações mais recentes e nota metodológica com as precisões da validação manual. Funciona para
anúncios novos. A Etapa 17 gera tabelas de referência para 66 grupos de bairro × tipo com ao menos 30 anúncios (aba `Benchmark_Bairro_Tipo`). Três exemplos anonimizados (`redacao/exemplos_diagnostico/`): (A) nota 5,0,
limpeza como ponto forte (80º percentil entre 1.338 pares); (B) nota 4,39 (6º percentil), com comodidades (sentimento médio 2,60) e satisfação geral no 4º percentil, e queixas de banheiro e cozinha; (C) apenas 6 avaliações, com
a maior parte dos aspectos sem evidência suficiente. O relatório prioriza onde investigar, não prevê nem prescreve causas.

## 6. Pergunta 4 (opcional) — Sazonalidade e eventos

*Abas da planilha:* `Sazon_Volume`, `Sazon_Conteudo`, `Sazon_Criterio`.


O volume de avaliações em janelas de eventos foi de 1,24 a 1,73 vez o de dias comuns do mesmo mês (IC 95% excluindo 1; defasagem de 14 dias): Rock in Rio 1,73; Corpus Christi 1,34; Réveillon 1,34; Todo Mundo no Rio (2024)
1,31; Carnaval 1,26; Semana Santa 1,25; feriados curtos 1,24. É volume de avaliações escritas, **não ocupação**, e os dados só incluem anúncios ainda ativos na coleta. Nos eventos de música e em Corpus Christi, a proporção de frases
negativas é menor (razão de chances de 0,84 a 0,91), compatível com um público diferente; no Carnaval e no Réveillon não há deslocamento geral e aumentam as queixas de fidelidade ao anúncio, custo-benefício e localização.
Tabelas completas, defasagem de 7 dias, intervalos e limitações em `03_sazonalidade_eventos.md`.

## 7. Pergunta 5 (complementar) — O rating sintético acrescenta algo à nota oficial?

*Abas da planilha:* `Rating_Sintetico`, `Descritivo_Teto`, `Formula_Ocupacao`, `Analise_A`, `Analise_B`, `Sensibilidade`; referência da análise anterior em `REF_Sem_LTM` e `REF_Investigacao_Coef`.


**Rating sintético (R_syn).** Média igual do sentimento dos aspectos disponíveis (mínimo de 3 aspectos específicos; `satisfacao_geral` entra na média mas não conta para o mínimo), na escala 1–5, para **22.564 anúncios**. A especificação
principal não aplica shrinkage; a versão com média bayesiana (m = 23) é reportada como sensibilidade. A calibração por quantis (`R_syn_cal`) serve só para exibição em estrelas.

**Compressão.** A nota oficial concentra 22,8% dos anúncios em 5,0; R_syn concentra 1,6% no seu valor mais comum. A correlação de postos entre R_syn e a nota é 0,62 e **61% dos anúncios mudam 10 pontos percentuais de posto ou mais**.
Dentro do grupo com nota 5,0 (n = 5.142), R_syn distribui os anúncios entre o percentil 0,27 e 0,98 (5º–95º) e concorda fracamente, mas de forma positiva, com as seis subnotas (Spearman de +0,08 a +0,12; subnotas também saturadas).

**Desfechos.** Ocupação e receita estimadas são funções exatas de variáveis do anúncio (`ocupação = min(255, avaliações_12m × 2 × max(3, minimum_nights))`; `receita = preço × ocupação`; verificado em 100% dos 42.013 anúncios e
consistente com a documentação da Inside Airbnb): índices de volume recente de avaliações, não ocupação observada. Por isso se usou também o número de avaliações dos últimos 12 meses (log) como desfecho direto, e **não** se controlou
por esse volume (controlar o desfecho anulava o teste; `02_investigacao_coeficiente_negativo.md`). Controles: volume total, preço, tipo e bairro. Validação out-of-sample: k-fold 5 × 5, seed fixa; 20.882 anúncios.

**Poder explicativo (R² out-of-sample; M0 = controles, M1 = + nota oficial, M2 = + R_syn, M3 = + ambos):**

| Desfecho | Escopo | n | M0 | M1 | M2 | M3 |
|---|---|---:|---:|---:|---:|---:|
| Ocupação | amostra completa | 20.882 | 0,475 | 0,483 | 0,478 | 0,483 |
| Ocupação | R_off ≥ 4,8 | 14.451 | 0,502 | 0,509 | 0,503 | 0,509 |
| Ocupação | R_off ≥ 4,9 | 9.747 | 0,538 | 0,541 | 0,538 | 0,541 |
| Ocupação | R_off = 5,0 | 4.711 | 0,506 | 0,506 | 0,506 | 0,506 |
| Receita (log) | amostra completa | 20.882 | 0,175 | 0,192 | 0,179 | 0,193 |
| Avaliações 12 m (log) | amostra completa | 20.882 | 0,440 | 0,456 | 0,444 | 0,456 |

Ganho de R² (IC 2,5%–97,5% entre dobras):

| Desfecho / escopo | M1 − M0 (nota oficial) | M2 − M1 (R_syn no lugar) | M3 − M1 (R_syn além da nota) |
|---|---|---|---|
| Ocupação, completa | **+0,0079** [+0,0052; +0,0099] | **−0,0050** [−0,0070; −0,0020] | 0,0000 [−0,0005; +0,0002] |
| Ocupação, R_off ≥ 4,8 | **+0,0063** [+0,0038; +0,0091] | **−0,0059** [−0,0083; −0,0033] | 0,0000 [−0,0003; +0,0002] |
| Ocupação, R_off ≥ 4,9 | **+0,0033** [+0,0009; +0,0057] | **−0,0033** [−0,0055; −0,0010] | −0,0001 [−0,0003; 0,0000] |
| Ocupação, R_off = 5,0 | 0 (nota constante) | −0,0002 [−0,0009; 0,0000] | −0,0002 [−0,0009; 0,0000] |
| Receita, completa | **+0,0174** [+0,0089; +0,0239] | **−0,0132** [−0,0206; −0,0050] | +0,0010 [−0,0013; +0,0025] |
| Receita, R_off = 5,0 | 0 | +0,0019 [−0,0040; +0,0059] | +0,0019 [−0,0040; +0,0059] |
| Avaliações 12 m, completa | **+0,0163** [+0,0108; +0,0208] | **−0,0116** [−0,0157; −0,0067] | +0,0006 [−0,0009; +0,0014] |
| Avaliações 12 m, R_off = 5,0 | 0 | +0,0015 [−0,0020; +0,0041] | +0,0015 [−0,0020; +0,0041] |

**Leitura.** A nota oficial acrescenta poder explicativo pequeno, mas detectável (0,8 a 1,7 pontos percentuais de R²); R_syn, no lugar dela, explica menos; e R_syn **não acrescenta nada além dela**, nem no teto. Isso é coerente com a pergunta 1:
o texto e a nota carregam informação semelhante. Em R_off = 5,0 há coeficientes dentro da amostra positivos para receita (+0,14 em log por DP; p = 0,0004) e avaliações em 12 m (+0,040, ≈ +4% por DP; p < 0,0001), sem confirmação fora da
amostra (ΔR² ≈ +0,0015, IC cruzando zero) e sem correção para múltiplas comparações: evidência fraca. Na amostra completa o coeficiente de R_syn é negativo (avaliações −0,037; p < 0,0001) enquanto o da nota oficial é positivo (+0,16).

**Monotonicidade e reordenamento (Análise B).** Correlação de postos de R_syn com o desempenho residualizado nos controles, por faixa da nota oficial: todas +0,083 (nota oficial +0,168); [0; 4,5) −0,086; [4,5; 4,8) −0,045; [4,8; 4,9) −0,036;
[4,9; 5,0) −0,018; = 5,0 +0,025. A regressão isotônica fora da amostra tem R² de 0,029 para a nota oficial e 0,006 para R_syn na amostra completa, e ≈ 0 no teto para ambos. R_syn reordena os anúncios em relação à nota oficial, mas a
reordenação não se associa ao desempenho medido.

**Sensibilidade** (ganho de R² de R_syn além da nota oficial no teto = 5,0; ρ de R_syn com o desempenho dentro dessa faixa):

| Variante | ΔR² ocupação | ΔR² avaliações 12 m [IC] | ρ bruto | ρ residual |
|---|---:|---|---:|---:|
| **Sem shrinkage (principal)** | −0,0002 | +0,0015 [−0,0020; +0,0041] | −0,01 | +0,03 |
| Com shrinkage (m = 23) | +0,0001 | +0,0016 [−0,0026; +0,0044] | +0,35 | +0,02 |
| Sem shrinkage, sem `satisfacao_geral` | −0,0002 | +0,0010 [−0,0011; +0,0032] | −0,02 | +0,02 |
| Com shrinkage, sem `satisfacao_geral` | −0,0001 | +0,0011 [−0,0023; +0,0034] | +0,33 | +0,01 |
| Sem shrinkage, apenas v ≤ 30 | −0,0003 | +0,0013 [−0,0037; +0,0046] | +0,02 | +0,03 |
| Com shrinkage, apenas v ≤ 30 | −0,0003 | +0,0014 [−0,0043; +0,0052] | +0,26 | +0,04 |

O ρ bruto de +0,35 com shrinkage é artefato: entre os anúncios de nota 5,0, que têm poucas avaliações (mediana 9, contra 31 nos demais), o encolhimento correlaciona R_syn com o volume (ρ = +0,50 com o log do volume; −0,04 sem shrinkage). Por isso a especificação
principal não o aplica; a escolha foi feita depois de ver esse resultado e ambas as versões são reportadas. O limite de 30 avaliações afeta 32% dos anúncios, mas só 5,2% dos de nota 5,0; a confiabilidade do sentimento médio é ~0,50 com 30 avaliações, 0,67 com 60 e 0,80
com 120, sem deriva temporal relevante (4,345 nas 10 mais recentes vs 4,368 nas 20 mais antigas).

## 8. Limitações

*Abas da planilha:* `Selecao`, `Estat_Corpus`, `REF_Sem_LTM`, `REF_Investigacao_Coef`.


- **Seleção.** Dos 28.890 elegíveis, 6.326 ficaram sem R_syn (menos de 3 aspectos com evidência textual): têm menos avaliações (mediana 3 vs 23), menor ocupação estimada (mediana 12 vs 66) e mais quartos privados (25% vs 14%). Dos 9.373 anúncios de nota 5,0,
  apenas 5.142 (55%) têm R_syn. A análise de importância (seção 4) não exige R_syn e inclui os anúncios com pouco texto.
- **Sentimento e nota oficial cobrem períodos diferentes** (30 avaliações mais recentes vs todas), com efeito pequeno (seção 7).
- **Qualidade da medição:** modelo de sentimento treinado em tweets, com acerto de 59% na amostra de validação (87% ponderado pela população; 52% em português na amostra) e aspecto com 55% (67% ponderado); o mapeamento tópico → aspecto e a validação manual foram feitos por um pesquisador;
  comparação de C_v entre BERTopic e LDA apenas indicativa.
- **Desfechos construídos a partir do volume de avaliações** (seção 7). Ocupação e receita não são observadas.
- **Associação, não causa.** Comparações múltiplas (três desfechos × quatro escopos × seis variantes de R_syn; 249 testes de tópicos) tratadas com Benjamini-Hochberg apenas nos tópicos e na sazonalidade; os coeficientes da seção 7 não são corrigidos.
- **Sazonalidade (opcional):** data da avaliação não é data da estadia; só uma edição do *Todo Mundo no Rio* dentro dos dados; anúncios ainda ativos na coleta.

## 9. Conclusões

*Abas da planilha:* síntese das seções anteriores.


1. O sentimento por aspecto extraído do texto é **moderadamente adequado** às notas e subnotas oficiais (ρ de 0,17 a 0,45), de modo consistente entre volumes, idiomas e tipos, e com informação específica além da nota global em vários aspectos.
2. A nota global se associa sobretudo ao que o hóspede escreve sobre **comodidades e instalações** (42% do R² explicado), **limpeza** (20%), satisfação geral e **comunicação**; queixas de banheiro, ar-condicionado, sujeira, cozinha, resposta do anfitrião,
   cheiro e manutenção são as que mais pesam, em prevalência e associação.
3. Essa informação pode ser entregue a anfitriões e gestoras como diagnóstico por anúncio, comparando-o ao seu bairro e tipo, com a evidência de cada aspecto explícita.
4. (Opcional) Eventos e feriados elevam o volume de avaliações em 24% a 73%; nos eventos de música há menos frases negativas.
5. O rating sintético, como índice único, **não acrescenta poder explicativo sobre o volume recente de avaliações além da nota oficial**, o que reforça que texto e nota medem em grande parte a mesma coisa; seu valor está na decomposição por aspecto, não em substituir a nota.
