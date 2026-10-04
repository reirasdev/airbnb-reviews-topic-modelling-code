# Resultados (rascunho para a dissertação)

> **Revisão 2026-10-04 (importante):** a seção 7.1 e a seção 10 foram corrigidas após descobrirmos que a ocupação e a
> receita estimadas são funções exatas de variáveis do próprio anúncio (ver `02_investigacao_coeficiente_negativo.md`). A
> Análise A da seção 7 inclui o controle de avaliações dos últimos 12 meses, que torna o desfecho quase determinístico; a
> seção 7.1 traz a versão sem esse controle, **recomendada como principal (pendente de confirmação do pesquisador)**.
>
> **Status:** rascunho gerado a partir da execução `run_20261004_132021` (Excel `resultados_20261004_132021.xlsx`) e da
> investigação `run_20261004_135242`. Todos os números vêm das abas do Excel / `historico/HISTORICO_DECISOES.md`.
> Trechos marcados **[conferir]** dependem de informação externa ao pipeline. Trabalho de **mensuração e associação**;
> nenhuma afirmação causal.

## 1. Dados e amostra

O estudo usa 42.013 anúncios do Airbnb no Rio de Janeiro e 995.072 avaliações textuais. Dos anúncios, 33.140 têm nota
oficial e subnotas; após exigir nota maior que zero e ao menos duas avaliações (`MIN_REVIEWS = 2`), restaram **28.890
anúncios elegíveis**. Para conter o custo computacional, o sentimento foi calculado sobre as **30 avaliações mais recentes
de cada anúncio**: 475.858 avaliações (após remover 1 avaliação automática e 311 duplicatas), divididas em **1.512.063
sentenças** (1.366.091 textos únicos; 3,18 sentenças por avaliação em média, 12,4 tokens por sentença).

Idiomas das avaliações usadas (detecção por avaliação): português 66,2%, inglês 15,5%, espanhol 14,2%, francês 2,4%,
alemão 1,1%, italiano 0,3%, indeterminado 0,3%. O corpus não foi separado por idioma.

A nota oficial é fortemente comprimida: entre os anúncios analisados, 22,8% têm nota exatamente 5,0 (média 4,82; desvio-padrão
0,22).

## 2. Sentimento por sentença

Um único modelo multilíngue (`cardiffnlp/twitter-xlm-roberta-base-sentiment`, três classes) foi aplicado a cada sentença; a
saída foi convertida em estrelas esperadas, 1·P(neg) + 3·P(neu) + 5·P(pos), na mesma escala 1–5 das notas oficiais. A
média das sentenças é 4,19 estrelas (mediana 4,64); 75,1% das sentenças têm 4 estrelas ou mais e 5,6% têm 2 ou menos,
o que reproduz, no texto, o viés de positividade da plataforma. **[conferir]** O modelo foi treinado em tweets
(deslocamento de domínio) e não passou por validação manual (fora do escopo); a validade de construto (seção 5) é a
evidência indireta de adequação.

## 3. Modelagem de tópicos

**BERTopic** (embeddings `paraphrase-multilingual-MiniLM-L12-v2`, UMAP + HDBSCAN, ajustado em 200.000 sentenças e aplicado
às demais) encontrou **185 tópicos**; 29,8% das sentenças da amostra de ajuste ficaram como ruído, reduzidos a 1,0% do corpus
após reatribuição por similaridade ao centroide mais próximo. A coerência C_v média é **0,388**. Tópicos em português,
inglês e espanhol aparecem juntos (ex.: "praia, beach, playa, restaurantes, mar"), como esperado de embeddings
multilíngues.

**LDA** (linha de base) foi ajustado em 100.000 sentenças, com K escolhido por C_v máximo numa grade de 5 a 40
(K = 5: 0,612; **10: 0,625**; 15: 0,594; 20: 0,575; 25: 0,525; 30: 0,537; 40: 0,516). O LDA com K = 10 tem C_v maior que o
BERTopic, mas **a comparação é apenas indicativa**: o LDA produz poucos tópicos amplos, o que favorece o C_v, e o BERTopic
produz muitos tópicos finos. Para a análise de aspectos, a granularidade do BERTopic é a relevante.

> Nota metodológica: uma primeira execução do BERTopic mutilava palavras acentuadas por causa do pré-processamento padrão
> da biblioteca (`language="english"`); foi corrigida (`language="multilingual"`) e o C_v da primeira execução (0,358) foi
> descartado. Ver `historico/v1_etapa3_bertopic_sem_acentos/RESUMO.md`.

## 4. Mapeamento tópico → aspecto

O código sugeriu o aspecto de maior similaridade de cosseno entre o centroide do tópico e o vetor do aspecto (média dos
embeddings de termos-semente multilíngues); a decisão final foi **humana**, tópico a tópico. A sugestão automática concentrou
tópicos em `localização` e tratou elogio genérico como aspecto; a revisão (105 tópicos mantidos, 80 alterados pelo
pesquisador e 66 reclassificados após discussão) criou o aspecto **`satisfacao_geral`** (elogio ou queixa genérica:
"recomendo", "voltarei", "adorei"). Distribuição das sentenças por aspecto: satisfação geral 27,1%; comunicação 19,2%;
localização 18,3%; comodidades 13,0%; limpeza 7,7%; precisão 5,2%; ruído/conforto 2,5%; check-in 2,3%; segurança 1,3%;
custo-benefício 1,0%; fora do perfil (`geral`) 2,5%.

## 5. Perfil ABSA e validação de construto

Para cada anúncio e aspecto calculou-se a média do sentimento das sentenças do aspecto (mínimo de duas sentenças). A
**validação de construto** correlaciona esse sentimento com a subnota oficial correspondente, no nível do anúncio. Não há
limiar de aprovação; os coeficientes indicam força e sinal da concordância.

| Aspecto | Subnota oficial | n | Spearman | Pearson |
|---|---|---:|---:|---:|
| Limpeza | cleanliness | 19.095 | 0,453 | 0,579 |
| Check-in | checkin | 8.919 | 0,419 | 0,401 |
| Comunicação | communication | 25.418 | 0,296 | 0,436 |
| Localização | location | 24.101 | 0,240 | 0,312 |
| Custo-benefício | value | 3.552 | 0,237 | 0,261 |
| Precisão | accuracy | 16.638 | 0,168 | 0,218 |
| Satisfação geral | rating (nota global) | 26.378 | 0,341 | 0,523 |

Todos os coeficientes são positivos e significativos (p < 0,001). A concordância é moderada; deve ser lida considerando que as
subnotas oficiais também são comprimidas no teto (muitos empates em 5,0), o que **atenua** as correlações. Três aspectos
(ruído/conforto, segurança, comodidades) não têm subnota e não puderam ser validados.

## 6. Rating sintético

R_syn é a média igual dos aspectos disponíveis (mínimo de 3 aspectos específicos; `satisfacao_geral` entra na média mas não
conta para o mínimo), em estrelas na escala 1–5. **22.564 anúncios** têm R_syn (seção 10 trata da seleção). A especificação
**principal não aplica shrinkage**; a versão com média bayesiana (m = 23, a mediana de avaliações) é reportada como
sensibilidade (seção 9). Uma versão calibrada por mapeamento de quantis para a distribuição da nota oficial (`R_syn_cal`) existe
apenas para comunicação em estrelas e não é usada nas análises.

**Compressão e descompressão no teto.** A nota oficial concentra 22,8% dos anúncios no valor modal (5,0); R_syn concentra
1,6% no seu valor modal mais comum. A correlação de postos entre R_syn e a nota oficial é 0,62, e **61% dos anúncios mudam
10 pontos percentuais de posto ou mais** entre os dois rankings. Dentro do grupo com nota exatamente 5,0 (n = 5.142), R_syn
distribui os anúncios no intervalo de percentil de 0,27 a 0,98 (5º–95º), isto é, discrimina onde a nota oficial é constante.
A concordância de R_syn com as seis subnotas **dentro desse grupo** é positiva e pequena (Spearman de +0,08 a +0,12), com
subnotas também saturadas (45% a 85% iguais a 5,0).

## 7. Análise A — poder explicativo do desempenho

Desfechos: ocupação estimada nos últimos 365 dias (principal) e receita estimada (secundária, em log). Controles: volume
total de avaliações, avaliações nos últimos 12 meses, preço (log), tipo de acomodação e efeitos fixos de bairro. Validação
**out-of-sample**: k-fold com 5 dobras repetido 5 vezes (seed fixa). Amostra: 20.882 anúncios (1.682 sem preço/receita foram
excluídos).

**Os controles sozinhos já explicam R² out-of-sample = 0,798 da ocupação e 0,681 da receita.** Acrescentar a nota oficial, o
rating sintético ou ambos praticamente não altera esses valores (ocupação: M1 0,7983; M2 0,7982; M3 0,7984; RMSE ≈ 33,9
noites). A tabela mostra o ganho de R² out-of-sample de acrescentar R_syn à nota oficial (M3 − M1), com intervalo 2,5%–97,5%
entre as dobras:

| Escopo (ocupação) | n | ΔR² (M3 − M1) | IC 2,5%–97,5% |
|---|---:|---:|---|
| Amostra completa | 20.882 | +0,0001 | [−0,0000; +0,0002] |
| Teto: R_off ≥ 4,8 | 14.451 | 0,0000 | [−0,0001; +0,0001] |
| Teto: R_off ≥ 4,9 | 9.747 | +0,0002 | [−0,0002; +0,0007] |
| Teto: R_off = 5,0 | 4.711 | +0,0006 | [−0,0006; +0,0015] |

Para a receita os valores são do mesmo tamanho (|Δ| < 0,0005) e os intervalos também incluem zero. **Não há evidência de que
o rating sintético explique desempenho além da nota oficial e dos controles, nem na amostra completa nem no teto.**

## 7.1 Análise A sem o controle de avaliações dos últimos 12 meses (recomendada como principal)

A ocupação estimada é, em 100% dos anúncios, `min(255, avaliações_12m × 2 × max(3, minimum_nights))`, e a receita estimada é
`preço × ocupação` (verificado nos dados; consistente com a documentação da Inside Airbnb). Controlar por avaliações dos
últimos 12 meses "controla o desfecho" e explica o R² de 0,80 da seção 7. Refizemos a análise com os controles da
especificação original (volume total de avaliações, preço, tipo de acomodação e bairro), para ocupação, receita e também o
**número de avaliações dos últimos 12 meses** (log), um desfecho sem construção algébrica. Especificação principal de R_syn
(sem shrinkage); mesmos folds e seed.

R² out-of-sample:

| Desfecho | Escopo | M0 controles | M1 R_off | M2 R_syn | M3 ambos |
|---|---|---:|---:|---:|---:|
| Ocupação | amostra completa | 0,475 | 0,483 | 0,478 | 0,483 |
| Ocupação | R_off = 5,0 | 0,506 | 0,506 | 0,506 | 0,506 |
| Receita (log) | amostra completa | 0,175 | 0,192 | 0,179 | 0,193 |
| Avaliações 12 m (log) | amostra completa | 0,440 | 0,456 | 0,444 | 0,456 |

Ganho de R² (IC 2,5%–97,5% entre dobras), amostra completa (n = 20.882):

| Comparação | Ocupação | Receita | Avaliações 12 m |
|---|---|---|---|
| M1 − M0 (nota oficial sobre controles) | **+0,0079** [+0,0052; +0,0099] | **+0,0174** [+0,0089; +0,0239] | **+0,0163** [+0,0108; +0,0208] |
| M2 − M1 (R_syn no lugar da nota oficial) | **−0,0050** [−0,0070; −0,0020] | **−0,0132** [−0,0206; −0,0050] | **−0,0116** [−0,0157; −0,0067] |
| M3 − M1 (R_syn além da nota oficial) | 0,0000 [−0,0005; +0,0002] | +0,0010 [−0,0013; +0,0025] | +0,0006 [−0,0009; +0,0014] |

No teto (ocupação): M3 − M1 = 0,0000 em R_off ≥ 4,8 ([−0,0003; +0,0002]), −0,0001 em ≥ 4,9 ([−0,0003; 0,0000]) e −0,0002 em
= 5,0 ([−0,0009; 0,0000]); para receita em = 5,0, +0,0019 [−0,0040; +0,0059]; para avaliações em 12 m, +0,0015 [−0,0020; +0,0041].

**Leitura.** Sem o controle que anulava o teste, a nota oficial passa a acrescentar poder explicativo detectável (≈ 1 a 2
pontos percentuais de R²), de modo que o teste tem poder para detectar associações dessa ordem. R_syn, sozinho, explica
**menos** do que a nota oficial, e **não acrescenta nada além dela**, na amostra completa nem nos tetos. A conclusão
qualitativa da seção 7 se mantém, agora com um teste informativo. Na faixa R_off = 5,0 a nota oficial é constante, então M1 = M0
por construção e o ganho de R_syn mede a informação extra que ele traz dentro do teto: nula, com intervalos que cruzam zero.

## 8. Análise B — monotonicidade e reordenamento

A correlação de postos de R_syn com o desempenho (ocupação), depois de residualizá-lo nos controles, é próxima de zero em
todas as faixas da nota oficial:

| Faixa de R_off | n | ρ (R_syn × desempenho residual) | ρ (R_syn × R_off) | % com mudança relevante de posto |
|---|---:|---:|---:|---:|
| Todas | 20.882 | +0,024 | 0,620 | 61% |
| [0; 4,5) | 1.285 | +0,003 | 0,427 | 30% |
| [4,5; 4,8) | 5.146 | +0,055 | 0,273 | 56% |
| [4,8; 4,9) | 4.704 | +0,025 | 0,134 | 73% |
| [4,9; 5,0) | 5.036 | −0,016 | 0,153 | 68% |
| = 5,0 | 4.711 | −0,050 | — | 56% |

A regressão isotônica (relação monótona crescente, avaliada fora da amostra) tem R² ≈ 0 para os dois ratings (R_syn: de
−0,003 a −0,0004; nota oficial: de −0,002 a +0,0007). **R_syn reordena os anúncios em relação à nota oficial, e não apenas os
reescala, mas essa reordenação não se associa ao desempenho medido.**

## 9. Sensibilidade e robustez

Todas as variantes usam a mesma amostra, os mesmos folds e a mesma seed.

| Variante | ρ(R_syn, desempenho bruto) na faixa 5,0 | idem, residual | ΔR² (M3 − M1), R_off = 5,0 |
|---|---:|---:|---:|
| **Sem shrinkage (principal)** | −0,01 | −0,05 | +0,0006 |
| Com shrinkage (m = 23) | +0,35 | −0,19 | −0,0001 |
| Sem shrinkage, sem `satisfacao_geral` | −0,02 | −0,04 | +0,0006 |
| Com shrinkage, sem `satisfacao_geral` | +0,33 | −0,18 | −0,0001 |
| Sem shrinkage, apenas v ≤ 30 (n = 12.128) | +0,02 | −0,06 | +0,0004 |
| Com shrinkage, apenas v ≤ 30 | +0,26 | −0,11 | +0,0001 |

(1) Os valores de +0,35 e −0,19 da versão com shrinkage são um **artefato do encolhimento**: entre os anúncios de nota 5,0,
que têm poucas avaliações (mediana 9, contra 31 nos demais), o shrinkage correlaciona R_syn com o volume (ρ = +0,50 com o
log do volume, contra −0,04 sem shrinkage). Por isso a especificação principal não o aplica; a escolha foi feita após ver
esse resultado e ambas as versões são reportadas. (2) Excluir `satisfacao_geral` quase não muda os resultados. (3) O limite
de 30 avaliações por anúncio afeta 32% dos anúncios mas apenas 5,2% dos de nota 5,0; a confiabilidade (Spearman-Brown) do
sentimento médio é ~0,50 com 30 avaliações, 0,67 com 60 e 0,80 com 120, e não há deriva temporal relevante (4,345 nas 10
avaliações mais recentes vs 4,368 nas 20 mais antigas). Restringindo a anúncios com até 30 avaliações (sentimento com todas
as avaliações), a conclusão não muda. (4) Todos os intervalos de ΔR² incluem zero em todas as variantes.

## 10. Seleção e limitações

- **Seleção.** Dos 28.890 elegíveis, 6.326 ficaram sem R_syn (menos de 3 aspectos com evidência textual). Eles têm menos
  avaliações (mediana 3 vs 23), menor ocupação estimada (mediana 12 vs 66) e mais quartos privados (25% vs 14%). **Dos 9.373
  anúncios com nota 5,0, apenas 5.142 (55%) têm R_syn**: o teste do teto vale para anúncios perfeitos com volume suficiente
  de texto, não para os perfeitos com pouquíssimas avaliações.
- **Desfechos construídos a partir do volume de avaliações.** Verificamos nos dados (100% dos 42.013 anúncios) que
  `ocupação = min(255, avaliações_12m × 2 × max(3, minimum_nights))` e `receita = preço × ocupação`, em linha com a documentação
  da Inside Airbnb (*Data Assumptions*). Esses campos não medem ocupação ou receita observadas, mas um índice do volume recente
  de avaliações; devem ser descritos assim. O controle de avaliações dos últimos 12 meses, usado na seção 7, torna o desfecho
  quase determinístico (por isso a seção 7.1 é a análise principal recomendada).
- **Sentimento e nota oficial cobrem períodos diferentes** (30 avaliações mais recentes vs todas), com efeito pequeno
  (seção 9).
- **Modelo de sentimento** treinado em tweets e sem validação manual; **mapeamento por um só avaliador**, sem concordância
  entre avaliadores; **comparação de C_v** entre BERTopic e LDA apenas indicativa.
- **Coeficiente negativo no teto (seção 7): artefato de especificação.** Ele desaparece com uma forma funcional flexível
  ou com a fórmula exata do desfecho; não é um achado. Ver `redacao/02_investigacao_coeficiente_negativo.md`.

## 11. Síntese

(i) O sentimento extraído do texto concorda moderadamente, e de modo consistente, com as subnotas oficiais por aspecto
(validade de construto). (ii) Onde a nota oficial é constante (5,0), R_syn discrimina os anúncios e concorda fracamente, mas
positivamente, com as subnotas. (iii) Apesar disso, R_syn **não explica ocupação, receita nem o volume recente de avaliações além da nota oficial e dos
controles**, nem no teto; sozinho, explica menos do que a nota oficial. A conclusão é robusta a variantes de agregação, ao
shrinkage e ao limite de avaliações, e vale com e sem o controle de avaliações recentes (seção 7.1). (iv) A
interpretação é restrita pela natureza mecânica dos desfechos e pela seleção da amostra.
