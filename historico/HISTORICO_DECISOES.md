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

## 13. Descoberta: a ocupação estimada é função exata de variáveis do anúncio (2026-10-04; `run_20261004_143317.log`)

- **Fonte oficial** (Inside Airbnb, *Data Assumptions*): reservas = avaliações ÷ taxa de avaliação (50%); noites = reservas ×
  duração média de estadia (3 noites ou o mínimo de noites, se maior); ocupação limitada a 70%; receita = ocupação × preço.
  O dicionário do repositório (`listings-dictionary.csv`) **não define** `estimated_*` (o trecho citado sobre `availability_*`
  descreve calendário, não a estimativa; além disso, define disponibilidade como "reservada ou bloqueada pelo anfitrião", o
  que a torna um controle ambíguo).
- **[C] Verificado nos dados (aba `Formula_Ocupacao`):** `ocupação = min(255, avaliações_12m × 2 × max(3, minimum_nights))` em
  **100% dos 42.013 anúncios**; `receita = preço × ocupação` em 100% dos 38.356 com preço; ltm = 0 ⇒ ocupação = 0 (12.979/12.979).
- **[C] Erro de especificação meu (assumido):** incluí `log(avaliações_12m)` como controle (recomendação do grill, item 5). A
  especificação original pedia só o volume total. Com esse controle o desfecho fica quase determinístico: o "R² = 0,80 só com
  controles" e o coeficiente negativo de R_syn no teto eram consequências disso.
- **O coeficiente negativo é artefato:** com forma funcional flexível passa a −0,42 (p = 0,15) em R_off ≥ 4,9 e −0,09 (p = 0,62)
  em = 5,0; com a fórmula exata, 0 (R² = 1). A primeira investigação (seção 12) não o resolvia por não incluir a forma exata.
- **Reanálise sem o controle de ltm** (aba `Sem_LTM`; módulo `src/s13_sem_ltm.py`; `INCLUDE_LTM_CONTROL=False`): R² dos controles
  cai a 0,475 (ocupação); a nota oficial acrescenta +0,008 [IC 0,005–0,010] e R_syn não acrescenta nada além dela
  (M3 − M1 = 0,0000), nem nos tetos; R_syn sozinho é pior que a nota oficial (M2 − M1 = −0,005). Mesmo padrão para receita e para
  avaliações dos últimos 12 meses (desfecho adicional sem construção algébrica).
- **[D] Pendente:** decidir se `INCLUDE_LTM_CONTROL=False` vira a especificação principal (recomendado). Hoje o default segue
  `True` para reprodutibilidade das execuções anteriores; as tabelas principais do Excel (`Analise_A/B`) ainda usam `True`.
- **Documentos revisados:** `redacao/01_resultados.md` (nova seção 7.1) e `redacao/02_investigacao_coeficiente_negativo.md`
  (reescrito: investigação resolvida).

## 14. Especificação principal final da Análise A: sem controle de avaliações recentes (2026-10-04; `run_20261004_144225.log`)

- **[D] Aprovado pelo pesquisador:** `INCLUDE_LTM_CONTROL = False`. Controles: log do volume total, log do preço, tipo de
  acomodação, bairro. Desfechos: ocupação, receita (log) e **número de avaliações em 12 meses (log; `EXTRA_OUTCOMES`)**.
  `s12` (investigação) e `s13.coef_forma_flexivel` forçam `True` internamente para reproduzir a análise original.
- **Resultados principais** (R_syn sem shrinkage; ver `redacao/01_resultados.md`, seções 7 a 9): nota oficial acrescenta ΔR² de
  +0,008 (ocupação), +0,017 (receita), +0,016 (avaliações 12 m); R_syn no lugar da nota explica menos (−0,005 a −0,013); R_syn
  além da nota ≈ 0 (IC cruzam zero), inclusive em R_off ≥ 4,8; 4,9; 5,0. Em R_off = 5,0, coeficientes in-sample positivos para
  receita (+0,14; p = 0,0004) e avaliações (+0,040; p < 0,0001), sem confirmação OOS (ΔR² +0,0015–0,0019; IC cruzam zero).
- Análise B: ρ(R_syn, desempenho residual) = +0,083 (todas) vs +0,168 da nota oficial; isotônica OOS R² 0,006 (R_syn) vs 0,029
  (nota oficial) na amostra completa; ~0 no teto.
- Sensibilidade: o artefato do shrinkage persiste só na correlação bruta (+0,35); com resíduo, ρ ≈ +0,01 a +0,04 em todas as
  variantes. O "−0,19" residual da seção 9 era consequência do controle de ltm.

## 15. >>> MUDANÇA DE ESTRATÉGIA (2026-10-04) <<<

**Ponto de rollback:** tag `estrategia-v1-tese-final` (commit `e9e2895`). Tudo até ali foi conduzido como teste de uma hipótese
("o rating sintético recupera informação que a nota oficial esconde, sobretudo no teto"). Para voltar:
`git checkout estrategia-v1-tese-final`.

**Nova estratégia (mestrado profissional; ver `redacao/00_enquadramento.md`):** o objetivo não é provar uma tese. Um resultado
que mostre que o sentimento é **adequado** às notas e subnotas já é uma contribuição; mostrar **quais aspectos e tópicos**
se associam à nota ajuda anfitriões e empresas gestoras. Perguntas: (1) adequação/validade de construto; (2) importância de
aspectos e tópicos; (3) diagnóstico prático por anúncio; (4) sazonalidade e eventos; (5) complementar: R_syn vs volume de
avaliações (resultado da v1).

**Plano (aprovado):** base comum (tabela de sentenças com aspecto persistida) + s14 validade de construto ampliada e amostra de
validação manual → s15 importância de aspectos/tópicos (inclui anúncios com pouco texto, sem exigir 3 aspectos) → s16
sazonalidade e feriados (versão restrita) → ferramenta de diagnóstico por anúncio (gera relatório de UM anúncio sob demanda,
com referência ao bairro e tipo; exemplos anonimizados). **Sazonalidade, versão restrita:** volume de avaliações 2016-2025 (todas as
avaliações) e conteúdo/sentimento por aspecto 2023-2025 (cobertura do sentimento por ano: 2023 37%, 2024 77%, 2025 96%);
avaliações atribuídas ao evento por janela de até 14 dias após o check-out (limite da plataforma para avaliar); o calendário de
disponibilidade/preço **não** está disponível (só uma foto da coleta).

## 16. Base comum e etapa 14 — validade de construto ampliada (2026-10-04; `run_20261004_153735.log`)

- **Base comum:** a Etapa 5 passa a persistir `sentencas_aspecto` (uma linha por sentença, com tópico, aspecto, estrelas, data e idioma);
  é a base das etapas 14, 15 e 16. Novos parâmetros no `config.py` (`MANUAL_SAMPLE_N`, `MANUAL_VALIDATION_XLSX`).
- **Etapa 14 (`src/s14_validade_construto.py`)**, abas `Val_*` do Excel. Resultados (Spearman, nível do anúncio):
  - **(a) Por volume:** a concordância é estável entre faixas de volume e entre anúncios com ≤ 30 avaliações (sentimento com todas)
    e > 30 (ex.: limpeza 0,44 vs 0,46; comunicação 0,27 vs 0,29); a hipótese de que o corte de 30 avaliações enfraqueceria a
    concordância **não se confirma**.
  - **(b) Convergente/discriminante:** a subnota correspondente tem a maior correlação com o aspecto em 5 de 7 casos e a 2ª maior em
    limpeza e precisão (as subnotas são muito correlacionadas entre si). Controlando a nota global (correlação parcial), resta
    informação específica em limpeza (0,17), localização (0,22), check-in (0,23) e comunicação (0,15); em custo-benefício (0,08) e
    precisão (0,04) quase nada.
  - **(c) Atenuação:** a confiabilidade split-half do sentimento por aspecto é baixa (0,10 a 0,40 após Spearman-Brown), o que atenua as
    correlações. As correlações corrigidas (0,57 a 0,96) são **ilustrativas e instáveis** (com confiabilidades tão baixas a correção
    é muito sensível; ver nota da etapa) e corrigem só o lado do sentimento.
  - **(d) Subnotas saturadas:** AUC (sentimento maior quando a subnota é 5 do que quando < 5) de 0,57 (precisão) a 0,69 (limpeza); Kendall
    tau-b de 0,12 a 0,32.
  - **(e) Recortes:** padrão semelhante em inglês, espanhol e português (ex.: limpeza 0,39/0,45/0,35; check-in 0,43/0,44/0,38), o que
    sustenta o uso de um modelo multilíngue; e entre casa inteira e quarto privado.
- **Validação manual:** gerada a planilha `data/validacao_manual_amostra.xlsx` (297 frases, estratificadas por aspecto × polaridade,
  rótulo cego: o gabarito do modelo fica em outra aba). Pendente de rotulagem pelo pesquisador; a etapa 14 calcula acurácia, kappa e
  matrizes de confusão quando a planilha estiver preenchida e **nunca sobrescreve** uma planilha existente.

## 17. Validação manual (297 frases rotuladas pelo pesquisador; `run_20261004_193125.log`, aba `Val_Manual`)

**Desenho.** Amostra estratificada por aspecto previsto pelo modelo (~27 por aspecto) × polaridade prevista, rótulo cego. Por ser
estratificada pela previsão, a **precisão por aspecto** é uma estimativa direta, mas a acurácia global (54,5%) e o recall **não** são
estimativas da população; ponderando a precisão de cada aspecto pela participação real do aspecto no corpus, a acurácia estimada é
**~52%**. Com ~27 frases por aspecto, os intervalos são largos (± ~0,18). Rotulagem por um avaliador.

**Sentimento (3 classes).** Acurácia 58,9%; F1 macro 0,57; kappa 0,39 (ponderado linear 0,48); Spearman humano × estrelas do modelo 0,64.
Por idioma: francês 0,92 (n = 12), inglês 0,65 (n = 63), espanhol 0,62 (n = 45), **português 0,52 (n = 166, o idioma majoritário)**.
O erro é sistemático e **conservador**: o modelo classifica como neutro 60 e como negativo 21 das 174 frases que o pesquisador considera
positivas, e nunca chama de positiva uma frase negativa (0/77). Quando o modelo diz "positivo", acerta 95% (93/98); quando diz
"negativo", 62% (52/84). Implicação: as estrelas esperadas comprimem o nível (média 4,2 contra 4,8 da nota oficial) mas preservam a
ordenação; para análises de queixas, P(negativo) tem precisão moderada.

**Aspecto.** Acurácia 54,5%, kappa 0,50. Precisão por aspecto previsto: custo-benefício 0,74, localização 0,74, precisão 0,70, limpeza 0,67,
check-in 0,56, segurança 0,48, comodidades 0,44, comunicação 0,44, ruído/conforto 0,44, satisfação geral 0,41, geral 0,37.
**Análise de erro:** frases cujo tópico original era *ruído* e foi reatribuído ao centroide mais próximo (111 de 297) têm acurácia de
aspecto de **38%**, contra **65%** nas de tópico direto (186). A similaridade ao centroide **não** discrimina acertos de erros
(25–44% em todas as faixas), então subir o limiar `OUTLIER_MIN_SIM` quase não melhora a acurácia e custa cobertura. Mandar essas
frases para `geral` seria pior (19% de acerto contra 38%): elas contêm conteúdo de aspecto, só que de forma ambígua. Frases muito curtas
(3-4 tokens) têm acurácia de aspecto de 39%.

**Leitura conjunta com a Etapa 14.** O sentimento e o aspecto são **moderadamente adequados**, e o ruído de classificação ajuda a explicar
as correlações moderadas com as subnotas (0,17 a 0,45) e a baixa confiabilidade split-half. Aspectos de maior precisão (custo-benefício,
localização, precisão, limpeza, check-in) sustentam melhor a análise de importância; os demais devem ser lidos com cautela.

**Ajuste de instrução.** O texto da aba `Instrucoes` gerado pela etapa 14 estava desatualizado (dizia usar "geral" para elogio genérico);
corrigido no gerador (a planilha rotulada não foi alterada). Os rótulos "geral" (2) e "nenhum" (39) são tratados como o mesmo grupo.

## 18. Etapa 15 — importância de aspectos e tópicos (2026-10-04; `run_20261004_200015.log`, abas `Imp_*`)

- **Dados:** 28.889 anúncios com texto (inclui os de pouco texto: sentimento não observado de um aspecto é imputado pela média, o que
  evita exigir 3 aspectos); alvo = percentil da nota (a nota é comprimida no teto). A tabela por sentença agora guarda `topic_direto`.
- **Decomposição LMG do R² da nota global (R² total = 0,32):** comodidades 42,5%, limpeza 19,6%, satisfação geral 17,5%, comunicação
  11,3%, check-in 3,4%, ruído/conforto 3,1%, precisão 1,7%, localização 0,6%, custo-benefício 0,3%, segurança 0,1%. O resultado é estável
  entre variantes (>= 3 aspectos, v <= 30, só tópicos diretos, sem `satisfacao_geral`) e entre segmentos (casa inteira/quarto privado,
  idioma predominante, 6 maiores bairros: comodidades 37%-43% em todos). Para cada subnota, o aspecto correspondente é um dos mais
  importantes (localização explica 42% do R² da subnota de localização; limpeza 33% da de limpeza), mas a **nota global quase não depende
  do sentimento sobre localização**.
- **Modelos:** GBM com NaN nativo R² fora da amostra 0,44 (OLS imputado 0,39). Permutação (queda de R² fora da amostra): comodidades 0,23;
  limpeza 0,08; satisfação geral 0,07; comunicação 0,03; check-in 0,02. Logística para "nota >= 4,9" (51% dos anúncios): AUC fora da amostra 0,82;
  odds ratio por DP de sentimento: comodidades 2,46; limpeza 1,91; satisfação geral 1,48; comunicação 1,37; check-in 1,25; ruído/conforto 1,24.
- **Tópicos (só diretos; 68 tópicos de queixa e 181 de elogio com amostra suficiente; BH):** as queixas que mais pesam (efeito sobre o
  percentil da nota × prevalência) são banheiro/chuveiro (prevalência 14%; −20 pontos), ar-condicionado/calor (13%; −18), sujeira (7%; −26),
  queixa genérica (9%; −20), cozinha (7%; −19), resposta do anfitrião (5%; −23), barulho (11%; −10), cheiro/mofo (5%; −22), cama/colchão
  (5%; −18), claridade/cortinas (5%; −16), manutenção (3%; −21), wifi (3%; −19), fechadura eletrônica (3%; −20). 57 de 68 queixas e 145 de
  181 elogios têm q < 0,05. Efeito médio de queixa por aspecto: custo-benefício −20, check-in −17, comodidades −15, limpeza −14.
- **[L] Cuidados de interpretação:** (i) é associação, não causa; (ii) a importância relativa mistura efeito e confiabilidade da medida
  (aspectos mais citados são medidos com menos erro; segurança e custo-benefício são pouco citados e imputados na maioria dos anúncios);
  (iii) `comodidades` é um aspecto largo (33 tópicos) e sua dominância vem em parte disso, por isso a análise por tópico é a leitura
  prática; (iv) a precisão da atribuição de aspecto varia de 0,41 a 0,74 (seção 17), com R² menor em tópicos diretos (0,24) por haver
  menos frases; (v) o "efeito" de um tópico compara anúncios com e sem ao menos uma menção negativa nas 30 avaliações usadas, controlando
  volume total e nº de sentenças; (vi) múltiplas comparações tratadas com Benjamini-Hochberg.

## 19. Etapa 16 (OPCIONAL) — sazonalidade e feriados: plano congelado ANTES de ver resultados (2026-10-04)

**Status:** etapa opcional; só entra na dissertação se os resultados forem interessantes (critério abaixo, definido antes da execução).

**Calendário** (`src/calendario.py`, `data/calendario_eventos.csv`, 135 janelas, 2016-2025): carnaval (sexta a quarta de cinzas), semana santa
(quinta a domingo), corpus christi (quinta a domingo), réveillon (28/dez a 02/jan), rock in rio (2017, 2019, 2022, 2024), olimpíadas 2016,
e feriados curtos (nacionais e do RJ pela biblioteca `holidays`, mais São Sebastião 20/jan municipal). Natal e Confraternização ficam
contidos na janela do réveillon. **[conferir]** São Sebastião (lei municipal) e as datas do Rock in Rio (site oficial).
**Atribuição:** a plataforma só permite avaliar após o check-out e até 14 dias depois; a avaliação pertence ao evento se estiver datada em
[início da estadia + 1, fim da estadia + defasagem]; defasagem 14 dias (eventos longos) e 5 dias (feriados de um dia, para não cobrir ~30%
do calendário); sensibilidade: 7 e 3.

**Análises (fixas):** (V) volume: contagem diária de TODAS as avaliações (2016-2019 e 2022-2025/03, excluindo 2020-2021), GLM de Poisson com efeitos
fixos de ano-mês e dia da semana, dummies dos 7 grupos de evento, EP robusto; razão de taxas (IRR) com IC 95%, e por ano de evento para os longos.
(C) conteúdo (2023-01 a 2025-03; sentimento cobre 37%/77%/96% das avaliações): GLM binomial diário por aspecto, com os mesmos efeitos fixos, para
(i) participação do aspecto nas sentenças e (ii) proporção de sentenças negativas dentro do aspecto; e por tópico (30 tópicos de queixa da etapa 15
com maior prevalência × impacto): proporção de sentenças negativas do tópico. Correção de Benjamini-Hochberg dentro de cada família.
**Critério de "interessante" (congelado):** (a) algum evento com IRR de volume cujo IC 95% exclui 1 e |IRR − 1| >= 10% nas duas defasagens
(14 e 7), ou (b) pelo menos 3 aspectos/tópicos com q < 0,05 e razão de chances de queixa >= 1,15 em um mesmo evento, nas duas defasagens.
Caso contrário, a etapa vira apêndice ou é descartada. Todas as estimativas são associações; datas de avaliação não são datas de estadia.

## 20. Etapa 16 (opcional) — resultados e correções de implementação (2026-10-04; `run_20261004_202351.log`, abas `Sazon_*`)

**Correções feitas DEPOIS de inspecionar a primeira execução (`run_20261004_202142`, log em `outputs/s16_primeira_versao_hc1.out`), declaradas aqui
por transparência:** (1) o Carnaval de 2025 dava IRR = 27 (artefato: os dados terminam em 20/mar/2025 e a janela cobre quase todo o mês truncado,
sem linha de base); (2) o Réveillon de 2019 dava IRR = 0,73 porque os dias de janeiro/2020 foram excluídos junto com a pandemia; (3) erros-padrão por
dia ignoravam a autocorrelação. Correção: análise até 28/fev/2025 (último mês completo), eventos só entram se a janela de avaliações cai inteira nos
dias analisados, e erro-padrão robusto HAC (21 defasagens). Com a primeira versão (HC1, sem filtros) os 7 eventos passavam no critério (a); após as
correções, 6 de 7. O critério e a lista de eventos não foram alterados.

**Volume de avaliações (todas as avaliações; IRR vs. dias fora de evento no mesmo ano-mês, defasagem 14 / 7 dias):** Rock in Rio 1,73 [1,16-2,58] / 2,43;
Olimpíadas 2016 1,66 [0,79-3,49] / 3,34 (um único ano; IC inclui 1 com defasagem 14); Réveillon 1,34 [1,23-1,46] / 1,45; Corpus Christi 1,33 [1,14-1,55] / 1,63;
Carnaval 1,26 [1,09-1,45] / 1,52; Semana Santa 1,25 [1,13-1,37] / 1,27; feriados curtos 1,24 [1,13-1,37] / 1,27. Consistência por ano de evento (primeira
versão): Carnaval, Corpus Christi e Rock in Rio com IRR > 1 em todos os anos; Semana Santa e Réveillon em quase todos.

**Conteúdo (2023-01 a 2025-02; só 2 Carnavais, 2023 e 2024; GLM binomial diário, EP HAC, BH por família):** poucas mudanças com explicação plausível.
No Carnaval, a proporção de frases negativas aumenta em precisão do anúncio (OR 1,79; tópico "fotos/descrição" OR 2,57), custo-benefício (OR 1,57;
tópico de valor OR 2,14) e localização (OR 1,23); no Réveillon, localização (OR 1,20) e custo-benefício (OR 1,60). Várias razões < 1 (ex.: Rock in
Rio e Corpus Christi, menor proporção negativa em vários aspectos, incluindo ruído e segurança) não têm explicação confirmada: podem refletir um
deslocamento geral de positividade nas janelas de evento ou composição de hóspedes, e não foram investigadas. Os testes por aspecto são relativos
ao total de frases, não ao nível geral de sentimento.

**Critério congelado (seção 19):** (a) volume: atendido por todos os eventos exceto Olimpíadas; (b) conteúdo: atendido só pelo Carnaval (5 itens de queixa com q < 0,05 e
OR >= 1,15 na defasagem 14 e 4 na 7). Observação: os itens contados para o Carnaval incluem aspecto e o tópico correspondente (precisão e o tópico de fotos;
custo-benefício e o tópico de valor), então a contagem independente é menor (~3).

**Leitura:** o resultado de volume é robusto e prático (picos de 25% a 75% no volume de avaliações em eventos, até o dobro no Rock in Rio com defasagem de 7 dias);
o conteúdo é modesto, com o Carnaval como único caso com uma história coerente (queixas sobre fidelidade ao anúncio, valor e localização). Sugestão: seção curta
de volume + Carnaval (ou apêndice); a decisão de incluir é do pesquisador. **[L]** data da avaliação não é a data da estadia; janelas de evento se sobrepõem em
~2% dos dias; feriados de calendário municipal e datas do Rock in Rio devem ser conferidos em fonte oficial; associações, não causas.

## 21. Emenda ao plano da Etapa 16 (2026-10-04), feita DEPOIS de ver os resultados da seção 20, a pedido do pesquisador

1. **Olimpíadas 2016 removidas** do calendário: evento único, não recorrente (e, na execução anterior, de um único bloco e IC que incluía 1).
2. **Todo Mundo no Rio incluído** (megashow gratuito em Copacabana promovido pela prefeitura; uma noite de sábado; datas informadas pelo pesquisador):
   04/mai/2024 (Madonna), 03/mai/2025 (Lady Gaga), 02/mai/2026 (Shakira). Janela de estadia = quinta a domingo do fim de semana do show.
   **Só a edição de 2024 cai dentro dos dados** (que terminam em 20/mar/2025), portanto a estimativa vem de um único bloco; será tratada com a
   mesma regra (HAC, critério (a)/(b) da seção 19) e declarada como evidência de uma única edição.
3. Lista de eventos e critério de "interessante" **não** foram alterados além disso. As duas mudanças são pós-registro: o log anterior ao ajuste
   fica em `outputs/s16_antes_da_emenda.out`.
4. **Interpretação do pesquisador (hipótese, não testada):** as menores proporções de queixa no Rock in Rio e em Corpus Christi podem refletir o perfil do
   hóspede (público mais jovem em festivais de música, possivelmente mais tolerante a ruído e a acomodações simples). Os dados não têm idade do hóspede;
   seria preciso um indicador indireto para testá-la.

## 22. Etapa 16 após a emenda (`run_20261004_203720.log`) e checagem exploratória do deslocamento geral de positividade

**Volume (IRR; defasagem 14 / 7; HAC):** Rock in Rio 1,73 / 2,42; Corpus Christi 1,34 / 1,65; Réveillon 1,34 / 1,45; Carnaval 1,26 / 1,51;
Semana Santa 1,25 / 1,27; feriados curtos 1,24 / 1,26; **Todo Mundo no Rio 2024: 1,31 [1,02-1,69] / 1,66 [1,37-2,00]** (uma única edição dentro dos dados;
2025 e 2026 são posteriores ao fim da coleta; o limite inferior do IC com defasagem 14 está colado em 1, então a evidência é fraca nessa defasagem).

**Conteúdo no Todo Mundo no Rio 2024:** nenhuma queixa aumenta; várias proporções negativas caem (custo-benefício OR 0,22; limpeza 0,78; comodidades 0,87;
comunicação 0,79). As menções mudam pouco (comunicação 1,16; check-in 1,12; precisão 1,08; comodidades 0,91). Critério (b) não atendido (0 itens de
queixa com OR >= 1,15 na defasagem 14; 2 na 7).

**Checagem exploratória (pós-hoc) da hipótese do pesquisador (perfil do hóspede / deslocamento geral de positividade):** proporção de frases
negativas **no corpus inteiro** nas janelas de evento (binomial diário, mesmos efeitos fixos, HAC), OR com defasagem 14: **Todo Mundo no Rio 0,84 [0,78-0,92];
Rock in Rio 0,87 [0,83-0,92]; Corpus Christi 0,91 [0,86-0,95]**; sem mudança geral em Carnaval (0,99), Réveillon (1,02), Semana Santa (1,05) e feriados curtos (1,00).
Ou seja, nos eventos de música e em Corpus Christi há um **deslocamento geral** para menos frases negativas, o que explica as razões < 1 por aspecto naquelas
janelas, e é compatível com a hipótese (público de festivais mais jovem/tolerante), embora os dados não tenham idade do hóspede e não distingam essa
explicação de entusiasmo com o evento. Nas demais janelas (Carnaval, Réveillon) não há deslocamento geral, então os aumentos específicos de queixa
(precisão do anúncio, custo-benefício, localização) são mais informativos. Interpretação: os testes por aspecto devem ser lidos relativamente ao nível geral.

## 23. Material de sazonalidade guardado e ferramenta de diagnóstico por anúncio (2026-10-04; etapa 17 e `diagnostico.py`)

- **Sazonalidade para a dissertação:** `redacao/03_sazonalidade_eventos.md` guarda o texto sugerido ("1,24 a 1,73 vez o de dias comuns do mesmo mês"; evitar "ocupação
  2 vezes maior"), a ressalva de que os dados só incluem avaliações de anúncios ainda ativos na coleta, a tabela Evento × defasagem 14 dias × defasagem 7 dias
  e a tendência a menos frases negativas nos eventos de música (Todo Mundo no Rio, Rock in Rio) e em Corpus Christi.
- **Ferramenta de diagnóstico (pergunta de pesquisa 3):** `diagnostico.py` (CLI) + `src/diagnostico.py` (núcleo) + `src/s17_benchmarks.py`. Gera, sob demanda, um HTML de UM
  anúncio com: sentimento médio por aspecto e posição (percentil) entre anúncios do mesmo bairro e tipo (se o bairro tem < 30, usa o tipo na cidade); evidência
  por aspecto (poucas frases = baixa, sem rotular força/atenção); queixas e elogios recorrentes com a associação média, na cidade, com o percentil da nota
  (só tópicos com q < 0,05 no sentido esperado, da etapa 15); evolução das 10 avaliações mais recentes; nota metodológica com as precisões da validação manual.
  Funciona para anúncios novos (marca a evidência como baixa). `--anonimizar` oculta id, bairro e frases. A Etapa 17 grava tabelas de referência por bairro × tipo
  (66 grupos com >= 30 anúncios; aba `Benchmark_Bairro_Tipo`) e o cache usado pela ferramenta.
- **Exemplos anonimizados** em `redacao/exemplos_diagnostico/`: A (nota alta), B (nota baixa; comodidades e satisfação geral no 4º percentil entre os pares) e C (poucas
  avaliações).
- **Correções durante o desenvolvimento:** o campo de avaliações usadas mostrava frases em vez de avaliações; elogios com associação negativa deixaram de ser listados.

## 24. Consolidação de `redacao/01_resultados.md` na estrutura v2 (2026-10-04)

O rascunho de resultados foi reorganizado pelas perguntas de pesquisa de `00_enquadramento.md`: 1 dados e amostra; 2 medição (sentimento, tópicos, aspectos);
3 **adequação** do sentimento às notas (concordância, robustez, validação manual); 4 **importância** de aspectos e tópicos; 5 **diagnóstico** por anúncio; 6 sazonalidade
(opcional, remete a `03_sazonalidade_eventos.md`); 7 resultado **complementar** do rating sintético (poder explicativo, Análise B, sensibilidades); 8 limitações; 9 conclusões.
A versão anterior (escrita como teste de hipótese) permanece no git (tag `estrategia-v1-tese-final`). Todos os números foram conferidos contra as tabelas geradas pelo pipeline.

## 25. Conferência das datas do Rock in Rio (2026-10-04)

A página geral `pt.wikipedia.org/wiki/Rock_in_Rio` só traz as datas de 1985 e 1991. Datas conferidas em fontes por edição: **2017** (pt.wikipedia, "Rock in Rio 2017"): 15, 16, 17, 21, 22, 23 e 24/set;
**2019** (pt.wikipedia, "Rock in Rio 2019"): 27, 28 e 29/set e 3 a 6/out; **2022** (pt.wikipedia, "Rock in Rio IX"): 2, 3, 4, 8, 9, 10 e 11/set; **2024** (notícias do setor, páginas pt.wikipedia da edição retornaram 404):
13, 14, 15, 19, 20, 21 e 22/set. Todas coincidem com o calendário usado (início e fim contínuos: 15-24/set/2017, 27/set-6/out/2019, 2-11/set/2022, 13-22/set/2024). A janela inclui os dias sem show entre os dois
fins de semana (3 a 4 dias; em 2019, 30/set a 2/out), uma simplificação: hóspedes que ficam os dois fins de semana são atribuídos ao evento. Resultados da Etapa 16 não mudam. Permanece **[conferir]** apenas o feriado
municipal de São Sebastião (20/jan).

## 26. CORREÇÃO das acurácias da validação manual e estimativa do ganho de uma recalibração (2026-10-04; `run_20261004_214250.log`, aba `Calib_Sentimento`)

**Correção.** As acurácias de 59% (sentimento) e 54,5% (aspecto) das seções 17 e 24 são as da **amostra de validação**, que foi estratificada por aspecto previsto e por polaridade
prevista (um terço cada), logo rica em frases difíceis; no corpus 81,5% das frases são previstas como positivas, onde o modelo acerta muito mais (95% de precisão em "positivo"). Ponderando cada frase pelo
tamanho do seu estrato (aspecto × polaridade) na população: **sentimento 87% (IC 95% bootstrap 82-91%), kappa 0,55 (0,44-0,64); aspecto 67% (56-76%)**. O tamanho efetivo da amostra ponderada é ~72 frases
(pesos de 0,01 a 7,13), então os intervalos são largos e a estimativa depende do esquema de pesos. A estimativa anterior de "~52%" para o aspecto ponderava só pela participação do aspecto, ignorando a polaridade, e fica
substituída. `redacao/01_resultados.md`, o texto do relatório de diagnóstico e os exemplos anonimizados foram atualizados com os dois números (amostra e população).

**Recalibração exploratória (etapa 18; não altera nenhuma análise principal).** Regressão logística multinomial sobre log(P(neg)/P(neu)), log(P(pos)/P(neu)) e indicador de português, ajustada com os 297 rótulos e
avaliada por validação cruzada 5 × 20 com pesos populacionais: acurácia ponderada 0,866 → 0,908, mas kappa 0,545 → 0,538 e F1 macro 0,67 → 0,58 (a recalibração passa a prever "positivo" com mais frequência,
ajudando o estrato grande e prejudicando as classes pequenas). Estrelas médias das sentenças 4,23 → 4,66. Efeito nas correlações aspecto × subnota: diferença média de +0,006 (satisfação geral +0,030; comunicação +0,017;
check-in +0,008; limpeza +0,002; custo-benefício −0,003; precisão −0,006; localização −0,009). **Conclusão: a recalibração corrige o nível das estrelas, mas quase não melhora a informação de ordenação em que as
análises se apoiam; não vale refazer o pipeline com ela.** O espaço de melhora está mais na atribuição de aspecto (67% ponderado) do que no sentimento (87%).

## 27. Pacote para revisão do orientador (2026-10-04)

`redacao/01_resultados.pdf` (8 páginas, gerado de `01_resultados.md` por `redacao/gerar_pdf.py`: Markdown → HTML → PDF pelo Edge em modo oculto) e a planilha `outputs/resultados_20261004_215620.xlsx` (mesmas
tabelas do cache; execução final, 32 abas). As abas da análise anterior com o controle de avaliações recentes e a investigação já resolvida foram movidas para o fim e renomeadas `REF_Sem_LTM` e
`REF_Investigacao_Coef` (marcadas como referência); `src/excel_writer.py` passa a gerá-las assim.

## 28. Esclarecimento das acurácias da validação manual e correção da estimativa de aspecto na população (2026-10-04)

**Sentimento.** A diferença entre 59% (amostra) e 87% (população) vem da composição: a amostra tem um terço de frases de cada polaridade prevista, e o corpus tem 81,5% positivas, 10,4% neutras e
8,1% negativas. Acerto por polaridade prevista na amostra: positiva 93%, negativa 56%, neutra 27%. Ponderando só pela polaridade: ~83%; com estratos aspecto × polaridade: 87% (IC 82-91%).
**Aspecto.** O acerto na amostra é parecido nas três polaridades (negativa 54,5%, neutra 52,6%, positiva 56,6%), então a polaridade não explica a diferença entre os 54,5% da amostra e os 67% da
seção 26. Ponderando só por aspecto: ~52%; com aspecto × polaridade: ~67% (IC 56-76%), instável (tamanho efetivo ~72 frases; pesos de 0,01 a 7,13). **Correção:** a seção 26 apresentava 67% como a acurácia
de aspecto na população; o correto é "entre ~52% e ~67% conforme o esquema de pesos". As precisões por aspecto previsto (0,41 a 0,74) e os 54,5% da amostra continuam sendo as estimativas robustas.
`redacao/01_resultados.md` (e o PDF), o texto do relatório de diagnóstico e os exemplos anonimizados foram atualizados.

## 29. Estratégia v3 — fase 0: reconhecimento e linha de base (2026-10-09; branch `estrategia-v3-sentimento-b-unificado`)

**Pedido do orientador** (execução avaliada como boa): (1) incorporar um segundo modelo de sentimento treinado em avaliações (B) e refazer as análises; (2) corrigir o enquadramento (os
desfechos "econômicos" são volume de avaliações; a contribuição não é o rating sintético); (3) fundir as duas estratégias em um único texto de resultados com linha de raciocínio contínua.
Branch criado a partir de `main` (commit `9cc84c0`). Um commit/push por fase.

**Linha de base.** As etapas 5 a 18 foram reexecutadas a partir dos caches (sem tocar em segmentação, sentimento A, tópicos ou mapa) e a planilha resultante
(`resultados_20261009_201540.xlsx`) foi comparada aba a aba com `resultados_20261004_215620.xlsx` (`src/comparar_planilhas.py`; tolerância relativa 1e-6): **30 de 32 abas idênticas
(diferença máxima 0)**. As 2 restantes diferem só na representação: `Resumo_Log` (um dicionário de métricas impresso como `np.float64(...)` por mudança de representação) e `REF_Investigacao_Coef`
(um erro-padrão `inf` da exclusão de `segurança`, já documentado como singularidade numérica). A linha de base está confirmada.

**Equivalências de nomes.** Os scripts por etapa são `src/s1_ingestao.py` ... `src/s18_calibracao_sentimento.py`; configuração em `config.py`; caches em `outputs/cache/375f221f/` (tabelas em `tables/`); rótulos manuais em
`data/validacao_manual_amostra.xlsx`. **GPU:** há uma GeForce MX110 (2 GB, driver 457), mas o PyTorch instalado é a build de CPU e uma GPU desse porte não aceleraria a inferência: a inferência do modelo B roda em CPU.
Limpeza: um arquivo vazio `python` (artefato de um comando antigo) foi removido da raiz do repositório.

## 30. Fase 1 (v3): segundo modelo de sentimento — REGRA PRÉ-REGISTRADA (2026-10-09, antes de rodar o modelo B)

**Modelos.** A (atual): `cardiffnlp/twitter-xlm-roberta-base-sentiment` (tweets; 3 classes; estrelas esperadas 1·P(neg) + 3·P(neu) + 5·P(pos)). B (novo): `nlptown/bert-base-multilingual-uncased-sentiment`
(avaliações de produtos e serviços; 5 classes de 1 a 5 estrelas). Estrelas esperadas de B = Σ k·P(k), k = 1..5.

**Definições (provisórias, adotadas antes de ver resultados de B).**
- Polaridade discreta de **A**: classe de maior probabilidade entre (negativo, neutro, positivo), exatamente como no pipeline atual (`argmax` das três probabilidades); "menção negativa" = polaridade negativa.
- Polaridade discreta de **B**: negativo se a classe mais provável (entre 1 e 5 estrelas) é 1 ou 2; neutro se 3; positivo se 4 ou 5. As colunas `p_neg`, `p_neu`, `p_pos` de B guardam P(1)+P(2), P(3) e P(4)+P(5)
  (apenas descritivas); toda análise de polaridade usa a coluna `cls`, definida pela classe mais provável de 5 classes (e não pelo argmax das três somas).
- Para as análises por frase, "menção negativa" e "menção positiva" passam a ser lidas de `cls` nos dois modelos (para A, equivale ao argmax das três probabilidades: sem mudança).
- Nível anúncio × aspecto, para o kappa entre modelos: polaridade modal das frases do anúncio no aspecto; empate entre classes vale "neutro".

**REGRA 1.6 (registrada antes da execução da fase 2 e antes da avaliação de B nas frases rotuladas).** O modelo principal é **B** se o intervalo de confiança de 95% (bootstrap estratificado) da diferença
**B − A no kappa ponderado linear populacional de sentimento** (frases rotuladas, pesos de população dos estratos originais aspecto × polaridade previstos por A) **excluir zero a favor de B** (limite inferior > 0);
caso contrário o principal continua sendo **A**. O outro modelo é sempre reportado integralmente como robustez. Também se reporta a diferença na acurácia populacional (total e só em português), sem papel na regra.

**Implementação.** Fonte do sentimento selecionável por configuração (`SENTIMENT_SOURCE`: A ou B); tabelas dependentes do modelo recebem o sufixo `__B` no cache; segmentação, idioma, tópicos e mapa de aspectos são compartilhados e não são refeitos.

## 31. Fase 4 (v3): segundo anotador — preparação (2026-10-09)

`python segundo_anotador.py gerar` sorteou 100 das 297 frases com a mesma estratificação (aspecto previsto × polaridade prevista; ~3 por célula, completando por sorteio) e gerou
`data/validacao_segundo_anotador.xlsx` (enviar: id cego, texto e colunas de rótulo com listas; sem rótulos do primeiro anotador, sem previsões de modelo, sem idioma; página de instruções com a definição de
cada aspecto) e `data/validacao_segundo_anotador_CHAVE.xlsx` (NÃO enviar: liga o id cego ao id original e traz os rótulos do primeiro anotador). `python segundo_anotador.py kappa <planilha preenchida>` calcula
concordância simples, kappa de Cohen e kappa ponderado linear (sentimento) e kappa (aspecto), com IC 95% por bootstrap, mais concordância por aspecto e matrizes de confusão; "nenhum" e "geral" são tratados
como o mesmo grupo. O script foi **testado com rótulos simulados (descartados)**; nenhum rótulo real foi preenchido. A concordância entre anotadores consta como **pendente**.

## 32. Fase 3 (v3): LDA como checagem do método de tópicos — preparação e primeira checagem com o modelo A (2026-10-09; `src/s22_lda_checagem.py`)

- **Papel do LDA:** checar se os resultados por aspecto dependem do método de tópicos; o BERTopic continua sendo o método. O LDA (K = 10) foi **reajustado** (o modelo não havia sido gravado) com a mesma amostra, dicionário e
  semente da etapa 3: os **10 tópicos reproduzem exatamente os gravados** (aba `Topicos_LDA`). Atribuição: todos os 1.366.091 textos únicos ao tópico dominante (3,0% das sentenças sem palavras no vocabulário do LDA ficam sem tópico).
- **Mapa provisório tópico LDA → aspecto (a confirmar pelo pesquisador; coluna `decisao_pesquisador` em branco).** Regra: o tópico recebe aspecto só se a leitura das palavras de maior peso indica um aspecto
  dominante, esse aspecto coincide com o de maior similaridade com os termos-semente e a margem entre o 1º e o 2º é ≥ 0,05; senão é "misto" (fora do perfil). Resultado: tópico 4 → comodidades; 6 → comunicação; 7 → satisfação geral;
  8 → localização; tópicos 0, 1, 2, 3, 5 e 9 → misto (3 e 9 são tópicos genéricos em inglês e espanhol; 1 junta prédio, portaria, piscina e funcionários; 5 junta ar-condicionado, cama e internet, mas a similaridade
  aponta ruído/conforto). **55,1% das sentenças caem em tópicos mistos do LDA**, de modo que o LDA só permite checar quatro dos dez aspectos.
- **Checagem com A:** entre as sentenças com aspecto nos dois métodos, 68,8% recebem o mesmo aspecto; correlação (Spearman) do perfil por anúncio BERTopic × LDA: comodidades 0,67, localização 0,61, comunicação 0,54, satisfação geral 0,46.
  Validade de construto com o perfil LDA (Spearman com a subnota): localização 0,20 (BERTopic 0,24), comunicação 0,28 (0,30), satisfação geral 0,19 (0,34): mesmo sinal. LMG da nota global (4 aspectos): comodidades é o primeiro nos dois métodos;
  correlação de postos da ordenação 0,80 (apenas 4 aspectos). Os números finais serão refeitos com o modelo principal definitivo (etapa 23).

## 33. Fases 1 e 2 (v3): modelo B concluído; REGRA 1.6 aplicada; cadeia a jusante com os dois modelos (2026-10-10)

**Execução.** Inferência do modelo B nos 1.366.091 textos únicos (igual à aba `Estat_Corpus`): 757 min em CPU, sem falhas (`outputs/sentimento_B.out`). Cadeia a jusante com B (etapas 5 a 11 e 14 a 17, `--sentimento B`) e comparações (19, 20, 24, 25).
Sanidade: A e B têm distribuições de polaridade diferentes por sentença (A: 6,8% negativa, 14,3% neutra, 78,9% positiva; B: 10,4%, 8,1%, 81,5%); estrelas médias por texto único 4,19 (A) e 4,06 (B).

**REGRA 1.6 (registrada na seção 30 antes de rodar B), resultado com o B completo = o preliminar:** diferença B − A no kappa ponderado linear populacional = **−0,141** (IC 95% bootstrap estratificado [−0,272; −0,012]),
isto é, o IC exclui zero **a favor de A**. **O modelo principal permanece A**; B é reportado integralmente como robustez (`Config`: `SENTIMENT_MAIN = "A"`). Discordância entre a amostra e a população, descrita sem escolher
o resultado mais conveniente: **na amostra de 297 frases B tem acurácia maior** (63,3% vs 58,9%; em português 61,4% vs 51,8%), mas a amostra foi estratificada pelas previsões de A (rica em frases que A classifica como
neutras, onde A erra); **ponderando pela população dos estratos originais, A é melhor** (acurácia 87,2% vs 85,0%; kappa linear 0,656 vs 0,515). Em português, o IC da diferença no kappa linear populacional é [−0,323; +0,011]
(inclui zero). B classifica mais frases como positivas (151 vs 98 das 297) e acerta menos nas previstas como neutras (17% vs 26%) e negativas (52% vs 62%).

**Concordância A × B no corpus:** sentença, Spearman das estrelas 0,61 e kappa ponderado linear das polaridades 0,45 (português 0,40; inglês 0,54; espanhol 0,54); anúncio × aspecto, Spearman 0,69 e kappa 0,55.
**Resultados com B (resumo; tabelas em `Resumo_AB`/`LadoALado_*`):** a validade de construto é semelhante (Spearman com a subnota correspondente entre 0,15 e 0,43; satisfação geral × nota global 0,26 vs 0,34 de A); a ordem de importância dos
aspectos para a nota global é parecida (comodidades 47,8% vs 42,5% do R²; satisfação geral 9,9% vs 17,5%); o R_syn de B correlaciona 0,82 com o de A; o poder explicativo de R_syn além da nota oficial permanece nulo nos dois modelos.
**Sazonalidade:** o **deslocamento geral de positividade nos eventos de música e em Corpus Christi (seção 22) não se replica com B** (razões de chances 0,97 a 0,99, ICs incluindo 1); os aumentos de queixas por aspecto no Carnaval também diferem entre os modelos
(A: precisão, custo-benefício e localização; B: segurança). O resultado de volume de avaliações (independe do sentimento) não muda. O conteúdo da sazonalidade é, portanto, **sensível ao modelo de sentimento**.

**Tabelas novas para sustentar o texto (antes só em scripts ad hoc):** `cmp_manual_aspecto` (acurácia de aspecto: amostra, ponderada, por polaridade, tópico direto vs reatribuído), `limite30` (limite de 30 avaliações), `sazon_negativa_geral`;
`n_efetivo_ponderado` nas métricas da validação manual (72,5 frases). **Diagnóstico (2.12):** regenerado com o modelo principal (A); os três exemplos anonimizados saem idênticos aos anteriores.
**Regressão:** as abas do modelo principal da nova planilha são idênticas às da planilha de 2026-10-04 (nenhuma diferença).


## 34. Fases 3 a 6 (v3): texto unificado, limite de 30 avaliações, enquadramento (2026-10-10)

**Texto.** `redacao/01_resultados_unificado.md` (10 seções, linha de raciocínio contínua: dados → o que se mede → como o texto é medido → a medição é confiável → o que o texto revela sobre a nota → aplicação → índice único → sazonalidade → limitações → conclusões) substitui os dois rascunhos anteriores. O rascunho da Estratégia 2 foi arquivado em `historico/rascunhos_v2/`. O texto é gerado por `redacao/montar_documento.py` a partir das tabelas do cache (mesmas da planilha final) e conferido por `redacao/verificar_numeros.py` seção a seção (só vale número presente nas abas citadas pela própria seção). Restam não localizados apenas limiares de critério (0,60; 0,20), contagens de design e totais derivados de somas; nenhum é resultado sem fonte.
**Decisões tomadas sem consulta (provisórias, a confirmar pelo pesquisador):** (i) mapa LDA → aspecto provisório (regra: leitura + similaridade + margem ≥ 0,05, senão "misto"); (ii) concordância do segundo anotador marcada como pendente (planilha cega e script de kappa prontos, testados só com rótulos simulados descartados); (iii) classificação de aspectos em "confiável"/"cautela" (precisão de atribuição ≥ 0,60 e Spearman com a subnota ≥ 0,20 nos dois modelos), fixada na seção 4.6 antes de ler as seções seguintes; (iv) coeficientes in-sample de R_syn com q-valores BH: não confirmados fora da amostra, declarados "não robustos" e fora da síntese; (v) shrinkage: justificativa teórica primeiro, e registro de que a decisão foi tomada depois de ver o resultado, com as duas versões reportadas.
**Limite de 30 avaliações (`s25_limite_30`).** Truncados 32,1% dos elegíveis (5,2% entre os de nota 5,0); split-half 0,336, Spearman-Brown 0,50/0,67/0,80 para 30/60/120; deriva temporal desprezível (4,345 vs 4,368). Acrescentado: entre os anúncios de nota 5,0 com R_syn, a correlação do índice com o log do número de avaliações é 0,498 com shrinkage e −0,040 sem (B: 0,455 e 0,030), medianas de 9 avaliações contra 31 nos demais, o que fundamenta a escolha sem shrinkage.
**Sazonalidade.** A menor proporção de frases negativas nos eventos de música não replica com B; do conteúdo por aspecto só 5 de 70 combinações coincidem em sinal e significância nos dois modelos. Notas de atualização acrescentadas a `03_sazonalidade_eventos.md` e `02_investigacao_coeficiente_negativo.md`.

## 35. Confirmações do pesquisador (2026-10-10)

- **Segundo anotador:** `data/validacao_segundo_anotador.xlsx` rotulada (100 frases). Concordância: sentimento 91% (kappa 0,855, IC [0,763; 0,937]; ponderado linear 0,883); aspecto 67% (kappa 0,622, IC [0,508; 0,727]); baixa concordância em satisfação geral (19%, confundida com o grupo geral) e limpeza (33%). Tabelas `cmp_segundo_anotador_*`, aba `Segundo_Anotador`; texto nas seções 4.6, 9 e 10.
- **Título escolhido:** *O que as avaliações revelam sobre a nota: decomposição por aspecto do sentimento em avaliações de hóspedes do Airbnb no Rio de Janeiro.*
- **Feriado de São Sebastião:** confirmado em 20 de janeiro (calendário já usa janela 19–21).
- **Mapa do LDA:** segue pendente; criado `data/mapa_lda_para_confirmar.xlsx` (coluna `aspecto_confirmado`, preenchida com a proposta provisória).

- **Mapa do LDA:** confirmado pelo pesquisador sem alterações (`data/mapa_lda_para_confirmar.xlsx`, 2026-10-10); deixa de ser provisório.

## 36. Retirada da sazonalidade (2026-10-10)

Por decisão do pesquisador, a análise de sazonalidade e eventos (opcional; só entraria com resultado excelente, o que não ocorreu) foi retirada do trabalho: removidas a seção 8 do texto unificado (limitações e conclusões passam a seções 8 e 9), as abas `Sazon_*` da planilha final e as menções em `00_enquadramento.md`. O rascunho antigo foi arquivado em `historico/rascunhos_v2/`. O código da etapa 16 e as seções 19 a 22 e 33 deste histórico permanecem apenas como registro.


## 37. Ajustes do orientador (14/10/2026), Fase 1: análises novas sobre dados existentes (2026-10-14; branch `ajustes-orientador-14out26`; `ajustes_v2.py`)

Nada do pipeline foi refeito: o script lê o cache, as frases rotuladas e a planilha final, reproduz primeiro as abas existentes (conferência por `assert`) e grava as abas novas, com sufixo `_v2`, em `outputs/resultados_final_20261013_000705_v2.xlsx` (cópia da planilha final com as abas acrescentadas; as 73 abas originais ficam intactas) e em `outputs/ajustes_v2/*.parquet`. Mesmas sementes, dobras e regras (modelo A principal, B acompanha). Linguagem de associação.

**M2 (`Classificacao_IC_v2`, `Concord_anotadores_v2`).** Intervalo de Wilson 95% da precisão de atribuição de aspecto (27 frases por aspecto; 297 no total: 54,5%, IC 48,9% a 60,1%) e precisão com os dois anotadores nas 100 frases em comum (9 ou 10 por aspecto): anotador 1 = 51/100, anotador 2 = 51/100, ambos concordam com o modelo = 40/100 (IC 31% a 50%), ao menos um concorda = 62/100 (IC 52% a 71%). Todos os intervalos dos três aspectos "confiáveis" incluem 0,60 (limpeza 67%, IC 47,8% a 81,4%; localização e custo-benefício 74%, IC 55,3% a 86,8%); a classificação passa a ser chamada de **indicativa**. Em limpeza, os dois anotadores concordam em 2 de 6 frases (33%, IC 9,7% a 70,0%, rotuladas como limpeza pelo anotador 1) e, entre as 9 frases previstas como limpeza, ambos concordam com o modelo em 2 e ao menos um em 6. A regra pré-fixada não foi alterada: limpeza continua "confiável" pela regra, com a ressalva.

**R2 (`Queixas_min2_v2`, `Queixas_min2_resumo_v2`).** Queixas por tópico exigindo ao menos 2 sentenças negativas no tópico (mesma especificação, mesmo piso de 100 anúncios, mesma correção BH; a reexecução com 1 menção reproduz a aba existente). Como o piso de 100 anúncios é mantido, o número de tópicos testados cai de 68 para 13 em A (108 para 18 em B). Das 15 queixas de maior peso em A, 11 seguem testáveis e as 11 mantêm sinal e q < 0,05; 4 deixam de ser testáveis (52, 86, 78 e 71 anúncios com duas menções: reparos, wi-fi, "airbnb/experiência" e fechadura eletrônica). A diferença associada média nessas 11 vai de −18,9 para −20,9 pontos de percentil (variação de −5,3 a +0,1); em B, de −20,0 para −23,2 (testáveis 10 de 15). Dez tópicos coincidem entre A e B no top 15 com duas menções. Leitura: a exigência de duas menções não enfraquece as associações; elas ficam um pouco maiores, como se esperaria se uma única frase negativa isolada contivesse ruído de classificação (A acerta 62% das frases que prevê como negativas). Não se alteram as conclusões.

**R3 (`Mapa_comodidades_v2`, `LMG_comodidades_v2`).** Comodidades dividido em sete subaspectos agrupando os 33 tópicos já mapeados a esse aspecto, pela palavra de maior peso do tópico (banheiro e chuveiro: 18, 32, 99, 114; climatização: 10; cozinha e utensílios: 31, 39, 157, 172; cama e colchão: 34, 69; internet: 130, 138, 149; manutenção e reparos: 53, 136; demais comodidades: os 17 restantes). LMG da nota global com 16 preditores (9 aspectos + 6 subaspectos de comodidades + "demais comodidades"). Duas leituras: (i) regra do estudo (ao menos 2 sentenças do subaspecto no anúncio): R² total cai de 0,320 para 0,266 em A (0,291 para 0,231 em B), porque os subaspectos têm dados próprios em apenas 5% a 25% dos anúncios (62% em "demais") e o resto é imputado; a soma dos subaspectos é de 25,2% em A e 29,8% em B, e limpeza (25,3% e 25,3%) e satisfação geral (23,5% e 13,8%) passam à frente de qualquer subaspecto isolado; (ii) sensibilidade com ao menos 1 sentença: R² total 0,304 (A) e 0,272 (B) e soma dos subaspectos de 42,1% (A) e 48,3% (B), praticamente igual aos 42,5% e 47,8% do aspecto inteiro; os maiores são banheiro e chuveiro (9,9% em A e 10,5% em B), demais comodidades (8,1% e 10,4%) e manutenção e reparos (7,8% e 8,2%). Leitura: o peso de comodidades vem do conjunto de subaspectos, sem que um deles domine; a posição de primeiro lugar do bloco depende de medir o aspecto com todas as sentenças. As duas versões são reportadas.

**R4 (`LMG_ausencia_v2`).** LMG com indicador de presença (≥ 2 sentenças) para cada aspecto, 20 preditores (sentimento imputado pela média + indicador). R² total sobe de 0,320 para 0,382 em A (0,291 para 0,358 em B). Parcela do sentimento sozinho: comodidades 34,3% (A) e 37,3% (B), limpeza 15,6% e 14,5%, satisfação geral 13,4% e 7,2%, comunicação 8,2% e 8,9%; somando o indicador de ausência (7,4% e 8,2% em comodidades; 2,0% e 2,2% em limpeza), comodidades 41,8% (A) e 45,6% (B). A ordem dos aspectos não muda; o resultado não depende da imputação pela média.

**F3 (`Tabela12_completa_v2`).** As 12 linhas (3 desfechos × 4 escopos) com M1−M0, M2−M1, M3−M1 (A) e M3−M1 (B), com intervalos entre dobras, extraídas de `Analise_A` e `Analise_A_mB` sem recálculo.

**F1 (`Fig1_numeros_v2` a `Fig4_diferencas_v2`).** Dados das figuras a partir de abas existentes: números do pipeline (`Estat_Corpus`), histograma da nota oficial e do índice sintético nos 22.564 anúncios com índice, LMG de A e B com a classificação, e diferenças associadas das Tabelas 9 e 10 com intervalo de 95% = estimativa ± 1,96 × erro padrão HC3 da mesma especificação (a aba `Imp_Topicos_*` já traz `ep`).

**R5 (registro datado da regra).** Commit `c6e72df` (2026-10-09 20:22:25 −0300): "Fase 1 (v3): regra 1.6 de escolha do modelo principal pre-registrada antes de rodar o modelo B"; a inferência de B começou em 2026-10-09 20:39:12 (`outputs/sentimento_B.out`, 757,1 min, fim em 2026-10-10 09:16) e o código de B foi commitado em `6a82cbe` (20:40:50); resultados em `ae38e3e` (2026-10-10). Texto da regra: seção 30 deste histórico.
