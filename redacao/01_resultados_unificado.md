# Resultados unificados (rascunho para a dissertação)

> **Planilha de apoio:** `resultados_final_20261010_160227.xlsx`. Cada seção abre indicando as abas correspondentes (*Abas da planilha*). Todas as medidas são de associação, sem linguagem causal. O mapa tópico → aspecto do LDA e a segunda anotação foram confirmados pelo pesquisador. A organização por perguntas está em `00_enquadramento.md`.

## 1. Dados e amostra

*Abas da planilha:* `Estat_Corpus`, `Selecao_Teto`, `Rating_Sintetico`, `Descritivo_Teto`, `Resumo_AB`, `Config`.

Este capítulo apresenta a base e o recorte usados em todas as análises seguintes. O estudo parte de 42.013 anúncios do Airbnb no Rio de Janeiro (Inside Airbnb) e 995.072
avaliações textuais. Dos anúncios, 33.140 têm nota oficial e subnotas (limpeza, localização, check-in, comunicação, custo-benefício e precisão); exigindo nota maior que zero e ao menos duas
avaliações, restaram **28.890 anúncios elegíveis**.

Para conter o custo computacional, o sentimento foi calculado sobre as **30 avaliações mais recentes de cada anúncio**: 475.858 avaliações (depois de remover
1 avaliação automática e 311 duplicatas), divididas em **1.512.063 sentenças** (1.366.091 textos únicos;
3,18 sentenças por avaliação e 12,4 tokens por sentença). Idiomas das avaliações usadas (detectados por avaliação): português 66,2%,
inglês 15,5%, espanhol 14,2%, francês 2,4%, alemão 1,1% e italiano 0,3%; o corpus não foi separado por idioma.

A nota oficial é fortemente comprimida: entre os 22.564 anúncios com índice sintético (seção 7), 22,8% têm nota exatamente 5,0 (média 4,82; desvio-padrão 0,22).
Entre os 28.890 elegíveis, 9.373 têm nota 5,0 (32,4%); desses, 5.142 (54,9%) têm índice sintético, porque o índice exige evidência textual em ao menos três aspectos.

## 2. O que os dados permitem medir

*Abas da planilha:* `Formula_Ocupacao`, `REF_Investigacao_Coef`.

A seção anterior descreveu o que existe na base; esta delimita o que ela permite concluir, porque isso determina qual é o objeto central do estudo. Os dados trazem a nota e as subnotas oficiais (escala de 1 a 5) e o
texto das avaliações, mas **não trazem ocupação nem receita observadas**. Os campos `estimated_occupancy_l365d` e `estimated_revenue_l365d` são estimativas da Inside Airbnb que verificamos ser funções exatas de
variáveis do próprio anúncio: `ocupação = min(255, avaliações nos últimos 12 meses × 2 × max(3, estadia mínima))` reproduz o campo em 100,0% dos 42.013 anúncios, e
`receita = preço × ocupação` em 100,0% dos 38.356 anúncios com preço; sem avaliação nos últimos 12 meses a ocupação é zero em 100,0% dos 12.979 casos.
Na faixa de nota 5,0, a correlação de postos entre a ocupação estimada e as avaliações dos últimos 12 meses é 0,97.

Por isso, daqui em diante esses campos são chamados de **índices de volume recente de avaliações**, e as expressões "desempenho econômico", "ocupação" e "receita" não são usadas para eles sem essa qualificação. Um corolário
metodológico: controlar a análise pelo número de avaliações dos últimos 12 meses equivale a controlar o próprio desfecho. Uma versão anterior da análise o fazia e obteve, na faixa de nota 5,0, um coeficiente de R_syn
de −1,34 noite por desvio-padrão (p = 0,0001); ele desaparece com uma forma funcional flexível (−0,09; p = 0,62) e é zero com a fórmula exata, e
a análise foi refeita sem esse controle (seção 7). **Consequência anunciada:** o objeto central do estudo são a nota, as subnotas e o texto das avaliações; o volume de avaliações entra apenas como desfecho auxiliar, em três
formas: o índice de ocupação, o índice de receita (em log) e o número de avaliações dos últimos 12 meses (em log), este último sem construção algébrica.

## 3. Como o texto é medido

*Abas da planilha:* `Config`, `Comparacao_Sentimento_AB`, `Avaliacao_Rotuladas_AB`, `Topicos_BERTopic`, `Topicos_LDA`, `Mapa_Topico_Aspecto`, `Mapa_Revisao`, `Resumo_Log`, `LadoALado_perfil_cobertura`.

Delimitado o objeto, esta seção descreve como o texto vira medida: sentimento por frase, tópicos, aspectos e perfil por anúncio. A medição é feita em quatro passos e cada um é avaliado na seção 4.

**Sentimento, com dois modelos.** Como a escolha do modelo pode alterar as conclusões, usamos dois, de natureza diferente. O modelo **A** (`cardiffnlp/twitter-xlm-roberta-base-sentiment`) é um modelo multilíngue genérico, treinado em
tweets, com três classes (negativo, neutro, positivo); convertemos a saída em estrelas esperadas, 1·P(neg) + 3·P(neu) + 5·P(pos). O modelo **B** (`nlptown/bert-base-multilingual-uncased-sentiment`) é multilíngue e foi treinado em avaliações
de produtos e serviços, com cinco classes (1 a 5 estrelas); as estrelas esperadas são a soma de k·P(k). A polaridade discreta de A é a classe mais provável das três; a de B é negativa se a classe mais provável tem 1 ou 2 estrelas,
neutra se tem 3 e positiva se tem 4 ou 5. Ambos foram aplicados às mesmas 1.512.063 sentenças (1.366.091 textos únicos). As estrelas médias por texto único são 4,19
em A e 4,06 em B; a proporção de sentenças com quatro estrelas ou mais é 75,1% em A e 70,0% em B, e a
distribuição das polaridades (negativa, neutra, positiva) é 6,8%, 14,3% e 78,9% em A, e
10,4%, 8,1% e 81,5% em B: nos dois, a maior parte das frases é positiva, o que reproduz no texto o viés de
positividade da plataforma. As análises usam a **ordenação** do sentimento, não o seu nível; por isso importa que as estrelas esperadas ordenem as frases como um leitor humano: a correlação de postos entre o rótulo manual
(−1, 0, +1) e as estrelas esperadas é 0,64 em A e 0,63 em B (seção 4.1).

**Tópicos.** As frases foram agrupadas por **BERTopic** (embeddings multilíngues `paraphrase-multilingual-MiniLM-L12-v2`, UMAP e HDBSCAN, ajustado em uma amostra de 200.000 sentenças e aplicado às demais),
que encontrou **185 tópicos**; 29,8% das frases da amostra de ajuste ficaram como ruído, reduzidos a 1,0% dos textos depois da reatribuição ao centroide mais próximo. A coerência C_v média dos tópicos do BERTopic é
0,388. O **LDA** (K = 10, escolhido por C_v máximo numa grade de 5 a 40) tem C_v médio 0,625; esses valores descrevem cada método e não os colocam em disputa. O papel do LDA neste estudo é
o de uma checagem (seção 4.5).

**Mapa tópico → aspecto.** Cada tópico do BERTopic foi mapeado a um de dez aspectos (limpeza, localização, check-in, comunicação, custo-benefício, ruído e conforto, segurança, precisão do anúncio, comodidades e satisfação geral, este
último para elogio ou queixa genérica); o código sugeriu o aspecto pela similaridade com termos-semente multilíngues e a decisão foi do pesquisador, tópico a tópico: dos 185 tópicos, 105 mantiveram a sugestão automática,
80 foram alterados pelo pesquisador e 66 reclassificados depois de discussão; 53 tópicos ficaram em satisfação geral. Cada frase herda o aspecto do seu tópico.

**Perfil por anúncio.** Para cada anúncio e aspecto, o perfil é a média do sentimento das frases do aspecto, exigindo ao menos 2 frases; 28.889 anúncios têm perfil. Participação de cada aspecto nas sentenças e número de
anúncios com o aspecto disponível:

| Aspecto | Frases do corpus | Anúncios com o aspecto |
|---|---:|---:|
| Satisfação geral | 27,1% | 26.378 |
| Comunicação | 19,2% | 25.418 |
| Localização | 18,3% | 24.101 |
| Comodidades | 13,0% | 22.272 |
| Limpeza | 7,6% | 19.095 |
| Precisão do anúncio | 5,2% | 16.638 |
| Ruído e conforto | 2,5% | 9.550 |
| Check-in | 2,3% | 8.919 |
| Segurança | 1,3% | 5.072 |
| Custo-benefício | 1,0% | 3.552 |
| Fora do perfil (`geral`) | 2,5% | — |

## 4. A medição é confiável?

*Abas da planilha:* `Avaliacao_Rotuladas_AB`, `Aspecto_Rotuladas`, `Comparacao_Sentimento_AB`, `Diferenca_B_menos_A`, `Config`, `Validacao_Construto`, `LadoALado_validacao_construto`, `Val_Volume_Convergente`, `Val_Confiab_AUC`, `Val_Recortes`, `Checagem_LDA`.

A seção 3 define como o texto é medido; antes de usar essas medidas para dizer algo sobre a nota, é preciso saber o quanto elas merecem confiança. Esta seção busca a resposta em cinco tipos de evidência, da mais direta à mais indireta:
frases rotuladas por um pesquisador, concordância entre os dois modelos, uma regra pré-registrada para escolher o modelo principal, concordância com as subnotas oficiais e uma checagem com um método de tópicos diferente. Fecha classificando
cada aspecto, e as seções seguintes respeitam essa classificação.

### 4.1 Evidência direta: frases rotuladas

*Abas da planilha:* `Avaliacao_Rotuladas_AB`, `Aspecto_Rotuladas`, `Resumo_AB`.

O pesquisador rotulou, sem ver as classificações automáticas, 297 frases: sentimento (negativo, neutro ou positivo) e aspecto principal. A amostra foi estratificada pelo aspecto e pela polaridade previstos pelo modelo A (cerca de um terço de frases
de cada polaridade por aspecto) e, portanto, é **rica em frases difíceis**: no corpus, 78,9% das sentenças são positivas segundo A. Por isso há duas leituras de cada métrica: na amostra, e ponderada pela população, em que cada frase pesa o
tamanho do seu estrato original (aspecto × polaridade previstos por A); os pesos são os mesmos para A e B, e o tamanho efetivo da amostra ponderada é de apenas 72 frases, de modo que os intervalos são largos.

| Medida | A | B |
|---|---:|---:|
| Acurácia na amostra | 58,9% | 63,3% |
| F1 macro na amostra | 0,57 | 0,52 |
| Kappa de Cohen na amostra | 0,39 | 0,38 |
| Kappa ponderado linear na amostra | 0,48 | 0,50 |
| Spearman, rótulo humano × estrelas esperadas | 0,64 | 0,63 |
| Acurácia ponderada pela população | 87,2% | 84,9% |
| Kappa ponderado pela população | 0,55 | 0,43 |
| Kappa ponderado linear pela população | 0,66 | 0,51 |

Para os dois modelos o erro mais comum é classificar como neutras frases que o pesquisador considera positivas: quando A prevê "positivo" acerta 94,9%, mas quando prevê "neutro" acerta apenas 26,1%. B classifica
mais frases como positivas (151 contra 98 de 297) e acerta menos nas previstas como neutras e negativas:

| Polaridade prevista | A: frases | A: acerto | B: frases | B: acerto |
|---|---:|---:|---:|---:|
| negativo | 84 | 61,9% | 87 | 51,7% |
| neutro | 115 | 26,1% | 59 | 16,9% |
| positivo | 98 | 94,9% | 151 | 88,1% |

A amostra e a população **discordam sobre qual modelo é melhor**, e é preciso descrever as duas. Na amostra, B tem acurácia maior (63,3% contra 58,9%; em português, 61,4% contra 51,8%),
porque a amostra foi construída a partir das previsões de A e concentra as frases em que A erra (as que A chama de neutras). Ponderando pela população, A é melhor: a acurácia é 87,2% contra 84,9% e o kappa ponderado linear é
0,66 contra 0,51. Por idioma:

| Idioma | Frases | A: acurácia (amostra) | B: acurácia (amostra) | A: acurácia ponderada | B: acurácia ponderada |
|---|---:|---:|---:|---:|---:|
| português | 166 | 51,8% | 61,4% | 85,0% | 82,7% |
| inglês | 63 | 65,1% | 71,4% | 91,5% | 90,5% |
| espanhol | 45 | 62,2% | 60,0% | 84,4% | 81,6% |
| demais idiomas | 23 | 87,0% | 60,9% | 94,6% | 90,4% |

O português, idioma de 66% das avaliações, é o de menor acerto na amostra para o modelo A.

**Aspecto.** A atribuição de aspecto não depende do modelo de sentimento. Acerta 54,5% na amostra (kappa 0,50); ponderando só pela participação de cada aspecto no corpus a estimativa é
52%, e com os estratos aspecto × polaridade, 66% (IC 95% por bootstrap [57%; 75%]), uma estimativa instável (células com poucas frases e pesos muito desiguais): lida na população, a acurácia de aspecto fica
**entre 52% e 66%**. O acerto é parecido nas três polaridades previstas (54%, 53% e 57%), mas muito diferente conforme o tópico:
65% nas frases de tópico direto (186) e 38% nas de tópico reatribuído por similaridade (111).
A precisão varia muito entre aspectos, com cerca de 27 frases rotuladas por aspecto (intervalos de ±0,18):

| Aspecto previsto | Frases rotuladas | Precisão da atribuição |
|---|---:|---:|
| Custo-benefício | 27 | 74% |
| Localização | 27 | 74% |
| Precisão do anúncio | 27 | 70% |
| Limpeza | 27 | 67% |
| Check-in | 27 | 56% |
| Segurança | 27 | 48% |
| Comodidades | 27 | 44% |
| Comunicação | 27 | 44% |
| Ruído e conforto | 27 | 44% |
| Satisfação geral | 27 | 41% |
| Fora do perfil (`geral`) | 27 | 37% |

### 4.2 Concordância entre os dois modelos

*Abas da planilha:* `Comparacao_Sentimento_AB`.

Com a evidência direta limitada a 297 frases, o corpus inteiro permite comparar os modelos entre si. Nas 1.512.063 sentenças, a correlação de postos das estrelas esperadas de A e B é 0,61 e o kappa ponderado linear das
polaridades é 0,45; por idioma, o kappa é 0,40 em português, 0,54 em inglês e 0,54 em espanhol. No nível anúncio × aspecto,
a concordância é maior (0,69 de Spearman; kappa 0,55), porque a média de várias frases reduz o ruído: varia de 0,46 (Precisão do anúncio) a 0,86 (Comodidades). Os dois modelos ordenam as frases e os
anúncios de modo semelhante, mas não são intercambiáveis: das 1.192.861 sentenças que A chama de positivas, B concorda em 1.087.384; das 215.635 que A chama de neutras, B chama 128.723 de positivas. Concordância completa:

| Nível | Grupo | n | Spearman das estrelas | Pearson das estrelas | Kappa linear das polaridades |
|---|---|---:|---:|---:|---:|
| sentença | total | 1.512.063 | 0,61 | 0,66 | 0,45 |
| sentença | pt | 955.831 | 0,57 | 0,61 | 0,40 |
| sentença | en | 292.513 | 0,71 | 0,78 | 0,54 |
| sentença | es | 195.827 | 0,69 | 0,78 | 0,54 |
| sentença | demais | 67.892 | 0,65 | 0,75 | 0,53 |
| anúncio × aspecto | total | 160.995 | 0,69 | 0,79 | 0,55 |
| anúncio × aspecto | idioma predominante: pt | 122.699 | 0,66 | 0,77 | 0,53 |
| anúncio × aspecto | idioma predominante: en | 23.467 | 0,79 | 0,87 | 0,60 |
| anúncio × aspecto | idioma predominante: es | 11.874 | 0,77 | 0,86 | 0,60 |
| anúncio × aspecto | idioma predominante: demais | 2.955 | 0,80 | 0,85 | 0,57 |

### 4.3 Regra pré-registrada e modelo principal

*Abas da planilha:* `Diferenca_B_menos_A`, `Config`.

Antes de rodar o modelo B, registramos a regra de escolha do modelo principal: **B seria o principal se o intervalo de 95% (bootstrap estratificado) da diferença B − A no kappa ponderado linear populacional de sentimento excluísse zero a favor de B; caso contrário, o principal seria A**,
com o outro modelo sempre reportado como robustez. O resultado: a diferença B − A é −0,141 (IC 95% [−0,272; −0,012]), isto é, o intervalo exclui zero, mas **a favor de A**. Pela regra, o modelo principal é **A**. Na acurácia populacional a diferença é
−0,023 [−0,078; 0,021], e só em português, no kappa ponderado linear, −0,169 [−0,323; 0,011], intervalo que inclui zero. A seção 4.1 mostra
por que a escolha não é óbvia (B é melhor na amostra, A na população); a regra foi fixada antes de ver os resultados justamente para não escolher o resultado mais conveniente. Daqui em diante o modelo principal é A, e os resultados de B aparecem lado a lado nas abas com sufixo `_mB` e nas abas `LadoALado_*`.

### 4.4 Validade de construto: concordância com as subnotas oficiais

*Abas da planilha:* `Validacao_Construto`, `LadoALado_validacao_construto`, `Val_Volume_Convergente`, `Val_Confiab_AUC`, `Val_Recortes`.

A evidência indireta mais importante é a concordância com as subnotas que os próprios hóspedes deram. Para cada aspecto com subnota correspondente, correlacionamos, no nível do anúncio, o sentimento do aspecto com a subnota (não há limiar de aprovação; interessam a força e o sinal),
e a satisfação geral com a nota global:

| Aspecto | Subnota | n | Spearman (A) | Pearson (A) | Spearman (B) | Pearson (B) |
|---|---|---:|---:|---:|---:|---:|
| Limpeza | cleanliness | 19.095 | 0,45 | 0,58 | 0,42 | 0,52 |
| Localização | location | 24.101 | 0,24 | 0,31 | 0,24 | 0,27 |
| Check-in | checkin | 8.919 | 0,42 | 0,40 | 0,43 | 0,42 |
| Comunicação | communication | 25.418 | 0,30 | 0,44 | 0,30 | 0,43 |
| Custo-benefício | value | 3.552 | 0,24 | 0,26 | 0,22 | 0,23 |
| Precisão do anúncio | accuracy | 16.638 | 0,17 | 0,22 | 0,15 | 0,21 |
| Satisfação geral | rating (nota global) | 26.378 | 0,34 | 0,52 | 0,26 | 0,38 |

Todos os coeficientes são positivos e significativos nos dois modelos; a concordância é moderada, de 0,17 a 0,45 em A e de 0,15 a 0,43 em B, sem um modelo sistematicamente melhor (B é um pouco maior em check-in e comunicação; A, em limpeza,
custo-benefício e, sobretudo, satisfação geral). Ela deve ser lida à luz de que as subnotas também são comprimidas (muitos empates em 5,0), o que atenua as correlações. Cinco verificações de robustez:

- **Por volume de avaliações.** No modelo A, a concordância dos anúncios com até 30 avaliações (em que o sentimento usa todas) difere da dos anúncios com mais de 30 em no máximo 0,11 (Check-in), sem padrão sistemático; em B o resultado é análogo.
- **Convergente e discriminante.** A subnota correspondente é a mais correlacionada com o aspecto em 5 de 7 casos em A e em 3 de 7 em B (nos demais fica em segundo ou terceiro lugar, porque as subnotas são muito correlacionadas entre si, o chamado efeito halo). Controlando a nota global
  (correlação parcial), resta informação específica em limpeza (0,17), localização (0,22), check-in (0,23) e comunicação (0,15), e quase nenhuma em custo-benefício (0,08) e precisão (0,04).
- **Subnotas saturadas.** A probabilidade de o sentimento ser maior nos anúncios de subnota 5 do que nos de subnota menor (AUC) vai de 0,57 a 0,69 em A e de 0,55 a 0,67 em B.
- **Idioma e tipo de acomodação.** No modelo A, as correlações são positivas em português, inglês e espanhol (de 0,13 a 0,45) e em casa/apartamento inteiro e quarto privado (de 0,17 a 0,46), o que sustenta o uso de modelos multilíngues.
- **Atenuação.** A confiabilidade split-half do sentimento por aspecto (metades das avaliações de cada anúncio, com Spearman-Brown) é baixa: de 0,10 a 0,40 em A e de 0,06 a 0,40 em B. Correlações corrigidas por essa atenuação
  (de 0,57 a 0,96 em A; em B, até 1,20) são apenas ilustrativas, porque com confiabilidades tão baixas a correção é instável e corrige só o lado do sentimento.

### 4.5 Checagem com um segundo método de tópicos (LDA)

*Abas da planilha:* `Checagem_LDA`, `Topicos_LDA`.

Para saber se os resultados por aspecto dependem do método de tópicos, atribuímos cada sentença ao tópico dominante do LDA (10 tópicos) e comparamos. O mapa tópico LDA → aspecto foi **confirmado pelo pesquisador** (`data/mapa_lda_para_confirmar.xlsx`, sem alterações): só recebe aspecto o tópico cuja leitura das palavras de maior peso, aspecto mais similar aos termos-semente
e margem entre o primeiro e o segundo aspecto (≥ 0,05) concordam; senão é "misto" e fica fora do perfil. Apenas 4 dos 10 tópicos receberam aspecto (comodidades, comunicação, satisfação geral e localização), e 55% das sentenças caem em tópicos mistos, de modo que o LDA só permite checar esses quatro aspectos.
Entre as sentenças com aspecto nos dois métodos, 68,8% recebem o mesmo aspecto.

| Aspecto (LDA) | Spearman do perfil BERTopic × LDA | Spearman com a subnota (LDA) | Spearman com a subnota (BERTopic) | Parcela do R² (LDA) | Parcela do R² (BERTopic) |
|---|---:|---:|---:|---:|---:|
| Localização | 0,61 | 0,20 | 0,24 | 1,6% | 0,9% |
| Comunicação | 0,54 | 0,28 | 0,30 | 22,7% | 15,5% |
| Comodidades | 0,67 | — (sem subnota) | — | 62,3% | 59,0% |
| Satisfação geral | 0,46 | 0,19 | 0,34 | 13,4% | 24,6% |

O sinal da validade de construto se mantém nos três aspectos que têm subnota (localização, comunicação e satisfação geral), com correlações do mesmo tamanho nos dois mais específicos e menores em satisfação geral. Na decomposição do R² da nota global, comodidades fica em primeiro nos dois métodos; satisfação geral e comunicação trocam de posição (correlação de postos 0,80, com apenas quatro aspectos).

### 4.6 O que é confiável e o que pede cautela

*Abas da planilha:* `Aspecto_Rotuladas`, `Validacao_Construto`, `LadoALado_validacao_construto`, `Segundo_Anotador`.

Resumindo as evidências, classificamos cada aspecto com um critério descritivo, fixado antes das seções seguintes: **confiável** se a precisão de atribuição na amostra é de ao menos 0,60 e a correlação com a subnota correspondente é de ao menos 0,20 nos dois modelos; **cautela** nos demais casos.

| Aspecto | Precisão da atribuição (amostra) | Spearman com a subnota (A) | Spearman com a subnota (B) | Classificação | Critério |
|---|---:|---:|---:|---|---|
| Limpeza | 67% | 0,45 | 0,42 | confiável | precisão ≥ 0,60 e correlação ≥ 0,20 com a subnota nos dois modelos |
| Localização | 74% | 0,24 | 0,24 | confiável | precisão ≥ 0,60 e correlação ≥ 0,20 com a subnota nos dois modelos |
| Check-in | 56% | 0,42 | 0,43 | cautela | precisão de atribuição < 0,60 |
| Comunicação | 44% | 0,30 | 0,30 | cautela | precisão de atribuição < 0,60 |
| Custo-benefício | 74% | 0,24 | 0,22 | confiável | precisão ≥ 0,60 e correlação ≥ 0,20 com a subnota nos dois modelos |
| Ruído e conforto | 44% | — | — | cautela | sem subnota correspondente: não validável |
| Segurança | 48% | — | — | cautela | sem subnota correspondente: não validável |
| Precisão do anúncio | 70% | 0,17 | 0,15 | cautela | correlação < 0,20 com a subnota em ao menos um modelo |
| Comodidades | 44% | — | — | cautela | sem subnota correspondente: não validável |
| Satisfação geral | 41% | 0,34 | 0,26 | cautela | precisão de atribuição < 0,60 |

São confiáveis: Limpeza, Localização, Custo-benefício. Pedem cautela: Check-in, Comunicação, Ruído e conforto, Segurança, Precisão do anúncio, Comodidades, Satisfação geral. Duas consequências valem para as seções 5 a 7. Primeiro, o aspecto de maior peso na seção 5, comodidades, pede cautela (atribuição imprecisa e sem subnota para validar); por isso a leitura prática da seção 5 se apoia nos tópicos finos de queixa e
elogio, cuja atribuição é melhor (tópicos diretos, 65% de acerto de aspecto), e os pesos por aspecto são apresentados como indicativos. Segundo, nenhum resultado por aspecto deve ser lido sem a classificação ao lado. Um segundo anotador rotulou, sem ver as classificações do primeiro nem dos modelos, 100 frases da amostra. A concordância no sentimento é de 91% (kappa de Cohen 0,86, IC [0,76; 0,94]; kappa ponderado linear 0,88) e, no aspecto, de 67% (kappa 0,62, IC [0,51; 0,73]). Os dois anotadores concordam bem no sentimento e só moderadamente no aspecto, o que é coerente com a classificação acima: a concordância é baixa justamente em satisfação geral (19%, n = 16, em geral confundida com o grupo geral) e em limpeza (33%, n = 6), e é alta em custo-benefício e precisão do anúncio (100% nos dois). A amostra de 100 frases é pequena, e as concordâncias por aspecto têm de 4 a 20 frases.

## 5. O que o texto revela sobre a nota

*Abas da planilha:* `Imp_Aspectos`, `Imp_Modelos`, `Imp_Segmentos_Sens`, `Imp_Topicos_Queixas`, `Imp_Topicos_Elogios`, `LadoALado_imp_lmg`, `LadoALado_imp_gbm`, `LadoALado_imp_logit`, `LadoALado_imp_segmentos`, `LadoALado_imp_sensibilidade`.

Estabelecido quais medidas merecem confiança (seção 4.6), esta seção apresenta a contribuição central do estudo: **o que o texto das avaliações revela sobre a nota que o anúncio recebe**. Primeiro, quais aspectos mais se associam à nota global e a cada subnota; depois, quais tópicos finos concentram as queixas
e os elogios. Tudo é associação, não causa.

### 5.1 Importância dos aspectos

*Abas da planilha:* `Imp_Aspectos`, `Imp_Modelos`, `Imp_Segmentos_Sens`, `LadoALado_imp_lmg`, `LadoALado_imp_gbm`, `LadoALado_imp_logit`, `LadoALado_imp_segmentos`, `LadoALado_imp_sensibilidade`.

A análise usa os 28.889 anúncios com texto, inclusive os de pouco texto (o sentimento não observado de um aspecto é imputado pela média, e isso evita exigir três aspectos por anúncio), e toma como alvo o percentil da nota (a nota é comprimida no topo). A decomposição
LMG (média de Shapley) reparte o R² da regressão da nota global sobre o sentimento dos dez aspectos; o R² total é de 0,320 em A e 0,291 em B. Parcela de cada aspecto:

| Aspecto | Parcela do R² (A) | Parcela do R² (B) | Classificação (seção 4.6) |
|---|---:|---:|---|
| Comodidades | 42,5% | 47,8% | cautela |
| Limpeza | 19,6% | 18,8% | confiável |
| Satisfação geral | 17,5% | 9,9% | cautela |
| Comunicação | 11,3% | 12,6% | cautela |
| Check-in | 3,4% | 4,9% | cautela |
| Ruído e conforto | 3,1% | 3,6% | cautela |
| Precisão do anúncio | 1,7% | 1,1% | cautela |
| Localização | 0,6% | 0,8% | confiável |
| Custo-benefício | 0,3% | 0,4% | confiável |
| Segurança | 0,1% | 0,1% | cautela |

**Comodidades** responde por 42,5% do R² em A e 47,8% em B, seguida por limpeza (19,6% e 18,8%); satisfação geral e comunicação vêm depois. Localização, custo-benefício e segurança quase não contribuem para a
**nota global**, embora localização seja o aspecto que mais explica a sua própria subnota (tabela abaixo): o hóspede avalia o local em separado, e a nota global parece refletir mais o que ele viveu dentro do imóvel. A ordem das parcelas é muito parecida entre os modelos (correlação de postos 0,99); a diferença mais
visível é a satisfação geral, que pesa menos em B. Ressalvas da seção 4.6: comodidades e satisfação geral estão na classe "cautela", e a importância relativa de um aspecto mistura efeito e confiabilidade da medida (aspectos pouco citados, como segurança e custo-benefício, são medidos com mais erro e imputados na maioria dos anúncios).

Para cada subnota, o aspecto correspondente está entre os que mais a explicam (modelo A, com a parcela também em B):

| Subnota | R² total (A) | Aspecto correspondente | Sua parcela (A) | Sua parcela (B) | Aspecto de maior parcela (A) |
|---|---:|---|---:|---:|---|
| cleanliness | 0,229 | Limpeza | 33,3% | 30,7% | Comodidades |
| location | 0,093 | Localização | 41,8% | 38,3% | Localização |
| checkin | 0,163 | Check-in | 11,9% | 14,5% | Comodidades |
| communication | 0,211 | Comunicação | 22,1% | 24,5% | Comodidades |
| value | 0,239 | Custo-benefício | 0,7% | 0,7% | Comodidades |
| accuracy | 0,258 | Precisão do anúncio | 2,1% | 1,4% | Comodidades |

Dois modelos mais flexíveis dão a mesma leitura. Um GBM com valores ausentes tem R² fora da amostra de 0,442 em A e 0,416 em B (regressão linear com imputação: 0,388 e 0,363); a queda de R² por permutação é maior em
Comodidades (0,233), Limpeza (0,078) e Satisfação geral (0,075) no modelo A. Na regressão logística para "nota ≥ 4,9" (que 51% dos anúncios têm; AUC fora da amostra 0,815 em A e 0,802 em B), um desvio-padrão a mais de sentimento
multiplica as chances de nota alta por 2,46 em comodidades, 1,91 em limpeza, 1,47 em satisfação geral e 1,37 em comunicação (A); em B, 2,49, 1,65, 1,21 e 1,36.

O resultado é estável. Comodidades é o aspecto de maior parcela em 11 dos 11 segmentos (tipo de acomodação, idioma predominante e os seis maiores bairros) em A e em 11 dos 11 em B, com parcela de 37% a 43% (A) e de
38% a 49% (B); e é o de maior parcela em 5 das 5 sensibilidades (todos os anúncios, só tópicos diretos, até 30 avaliações, ao menos 3 aspectos, sem satisfação geral como preditor) em A e em 5 das 5 em B.

### 5.2 Queixas e elogios por tópico

*Abas da planilha:* `Imp_Topicos_Queixas`, `Imp_Topicos_Elogios`, `RSyn_Resumo_AB`.

A leitura prática está nos tópicos finos, cuja atribuição de aspecto é mais precisa (tópicos diretos). Para cada tópico, comparamos o percentil da nota entre anúncios com e sem ao menos uma menção negativa (ou positiva) no tópico, controlando o volume de avaliações e de frases; as 68 queixas e 181 elogios com
amostra suficiente foram testados com correção de Benjamini-Hochberg (56 queixas e 123 elogios com q < 0,05 no sentido esperado). Queixas de maior peso (efeito × prevalência), modelo A:

| Tópico (palavras de maior peso) | Aspecto (classificação) | Anúncios com menção | Efeito no percentil da nota | q (BH) |
|---|---|---:|---:|---:|
| banheiro, chuveiro, água, box | Comodidades (cautela) | 14% | −20,3 pontos | 0,000 |
| condicionado, aire, acondicionado, calor | Comodidades (cautela) | 13% | −17,7 pontos | 0,000 |
| sujo, limpeza, chão, dirty | Limpeza (confiável) | 7% | −26,4 pontos | 0,000 |
| infelizmente, leave, disappointed, problemas | Satisfação geral (cautela) | 9% | −20,0 pontos | 0,000 |
| cozinha, cozinhar, kitchen, cocina | Comodidades (cautela) | 7% | −19,1 pontos | 0,000 |
| anfitrião, anfitriã, hóspedes, host | Comunicação (cautela) | 5% | −22,9 pontos | 0,000 |
| barulho, noise, ruido, noisy | Ruído e conforto (cautela) | 11% | −9,7 pontos | 0,000 |
| cheiro, mofo, forte, olor | Limpeza (confiável) | 5% | −21,8 pontos | 0,000 |
| cama, bed, camas, casal | Comodidades (cautela) | 5% | −17,8 pontos | 0,000 |
| dormir, cortina, luz, cortinas | Ruído e conforto (cautela) | 5% | −15,7 pontos | 0,000 |
| reparos, precisa, manutenção, melhorias | Comodidades (cautela) | 3% | −21,5 pontos | 0,000 |
| wifi, sinal, senha, único | Comodidades (cautela) | 3% | −19,5 pontos | 0,000 |
| airbnb, experiência, experience, airbnbs | Satisfação geral (cautela) | 3% | −21,4 pontos | 0,000 |

Chamam atenção as queixas de instalações e manutenção (banheiro, ar-condicionado, cozinha, cama, wi-Fi, reparos), de limpeza (sujeira, cheiro) e de resposta do anfitrião, que se associam a quedas de 10 a 26 pontos no percentil da nota entre os anúncios que as recebem. Entre as **15 queixas de maior peso**, 13 coincidem nos dois modelos: a lista é robusta à escolha do modelo
(em A e não em B: reparos, precisa, manutenção; repelente, cocina, kitchen; em B e não em A: check, checkout, flexível; reserva, paguei, cheguei). Elogios mais associados a notas altas, modelo A:

| Tópico (palavras de maior peso) | Aspecto (classificação) | Anúncios com menção | Efeito no percentil da nota | q (BH) |
|---|---|---:|---:|---:|
| anfitriã, anfitrião, host, anfitriões | Comunicação (cautela) | 84% | +8,5 pontos | 0,000 |
| rio, janeiro, río, rock | Satisfação geral (cautela) | 56% | +7,5 pontos | 0,000 |
| casa, senti, sentimos, sentir | Satisfação geral (cautela) | 34% | +10,9 pontos | 0,000 |
| voltaremos, voltar, esperamos, iremos | Satisfação geral (cautela) | 44% | +8,2 pontos | 0,000 |
| agradeço, gracias, agradecer, atenção | Comunicação (cautela) | 31% | +5,7 pontos | 0,000 |
| limpo, organizado, limpio, clean | Limpeza (confiável) | 34% | +4,8 pontos | 0,000 |

A queixa genérica ("decepcionado, problemas") e os elogios genéricos (sentir-se em casa, voltar) pertencem a satisfação geral, aspecto de cautela, e servem sobretudo como termômetro.

### 5.3 Cuidados de interpretação
Sem rótulo causal: um anúncio com queixa de banheiro tem nota menor, mas isto não quer dizer que consertar o banheiro eleve a nota. O "efeito" é a diferença média, na cidade, entre anúncios com e sem a menção, controlada por volume. A atribuição de aspecto acerta entre 52% e
66% na população (seção 4.1), e a importância por aspecto fica abaixo da dos tópicos, o que reforça a leitura por tópico.

## 6. Aplicação: diagnóstico por anúncio

*Abas da planilha:* `Benchmark_Bairro_Tipo`.

A seção 5 diz o que se associa à nota; esta mostra como um anfitrião ou uma empresa gestora usa isso. A ferramenta `diagnostico.py` gera, a pedido, o relatório de **um** anúncio: o sentimento médio em cada aspecto e a posição (percentil) entre anúncios do mesmo bairro e tipo de acomodação (ou do tipo na cidade, quando o bairro
tem poucos anúncios); a evidência de cada aspecto (poucas frases, evidência baixa, sem rótulo de força ou atenção); as queixas e os elogios recorrentes do anúncio, com a associação média, na cidade, desses tópicos com o percentil da nota (seção 5.2); e a evolução do sentimento nas avaliações mais recentes. A ferramenta funciona
também para anúncios novos, marcando a evidência como baixa em vez de omitir o aspecto.

Para a comparação, a Etapa 17 construiu tabelas de referência: 66 grupos de bairro e tipo de acomodação com ao menos 30 anúncios e 3 grupos por tipo na cidade (aba `Benchmark_Bairro_Tipo`), com mediana e quartis do sentimento por aspecto e da nota. O relatório respeita a classificação da seção 4.6: a nota metodológica que o acompanha informa a precisão
da atribuição por aspecto, e os aspectos de cautela não devem orientar decisões isoladamente (os confiáveis são Limpeza, Localização, Custo-benefício). Três exemplos anonimizados (um anúncio de nota alta, um de nota baixa e um com poucas avaliações) estão em `redacao/exemplos_diagnostico/`: no de nota baixa, o relatório aponta
comodidades e satisfação geral muito abaixo dos pares e as queixas de banheiro e cozinha; no de poucas avaliações, a maior parte dos aspectos aparece com evidência baixa. O relatório prioriza onde investigar, e não prevê nota nem prescreve causas.

## 7. Um índice único acrescenta algo?

*Abas da planilha:* `RSyn_Resumo_AB`, `Descritivo_Teto`, `Selecao_Teto`, `Analise_A`, `Analise_A_mB`, `Analise_A_Intersecao`, `Comparacoes_Multiplas`, `Analise_B`, `Analise_B_mB`, `Sensibilidade`, `Sensibilidade_mB`, `Limite_30_Avaliacoes`.

Com a seção 5 estabelecida, resta uma pergunta secundária: o que se ganha ao resumir o perfil de aspectos em **um número**, um índice sintético que substitua a nota oficial? É um resultado secundário, e um resultado nulo seria legítimo: a decomposição por aspecto da seção 5 é a contribuição do estudo, e o índice sintético apenas a testa.

### 7.1 Construção
O índice sintético (R_syn) é a média igual dos sentimentos dos aspectos disponíveis do anúncio, em estrelas de 1 a 5, exigindo ao menos 3 aspectos específicos com evidência (a satisfação geral entra na média, mas não conta para o mínimo). Há 22.564 anúncios com R_syn.
A especificação principal **não** aplica shrinkage (encolhimento empírico-bayesiano com m = 23, a mediana de avaliações), por uma razão teórica: o encolhimento puxa os anúncios de poucas avaliações para a média global e, com isso, correlaciona o índice com o volume de avaliações justamente onde a nota é 5,0 (os anúncios de nota 5,0 têm mediana de
9 avaliações, contra 31 nos demais): entre eles, a correlação de postos do índice com o log do volume é 0,50 com shrinkage e −0,04 sem (0,45 e 0,03 em B).
Registramos que **essa decisão foi tomada depois de ver o resultado** com shrinkage; por isso as duas versões são reportadas (seção 7.5).

### 7.2 Compressão da nota oficial e reordenamento

*Abas da planilha:* `RSyn_Resumo_AB`, `Selecao_Teto`.

A nota oficial concentra 22,8% dos anúncios com R_syn no valor 5,0; o valor mais comum do índice sintético concentra 1,6% em A e 1,9% em B. A correlação de postos entre R_syn e a nota oficial é 0,62 em A e 0,58 em B; 61% (A) e
63% (B) dos anúncios mudam 10 pontos percentuais de posto ou mais entre os dois rankings. Os R_syn de A e de B têm correlação de postos 0,82. Entre os anúncios de nota exatamente 5,0 com R_syn (5.142), o índice espalha os anúncios entre o percentil
27 e o 98 (5º a 95º; B: 22 e 98) e concorda fracamente, mas de forma positiva, com as seis subnotas (correlação de postos de 0,08 a 0,12 em A e de 0,04 a 0,10 em B; as subnotas também são saturadas).

**Quem entra no teto.** Essa discriminação vale para os anúncios de nota 5,0 **que têm R_syn**: 5.142 dos 9.373 anúncios de nota 5,0 (54,9%). Os que ficam de fora são sobretudo os de pouquíssimas avaliações, que são justamente os mais comprimidos:

| Característica (nota 5,0) | Com R_syn | Sem R_syn |
|---|---:|---:|
| Anúncios | 5.142 | 4.231 |
| Avaliações totais (mediana) | 9 | 3 |
| Preço (mediana) | 345 | 331 |
| Casa ou apartamento inteiro | 81% | 72% |
| Quarto privado | 18% | 26% |
| Português predominante | 74% | 73% |

### 7.3 Poder explicativo sobre os índices de volume

*Abas da planilha:* `Analise_A`, `Analise_A_mB`, `Analise_A_Intersecao`, `Comparacoes_Multiplas`, `Descritivo_Teto`.

Os controles são o volume total de avaliações (log), o preço (log), o tipo de acomodação e o bairro; **não** se controla pelas avaliações dos últimos 12 meses (seção 2). A validação é fora da amostra, com 5 dobras repetidas 5 vezes, mesma semente e mesmas dobras em todos os modelos. M0 são os controles; M1 acrescenta a nota oficial; M2 acrescenta o R_syn
no lugar da nota; M3 acrescenta os dois. No índice de ocupação, na amostra completa, os controles têm R² fora da amostra de 0,475, e a nota oficial o eleva a 0,483. Ganho de R² fora da amostra (média entre dobras e intervalo de 2,5% a 97,5% entre dobras):

| Desfecho | Escopo | M1 − M0: nota oficial (A) | M2 − M1: R_syn no lugar da nota (A) | M3 − M1: R_syn além da nota (A) | M3 − M1 (B) |
|---|---|---|---|---|---|
| Índice de ocupação | amostra completa | +0,0079 [+0,0052; +0,0099] | −0,0050 [−0,0070; −0,0020] | +0,0000 [−0,0005; +0,0002] | +0,0002 [−0,0007; +0,0006] |
| Índice de ocupação | nota ≥ 4,8 | +0,0063 [+0,0038; +0,0091] | −0,0059 [−0,0083; −0,0033] | +0,0000 [−0,0003; +0,0002] | +0,0002 [−0,0005; +0,0006] |
| Índice de ocupação | nota ≥ 4,9 | +0,0033 [+0,0009; +0,0057] | −0,0033 [−0,0055; −0,0010] | −0,0001 [−0,0003; +0,0000] | +0,0000 [−0,0006; +0,0002] |
| Índice de ocupação | nota = 5,0 | +0,0000 [+0,0000; +0,0000] | −0,0002 [−0,0009; +0,0000] | −0,0002 [−0,0009; +0,0000] | −0,0002 [−0,0007; +0,0000] |
| Índice de receita (log) | amostra completa | +0,0174 [+0,0089; +0,0239] | −0,0132 [−0,0206; −0,0050] | +0,0010 [−0,0013; +0,0025] | +0,0014 [−0,0015; +0,0027] |
| Índice de receita (log) | nota ≥ 4,8 | +0,0039 [−0,0001; +0,0073] | −0,0037 [−0,0080; +0,0009] | −0,0002 [−0,0012; +0,0001] | −0,0002 [−0,0008; +0,0000] |
| Índice de receita (log) | nota ≥ 4,9 | +0,0009 [−0,0015; +0,0028] | −0,0002 [−0,0029; +0,0029] | +0,0004 [−0,0010; +0,0012] | +0,0004 [−0,0016; +0,0015] |
| Índice de receita (log) | nota = 5,0 | +0,0000 [+0,0000; +0,0000] | +0,0019 [−0,0040; +0,0059] | +0,0019 [−0,0040; +0,0059] | +0,0016 [−0,0019; +0,0040] |
| Avaliações em 12 meses (log) | amostra completa | +0,0163 [+0,0108; +0,0208] | −0,0116 [−0,0157; −0,0067] | +0,0006 [−0,0009; +0,0014] | +0,0012 [−0,0008; +0,0025] |
| Avaliações em 12 meses (log) | nota ≥ 4,8 | +0,0060 [+0,0033; +0,0088] | −0,0055 [−0,0088; −0,0026] | −0,0001 [−0,0005; +0,0001] | +0,0001 [−0,0008; +0,0006] |
| Avaliações em 12 meses (log) | nota ≥ 4,9 | +0,0028 [−0,0008; +0,0059] | −0,0020 [−0,0045; +0,0014] | +0,0003 [−0,0004; +0,0007] | +0,0000 [−0,0006; +0,0002] |
| Avaliações em 12 meses (log) | nota = 5,0 | +0,0000 [+0,0000; +0,0000] | +0,0015 [−0,0020; +0,0041] | +0,0015 [−0,0020; +0,0041] | +0,0005 [−0,0018; +0,0017] |

A nota oficial acrescenta um poder explicativo pequeno, mas detectável (nos três desfechos, na amostra completa); o R_syn, no lugar dela, explica menos; e **o R_syn não acrescenta poder explicativo além da nota oficial**: o intervalo de M3 − M1 exclui zero em 0 das 12 comparações em A e em 0 em B. Restritos aos 22.564
anúncios com R_syn nos dois modelos, as diferenças M3 − M1 entre A e B são de no máximo 0,0010 (aba `Analise_A_Intersecao`).

**Coeficientes dentro da amostra.** Em M3, o coeficiente padronizado de R_syn (erro-padrão robusto HC3) aparece significativo em vários desfechos e escopos; reunimos os 12 de cada modelo em uma família e aplicamos Benjamini-Hochberg:

| Desfecho | Escopo | Coef. de R_syn (A) | p (A) | q (A) | Coef. de R_syn (B) | p (B) | q (B) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Índice de ocupação | amostra completa | −0,919 | 0,0617 | 0,1058 | −1,636 | 0,0007 | 0,0027 |
| Índice de ocupação | nota ≥ 4,8 | −0,716 | 0,1255 | 0,1882 | −1,252 | 0,0055 | 0,0132 |
| Índice de ocupação | nota ≥ 4,9 | −0,236 | 0,6424 | 0,6855 | −0,654 | 0,1808 | 0,2411 |
| Índice de ocupação | nota = 5,0 | +0,188 | 0,6855 | 0,6855 | −0,190 | 0,6797 | 0,6797 |
| Índice de receita (log) | amostra completa | −0,129 | 0,0000 | 0,0000 | −0,143 | 0,0000 | 0,0000 |
| Índice de receita (log) | nota ≥ 4,8 | −0,016 | 0,4550 | 0,5460 | −0,011 | 0,6167 | 0,6728 |
| Índice de receita (log) | nota ≥ 4,9 | +0,058 | 0,0218 | 0,0435 | +0,063 | 0,0165 | 0,0248 |
| Índice de receita (log) | nota = 5,0 | +0,141 | 0,0004 | 0,0012 | +0,120 | 0,0047 | 0,0132 |
| Avaliações em 12 meses (log) | amostra completa | −0,037 | 0,0000 | 0,0000 | −0,052 | 0,0000 | 0,0000 |
| Avaliações em 12 meses (log) | nota ≥ 4,8 | −0,005 | 0,4280 | 0,5460 | −0,016 | 0,0140 | 0,0241 |
| Avaliações em 12 meses (log) | nota ≥ 4,9 | +0,020 | 0,0056 | 0,0133 | +0,008 | 0,2866 | 0,3440 |
| Avaliações em 12 meses (log) | nota = 5,0 | +0,040 | 0,0000 | 0,0001 | +0,026 | 0,0073 | 0,0145 |

Com a correção, 6 de 12 coeficientes têm q < 0,05 em A e 8 em B. Eles **não são robustos**: mudam de sinal conforme o escopo (negativos na amostra completa, positivos em parte dos tetos) e conforme o modelo de sentimento (por exemplo, no índice de ocupação da amostra completa, o coeficiente não é significativo em A e é negativo e significativo em B), e não se
confirmam fora da amostra (os ganhos M3 − M1 acima têm intervalos que incluem zero na quase totalidade das comparações). Por isso ficam fora da síntese e das conclusões.

### 7.4 Monotonicidade e reordenamento

*Abas da planilha:* `Analise_B`, `Analise_B_mB`.

O R_syn reordena os anúncios em relação à nota oficial (seção 7.2); a pergunta é se essa reordenação se associa ao desfecho. Correlação de postos entre cada medida e o índice de ocupação residualizado nos controles, por faixa da nota oficial:

| Faixa da nota oficial | n | ρ de R_syn × desfecho residual (A) | ρ de R_syn × desfecho residual (B) | ρ da nota oficial × desfecho residual | ρ de R_syn × nota oficial (A) | % que muda ≥ 10 pp de posto (A) |
|---|---:|---:|---:|---:|---:|---:|
| TODAS | 20.882 | 0,083 | 0,071 | 0,168 | 0,620 | 61% |
| [0; 4.5) | 1.285 | −0,086 | −0,108 | −0,176 | 0,427 | 30% |
| [4.5; 4.8) | 5.146 | −0,045 | −0,063 | 0,047 | 0,273 | 56% |
| [4.8; 4.9) | 4.704 | −0,036 | −0,063 | 0,018 | 0,134 | 73% |
| [4.9; 5) | 5.036 | −0,018 | −0,004 | 0,099 | 0,153 | 68% |
| = 5,0 | 4.711 | 0,025 | 0,028 | — | — | 55% |

Para os dois modelos, a associação do R_syn com o desfecho residual é pequena e muda de sinal entre faixas, e na faixa de nota 5,0 é próxima de zero. A regressão isotônica (relação monótona crescente, avaliada fora da amostra) tem R² de 0,029 para a nota oficial e 0,006 para o R_syn na amostra completa (B: 0,004),
e nos tetos é ≈ 0 para ambos (nota 5,0: −0,003 para o R_syn em A).

### 7.5 Sensibilidade

*Abas da planilha:* `Sensibilidade`, `Sensibilidade_mB`, `Limite_30_Avaliacoes`.

Ganho de R² do R_syn além da nota oficial no teto (nota = 5,0) e correlação de postos do índice com o desfecho (índice de ocupação) dentro da faixa de nota 5,0, para as seis variantes (shrinkage; com e sem satisfação geral; todos os anúncios ou só os de até 30 avaliações):

| Variante | Δ R² índice de ocupação (A) | Δ R² avaliações 12 m (A) [IC] | ρ bruto (A) | ρ residual (A) | Δ R² avaliações 12 m (B) | ρ bruto (B) |
|---|---:|---:|---:|---:|---:|---:|
| Sem shrinkage (principal) | −0,0002 | +0,0015 [−0,0020; +0,0041] | −0,01 | +0,03 | +0,0005 | +0,03 |
| Com shrinkage (m = 23) | +0,0001 | +0,0016 [−0,0026; +0,0044] | +0,35 | +0,02 | +0,0002 | +0,31 |
| Sem shrinkage, sem satisfação geral | −0,0002 | +0,0010 [−0,0011; +0,0032] | −0,02 | +0,02 | +0,0006 | +0,02 |
| Com shrinkage, sem satisfação geral | −0,0001 | +0,0011 [−0,0023; +0,0034] | +0,33 | +0,01 | +0,0004 | +0,31 |
| Sem shrinkage, só anúncios com até 30 avaliações | −0,0003 | +0,0013 [−0,0037; +0,0046] | +0,02 | +0,03 | +0,0007 | +0,05 |
| Com shrinkage, só anúncios com até 30 avaliações | −0,0003 | +0,0014 [−0,0043; +0,0052] | +0,26 | +0,04 | +0,0008 | +0,23 |

O ρ bruto de +0,35 com shrinkage é um artefato do encolhimento (seção 7.1); sem ele, e com o desfecho residualizado nos controles, o ρ é próximo de zero em todas as variantes. Excluir a satisfação geral
quase não muda os resultados. O limite de 30 avaliações por anúncio afeta 32% dos anúncios elegíveis (9.266), mas só 5,2% dos de nota 5,0; a confiabilidade do sentimento médio por anúncio é de 0,50
com 30 avaliações, 0,67 com 60 e 0,80 com 120, e não há deriva temporal relevante (estrelas médias de 4,345 nas 10 avaliações mais recentes e 4,368 nas 20 mais antigas).

### 7.6 Como ler o resultado
O resultado é nulo e secundário: o índice sintético não acrescenta poder explicativo sobre os índices de volume além da nota oficial, em nenhum dos dois modelos de sentimento. Há duas leituras, que não se excluem. A primeira é que **o sentimento do texto tem pouca razão teórica para prever uma contagem de avaliações**: os desfechos disponíveis são índices de volume (seção 2), e o nulo é em
parte consequência do desfecho que a base permite. A segunda é que **o valor do texto está na decomposição por aspecto da seção 5, e não em substituir a nota**: a nota oficial já resume bem a satisfação geral do hóspede, e o texto acrescenta o porquê. Em nenhum ponto este estudo apresenta o R_syn como "rating melhor".

## 8. Limitações

*Abas da planilha:* `Config`, `Estat_Corpus`, `Limite_30_Avaliacoes`, `Avaliacao_Rotuladas_AB`, `Aspecto_Rotuladas`, `Val_Confiab_AUC`, `Checagem_LDA`, `Segundo_Anotador`.

Reunimos aqui o que limita a leitura de todo o texto, na ordem das seções.

- **Recorte do corpus (seção 1).** O sentimento usa as 30 avaliações mais recentes de cada anúncio; 32% dos anúncios elegíveis (9.266) têm mais avaliações que o limite. O truncamento afeta pouco os de nota 5,0 (5,2%), mas reduz a confiabilidade do sentimento médio por anúncio (Spearman-Brown de 0,50 com 30 avaliações).
  Os dados só têm anúncios ativos na coleta, e as avaliações não indicam a data da estadia.
- **Desfechos (seção 2).** Não há ocupação nem receita observadas; os campos disponíveis são funções do número de avaliações recentes. Nenhum resultado fala de desempenho econômico.
- **Medição do texto (seções 3 e 4).** Os rótulos de referência vêm de um único pesquisador, que também revisou o mapa de tópicos para aspectos; um segundo anotador rotulou 100 frases (seção 4.6), com concordância moderada no aspecto (kappa 0,62), de modo que a atribuição de aspecto tem erro de rotulagem além do erro do modelo. A amostra rotulada tem 297 frases e, ponderada pela população, tamanho efetivo de cerca de 72 frases, de modo que os intervalos são largos e as
  comparações entre modelos são frágeis (a diferença de kappa B − A é de −0,141, com IC que mal exclui zero). A confiabilidade split-half do sentimento por aspecto é baixa, e as subnotas oficiais usadas como referência são comprimidas. Sete dos dez aspectos pedem cautela (seção 4.6); em especial, comodidades, o aspecto de maior peso,
  tem atribuição imprecisa e não tem subnota para validar. O mapa do LDA foi confirmado pelo pesquisador; o LDA só checa quatro aspectos.
- **Dois modelos de sentimento (seção 4).** O modelo A é o principal por uma regra fixada antes da execução do B, mas B é melhor na amostra rotulada e A na população; a escolha não é óbvia, e por isso os resultados de B acompanham todos os blocos. Onde os dois divergem (seção 7.3), as duas leituras são relatadas sem preferência.
- **Importância dos aspectos (seção 5).** A importância relativa de um aspecto mistura efeito e confiabilidade da medida, e as associações com a nota são entre anúncios, não dentro do anúncio; nada disso autoriza falar em causa. Anúncios sem aspectos suficientes têm sentimento imputado.
- **Índice sintético (seção 7).** Só 5.142 dos anúncios de nota 5,0 têm o índice, e os que ficam de fora têm menos avaliações; as conclusões sobre o teto valem para esse subconjunto. A decisão de não aplicar shrinkage foi tomada depois de ver o resultado com shrinkage. Coeficientes dentro da amostra não são robustos e não foram confirmados fora dela.
- **Generalização.** Um só município, uma só plataforma e uma só coleta.

## 9. Conclusões

*Abas da planilha:* `Avaliacao_Rotuladas_AB`, `Diferenca_B_menos_A`, `Validacao_Construto`, `Checagem_LDA`, `Segundo_Anotador`, `Imp_Aspectos`, `LadoALado_imp_lmg`, `Imp_Topicos_Queixas`, `RSyn_Resumo_AB`, `Selecao_Teto`, `Analise_A`, `Comparacoes_Multiplas`, `Config`.

As conclusões seguem a ordem da linha de raciocínio. Todas são associações, e todas valem com as ressalvas da seção 8.

1. **A medição do texto é utilizável, com restrições.** Em 297 frases rotuladas por um pesquisador, a acurácia populacional do sentimento é de 87% no modelo A e 85% no B, e o kappa ponderado populacional é 0,66 e 0,51. Pela regra fixada antes da execução do B (diferença de kappa B − A de −0,141, IC [−0,272; −0,012]), o modelo principal é A, e B acompanha todos os resultados. Os dois modelos concordam em ordenar
   frases e anúncios, mas não são intercambiáveis. O sentimento dos aspectos concorda com as subnotas oficiais de forma moderada e positiva; só Limpeza, Localização, Custo-benefício satisfazem o critério de confiança da seção 4.6, e Check-in, Comunicação, Ruído e conforto, Segurança, Precisão do anúncio, Comodidades, Satisfação geral pedem cautela. Um segundo método de tópicos (LDA) reproduz o sinal nos aspectos que consegue checar. Entre dois anotadores, a concordância é alta no sentimento (kappa 0,86) e moderada no aspecto (0,62).
2. **O texto das avaliações revela o que se associa à nota.** Nos dois modelos, comodidades é o aspecto de maior parcela do R² da nota global (42% em A e 48% em B), seguida de limpeza (20% e 19%), e isso se mantém em todos os segmentos e sensibilidades.
   Como comodidades pede cautela, a leitura que mais se sustenta é a dos tópicos finos: 13 das 15 queixas de maior peso são as mesmas nos dois modelos (banheiro e chuveiro, ar-condicionado, sujeira, cozinha, cheiro, cama, wi-Fi, resposta do anfitrião), associadas a quedas de 10 a 26 pontos no percentil da nota.
3. **A decomposição é aplicável ao anúncio.** O diagnóstico por anúncio (seção 6) compara cada aspecto com anúncios do mesmo bairro e tipo, mostra a evidência de cada um e as queixas e elogios recorrentes, e indica onde investigar, sem prever nota nem prescrever causas.
4. **Um índice único não acrescenta poder explicativo.** O índice sintético reordena os anúncios em relação à nota oficial e discrimina os anúncios de nota 5,0 que o têm (5.142 de 9.373), mas não acrescenta poder explicativo sobre os índices de volume além da nota oficial, em nenhum dos dois modelos. O resultado é nulo e secundário, com duas leituras que não se excluem: o sentimento tem pouca razão teórica para
   prever uma contagem de avaliações, e o valor do texto está na decomposição por aspecto. Os coeficientes dentro da amostra não são robustos e ficam fora desta síntese.

O que o estudo **não** conclui: que o índice sintético seja um "rating melhor", que consertar um problema aponte para aumento de nota, que haja efeito sobre receita ou ocupação.
