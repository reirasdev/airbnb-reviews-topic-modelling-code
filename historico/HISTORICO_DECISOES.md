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
