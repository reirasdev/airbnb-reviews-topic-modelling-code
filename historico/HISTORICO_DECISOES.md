# Histórico de decisões, correções e aperfeiçoamentos

Registro cronológico para apoiar a escrita da dissertação (seção de metodologia, limitações e reprodutibilidade).
Convenção: **[D]** decisão de projeto · **[C]** correção de erro · **[A]** aperfeiçoamento · **[L]** limitação a declarar.

## 1. Inspeção dos dados (2026-10-01)

- 42.013 imóveis, 995.072 avaliações; 33.140 com nota e subnotas; `number_of_reviews` coincide 100% com a contagem no
  `reviews.csv`. 39% dos avaliados têm nota exatamente 5,0; 72% têm nota ≥ 4,8.
- 4.250 imóveis avaliados têm < 2 avaliações → excluídos; **28.890 elegíveis** (nota > 0; 1 imóvel com nota 0 excluído).
- **[L] Desfechos parcialmente mecânicos.** `estimated_occupancy_l365d` e `estimated_revenue_l365d` são estimativas
  derivadas do volume de avaliações recentes. O Spearman nota × ocupação é **−0,19** (sinal negativo, dominado pelo
  volume). Mitigação: controles de volume total e dos últimos 12 meses; receita também controlada por preço.

## 2. Decisões do "grill" (2026-10-01/02)

- **[D] R_syn_raw contínuo** é a variável das Análises A/B e do teste do teto. O quantile mapping para a distribuição de
  R_off gera `R_syn_cal`, **apenas para exibição em estrelas**: calibrar para R_off importaria o teto (39% = 5,0) e
  anularia, por construção, o teste do teto.
- **[D] Ordem:** sentimento → agregação por aspectos → shrinkage (sobre a escala 1–5) → calibração (exibição).
  `v` = total real de avaliações do imóvel; `m` = mediana de `v` entre imóveis com R_syn.
- **[D] Agregação ABSA → R_syn:** média igual dos aspectos disponíveis (≥ 3 aspectos, ≥ 2 sentenças por aspecto). Pesos
  aprendidos contra R_off foram rejeitados por circularidade.
- **[D] Sentenças gerais** (`geral`) ficam fora do perfil ABSA e de R_syn.
- **[D] Sentimento em estrelas esperadas** = 1·P(neg)+3·P(neu)+5·P(pos). Modelo único:
  `cardiffnlp/twitter-xlm-roberta-base-sentiment`. **[L]** treinado em tweets (deslocamento de domínio); sentenças
  informativas neutras puxam médias de aspecto para 3.
- **[D] Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2` (alinhamento entre idiomas por treino paraphrase).
- **[D] Taxonomia:** 8 aspectos sugeridos + `comodidades/instalações` (maior tópico esperado, sem subnota). Sem subnota,
  portanto não validáveis: `ruido_conforto`, `seguranca`, `comodidades`.
- **[D] Segmentação por regex** (independente de idioma) e **idioma por avaliação** (lingua), herdado pelas sentenças —
  detecção por sentença curta é pouco confiável. Primeiro nome do anfitrião mascarado nos comentários.
- **[D] Amostragem:** 30 avaliações mais recentes por imóvel (custo em CPU). 475.858 avaliações / 1.512.063 sentenças.
  **[L]** a nota oficial usa todas as avaliações; o sentimento usa as 30 mais recentes.
- **[D] Análise A:** além de M1 (R_off) e M2 (R_syn), M0 (controles) e M3 (ambos) para o R² incremental; k-fold
  repetido (5×5, seed fixa, mesmos folds entre modelos); grade do teto {4,8; 4,9; 5,0}; coeficientes M3 com EP robusto HC3.
  Não são testes não-aninhados (Vuong/J/encompassing ficam para estudo posterior).
- **[D] Análise B:** faixas fixas de R_off (a faixa "= 5,0" tem R_off constante, onde a correlação de R_syn com o
  desempenho é evidência pura); isotônica sobre o desempenho residualizado nos controles.

## 3. Correções e aperfeiçoamentos durante a implementação

| # | Tipo | O que aconteceu | Resolução |
|---|---|---|---|
| 1 | [C] | `pip install` do `torch` dentro do repositório falhou por limite de 260 caracteres do Windows | venv em caminho curto (`C:\vairbnb`) |
| 2 | [C] | **Quantização int8 dinâmica destruiu o modelo de sentimento:** saída quase uniforme (~0,33/classe) vs. fp32 correto (ex.: 0,92 positivo para "impecável, super limpo"). Detectado pelas frases-sanidade logadas | `SENTIMENT_QUANTIZE=False` (entra no hash do cache) |
| 3 | [A] | Sentimento e embeddings calculados por **texto único** (1,37 M únicos de 1,51 M) e em chunks com checkpoint retomável | economia de ~10% e retomada após falha |
| 4 | [C] | **BERTopic `language="english"` removia caracteres acentuados** das palavras dos tópicos (ver `v1_etapa3_bertopic_sem_acentos/RESUMO.md`). Hipótese inicial (tokenizador) testada e descartada | `language="multilingual"`; Etapa 3 refeita |
| 5 | [A] | Cache de transform do BERTopic só vale para o mesmo ajuste | assinatura (md5) dos tópicos do ajuste invalida chunks de ajuste diferente |

## 4. Medidas de custo (CPU, 4 núcleos físicos, sem GPU útil)

- Sentimento XLM-R fp32: ~35–60 textos/s → **634 min** para 1,37 M textos únicos.
- Etapa 3 (embeddings + UMAP/HDBSCAN em 200 mil + transform de 1,37 M + LDA 7 valores de K): **202 min**.

## 5. Validação em rodada de teste (2% dos imóveis, 404 imóveis na Análise A — não é resultado)

Concordância (Spearman) ABSA × subnota oficial: limpeza 0,58 · check-in 0,38 · comunicação 0,37 · localização 0,26 ·
custo-benefício 0,23 · precisão 0,18. Serviu para validar o pipeline, não para inferência.

## 6. Próximas etapas

Revisão humana do mapa tópico → aspecto (`data/mapa_aspecto_confirmado.csv`) → Etapas 5–9 completas.

## 7. Reexecução da Etapa 3 (v2) e revisão do mapa tópico → aspecto (2026-10-02/03)

- **[C]** v1 invalidada pelo bug do BERTopic (item 4 da tabela da seção 3). v2: mesmos 185 tópicos e tamanhos idênticos
  (o bug só afetava as palavras); **C_v BERTopic 0,388** (v1 inválido: 0,358); LDA K=10, C_v 0,625.
- **[A]** A reexecução da Etapa 3 levou 24 min (a v1 levou 202 min): o tempo da v1 foi dominado por uma etapa que não se
  repetiu; não investigado além disso.
- **Revisão humana do mapa** (`historico/v2_mapeamento_satisfacao_geral/`): dos 185 tópicos, 105 mantiveram a sugestão
  automática e 80 foram alterados pelo pesquisador. Achado da revisão: a sugestão automática despejava ~46% dos tópicos
  em `localização` e tratava elogio genérico como aspecto.
- **[D] Novo aspecto `satisfacao_geral`** (elogio/queixa genérico: "recomendo", "voltarei", "adorei", "experiência
  incrível"). O pesquisador havia usado `custo_beneficio` como balde desses tópicos (51 tópicos, 15,7% das frases, dos
  quais só o tópico 16 tratava de preço, 1,1%), o que diluiria a validação contra `review_scores_value`. Após revisão
  conjunta (66 tópicos reclassificados): `satisfacao_geral` 23,0% das frases mapeadas, `custo_beneficio` 1,1%.
  `satisfacao_geral` é validado contra `review_scores_rating`, não conta para o mínimo de aspectos específicos
  (`GENERIC_ASPECTS`) e **entra na média de R_syn** (`RSYN_EXCLUDE_ASPECTS` permite a sensibilidade sem ele).
- **[L]** `custo_beneficio` ficou esparso (3.552 imóveis com ≥ 2 frases do aspecto).

## 8. Resultados da execução completa (Etapas 5–9, mapeamento confirmado; `run_20261003_211335.log`)

**Escopo:** 28.889 imóveis com perfil ABSA; 22.564 com ≥ 3 aspectos específicos (R_syn); 20.882 na análise (com preço).
Shrinkage m = 23 (mediana de avaliações); R_global = 4,155.

**Validação de construto (Spearman, nível do imóvel):** limpeza 0,45 · check-in 0,42 · satisfação geral×nota global 0,34 ·
comunicação 0,30 · localização 0,24 · custo-benefício 0,24 · precisão 0,17 (todos p < 0,001; Pearson de 0,22 a 0,58).
As subnotas oficiais também são comprimidas no teto, o que atenua os coeficientes.

**R_syn × R_off:** Spearman 0,56; 71% dos imóveis mudam ≥ 10 pontos percentuais de posto. R_syn_raw tem dp 0,15 contra 0,22
de R_off, e 22,8% dos imóveis têm R_off = 5,0 exato (R_syn_raw é contínuo).

**Análise A (R² out-of-sample, k-fold 5×5):** os controles sozinhos (volume, avaliações dos últimos 12 meses, preço, tipo,
bairro) já explicam **R² = 0,80 da ocupação** e 0,68 da receita. Nem R_off nem R_syn acrescentam: ΔR² (M3 − M1) = +0,0005
na amostra completa; no teto (R_off ≥ 4,8; 4,9; 5,0) ΔR² entre −0,0001 e +0,0002, com IC 2,5–97,5% cruzando zero.
**A tese (R_syn explica desempenho além de R_off, sobretudo no teto) NÃO é sustentada com estes desfechos.**
**[L]** Interpretação cautelosa: ocupação e receita estimadas são mecanicamente ligadas ao volume recente de avaliações
(`number_of_reviews_ltm` sozinho quase esgota o R²), então o teste tem pouco poder para detectar qualquer efeito de nota.

**Análise B:** isotônica fora da amostra R² ≈ 0 para ambos (R_syn 0,0025 vs R_off 0,0007, diferença irrisória). Na faixa
R_off = 5,0, o Spearman de R_syn com o desempenho **bruto** é +0,35, mas com o desempenho **residualizado** nos controles é
−0,19: a associação bruta é majoritariamente volume (o shrinkage puxa imóveis com poucas avaliações para a média global,
correlacionando R_syn com volume). O −0,19 residual não foi investigado.

**Pontos abertos para a escrita:** (i) sensibilidade a R_syn sem shrinkage (`R_syn_pre`) e sem `satisfacao_geral`;
(ii) desfechos menos mecânicos que ocupação/receita estimadas; (iii) explicação do −0,19 residual na faixa 5,0.
