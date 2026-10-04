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

## 9. Sensibilidade do rating sintético (2026-10-03; `run_20261003_212801.log`, aba `Sensibilidade`)

Variantes de R_syn_raw sobre a mesma amostra, folds e seed: **base** (shrinkage + `satisfacao_geral`), **sem_shrinkage**,
**sem_satisfacao**, **sem_ambos** (módulo `src/s10_sensibilidade.py`, etapa opcional 10).

| Variante | Spearman R_syn×R_off | Spearman R_syn×log v | Faixa R_off=5,0: ρ com desempenho bruto | idem, residual | ΔR² OOS (M3−M1), teto 5,0 |
|---|---|---|---|---|---|
| base | 0,564 | −0,013 | **+0,347** | **−0,193** | −0,0001 |
| sem_shrinkage | 0,621 | −0,147 | −0,008 | −0,050 | +0,0006 |
| sem_satisfacao | 0,555 | −0,019 | +0,331 | −0,184 | −0,0001 |
| sem_ambos | 0,609 | −0,140 | −0,015 | −0,043 | +0,0006 |

**Achados**
1. **O +0,35 (bruto) e o −0,19 (residual) na faixa R_off = 5,0 são artefatos do shrinkage, não da `satisfacao_geral`.** Sem
   shrinkage ambos somem (≈ 0). Dentro da faixa 5,0 (5.142 imóveis, v mediano 9 contra 31 fora dela), o shrinkage correlaciona
   R_syn com o volume (ρ = +0,50 com log v, contra −0,04 sem shrinkage). Como o desfecho bruto é mecanicamente ligado ao
   volume, R_syn "herda" correlação positiva; ao residualizar o desfecho nos controles de volume, o sinal inverte.
2. **Excluir `satisfacao_geral` quase não muda nada** (ρ com R_off 0,555 vs 0,564; mesmos ΔR²).
3. **A conclusão da Análise A não depende da variante:** ΔR² OOS entre −0,0001 e +0,0006 em todos os escopos, ou seja,
   R_syn não explica ocupação além de R_off e dos controles.
4. **[D] Implicação:** o shrinkage com `m = 23` mistura "sentimento" com "volume" justamente na faixa onde o teste do teto
   importa (imóveis perfeitos têm poucas avaliações). Para a tese, reportar a variante **sem shrinkage** como análise
   principal do teto, ou declarar a limitação. A decisão fica com o pesquisador.

**Correção operacional (2026-10-03):** os CSVs brutos da raiz foram removidos do histórico git local (nunca haviam sido
enviados) e passaram ao `.gitignore`; o push foi aceito. Um `filter-branch` apagou os arquivos do disco e eles foram
restaurados do branch local `backup-antes-de-remover-csvs` (tamanhos e dimensões conferidos; `listings-dictionary.csv`
pode diferir só em finais de linha).

## 10. Complementares: limite de 30 avaliações, descritivo do teto e seleção (2026-10-04; `run_20261004_130216.log`, `..._130435.xlsx`)

**Limite de 30 avaliações (decisão: não reprocessar o corpus inteiro).** 32% dos imóveis elegíveis (9.266) têm v > 30, mas só
5,2% dos imóveis com R_off = 5,0 (imóveis perfeitos têm poucas avaliações). Deriva temporal desprezível (sentimento médio das
10 avaliações mais recentes 4,345 vs 4,368 das 20 mais antigas). O efeito é **ruído, não viés**: correlação split-half
(15 recentes × 15 antigas) = 0,34, logo confiabilidade Spearman-Brown ≈ 0,50 com 30 avaliações, 0,67 com 60 e 0,80 com 120.
Reprocessar custaria ~13–14 h (≈ 1,3 M textos únicos a mais). **Sensibilidade gratuita:** análises restritas a v ≤ 30
(sentimento com TODAS as avaliações; n = 13.298 com R_syn, 12.128 na Análise A; variantes `base_v30` e `sem_shrinkage_v30`).
Resultado: ΔR² OOS (M3 − M1) entre −0,0001 e +0,0009 e **todos os IC 2,5–97,5% incluem zero**; o artefato do shrinkage na faixa
5,0 persiste atenuado (ρ bruto 0,26 / residual −0,11 com shrinkage; ≈ 0 sem). A conclusão nula não depende do limite de 30.

**Descritivo do teto (aba `Descritivo_Teto`).**
- Compressão: 22,8% dos imóveis com R_syn estão exatamente em R_off = 5,0 (valor modal); o valor modal de R_syn_raw concentra
  só 3,9% (com shrinkage) ou 1,6% (sem). As medidas de empate por valor arredondado a 2 casas (≈ 100% em empate) **não
  discriminam** e não devem ser usadas.
- Dentro de R_off = 5,0 (n = 5.142), R_syn_raw espalha os imóveis (percentil de R_syn: dp 0,19–0,22; p5–p95 = 0,34–0,94 com
  shrinkage, 0,27–0,98 sem).
- Concordância de R_syn com as 6 subnotas dentro de R_off = 5,0: **ρ entre −0,04 e +0,01 com shrinkage** e **entre +0,08 e +0,12
  sem shrinkage** (positivo nas 6). As subnotas também são saturadas (45–85% iguais a 5,0), o que atenua os coeficientes.
  Leitura cautelosa: evidência modesta de informação recuperada no teto, apenas na variante sem shrinkage.

**Seleção (aba `Selecao`) — limitação importante.**
- R_syn exige ≥ 3 aspectos específicos com ≥ 2 frases: 22.564 de 28.890 elegíveis (6.326 excluídos). Os excluídos são de **baixo
  volume**: v mediano 3 vs 23; ocupação estimada mediana 12 vs 66; 25% quartos privados vs 13,6%; nota oficial mediana 5,0.
- **Consequência para a tese:** dos 9.373 imóveis elegíveis com R_off = 5,0, só 5.142 (55%) entram em R_syn; **o teste do teto
  descreve imóveis perfeitos com volume suficiente, não os perfeitos com pouquíssimas avaliações.**
- Análise A exclui outros 1.682 imóveis sem preço/receita (menos avaliações e ocupação menor; dif. padronizada 0,2–0,4).

## 11. Especificação principal passa a ser SEM shrinkage (2026-10-04; `run_20261004_132021.log`)

**[D] Decisão** (tomada DEPOIS de ver a sensibilidade da seção 9; por isso as duas especificações são reportadas lado a lado,
sem esconder a escolha): `RSYN_SHRINK = False` no `config.py`. `R_syn_raw` é a média igual dos aspectos sem encolhimento;
`R_syn_shrink` (média bayesiana da spec original, m = 23) permanece em toda tabela e na aba `Sensibilidade`
(variante `com_shrinkage`). **Motivo metodológico, não estatístico:** o shrinkage com m = mediana de v correlaciona R_syn com o
volume (ρ = +0,50 dentro de R_off = 5,0, onde v mediano é 9 contra 31 fora), contaminando o teste do teto; sem shrinkage
ρ = −0,04. As seções 8–10 descrevem a variante com shrinkage como "base" (histórico); a partir daqui "principal" = sem shrinkage.
Variantes nomeadas na aba `Sensibilidade`: `sem_shrinkage` (principal), `com_shrinkage`, `*_sem_satisfacao`, `*_v30`.

**Resultados da especificação principal (ocupação; n = 20.882 na Análise A)**
- ΔR² OOS (M3 − M1): +0,0001 (completa), 0,0000 (R_off ≥ 4,8), +0,0002 (≥ 4,9), +0,0005 (= 5,0); todos os IC 2,5–97,5% incluem
  zero. M2 − M1 é ligeiramente negativo (−0,0004 a +0,0006), também com IC cruzando zero. Receita: idem (|Δ| < 0,0005).
  **Sem evidência de que R_syn explique desempenho além de R_off e dos controles.**
- Coeficiente in-sample (z) de R_syn em M3: **negativo e estatisticamente significativo nos tetos 4,9 e 5,0** (−1,35 noites por
  DP, p = 0,0001; ocupação média ≈ 87, dp ≈ 70), mas sem ganho fora da amostra. Efeito pequeno, no sentido oposto ao da tese;
  não investigado (hipótese: composição de aspectos; não testada).
- Análise B: ρ de R_syn com desempenho residual por faixa de R_off entre −0,05 e +0,06; na faixa 5,0 = −0,05. Isotônica OOS ≈ 0
  (R² entre −0,003 e +0,0007 para R_syn e R_off). 61% dos imóveis mudam ≥ 10 pp de posto entre R_off e R_syn (ρ = 0,62).

## 12. Redação e investigação do coeficiente negativo (2026-10-04; `run_20261004_135242.log`)

- **[A]** Rascunhos em `redacao/`: `01_resultados.md` (resultados completos com números rastreáveis às abas do Excel) e
  `02_investigacao_coeficiente_negativo.md`.
- **Investigação (exploratória, 51 especificações, módulo `src/s12_investigacao_coef.py`):** o coeficiente negativo de R_syn
  nos tetos (−1,03 em R_off ≥ 4,9; −1,34 em = 5,0, noites por DP) **não foi explicado** por `minimum_nights`, características do
  anúncio, quantidade de texto, zeros de ocupação ou qualquer aspecto isolado. É pequeno (~5% do DP residual), muda de sinal
  conforme a especificação (amostra completa: +0,18 em S0, −0,75 com `minimum_nights`, +5,5 sem o volume recente) e não gera
  ganho fora da amostra. Tratar como achado exploratório sem leitura de demanda. A ocupação tem ρ = 0,97 com as avaliações
  dos últimos 12 meses no grupo de nota 5,0.
- **[L]** A descrição do método de estimativa da ocupação (dependência de `minimum_nights`) vem de conhecimento externo ao
  dicionário de dados; precisa ser confirmada na documentação oficial da Inside Airbnb antes de ser citada.
