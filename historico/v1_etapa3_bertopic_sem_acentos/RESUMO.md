# v1 — Etapa 3 (BERTopic/LDA) arquivada e reexecutada

**Data:** 2026-10-02 · **Execução original:** `run_20261002_005544.log` (Etapas 1–4, N=30)
**Motivo da reexecução:** bug de pré-processamento do BERTopic que mutilava as palavras acentuadas dos tópicos.

## Resultado da v1 (o que foi arquivado)

| Item | Valor |
|---|---|
| Imóveis analisados | 28.890 (de 42.013; elegíveis = nota > 0 e ≥ 2 avaliações) |
| Avaliações usadas | 475.858 (30 mais recentes por imóvel) |
| Sentenças / textos únicos | 1.512.063 / 1.366.091 |
| Sentimento médio (estrelas) | 4,19 (mediana 4,64; 75,1% das sentenças ≥ 4; 5,6% ≤ 2) |
| BERTopic | 185 tópicos; 29,8% de outliers no ajuste, 1,0% após reatribuição; C_v médio 0,358 |
| LDA | K=10 escolhido por C_v máximo; C_v 0,625 |
| Tempo | Etapa 2 (sentimento) 634 min; Etapa 3 202 min |

## Problema encontrado

Todas as palavras dos tópicos saíam sem caracteres acentuados ("anfitri", "farmcia", "prximo"), e **0 dos 185 tópicos** tinha
qualquer letra acentuada nas `top_words`. A hipótese inicial (tokenizador do `CountVectorizer`) foi testada e **descartada**:
o padrão `[^\W\d_]{3,}` preserva acentos. A causa-raiz está em `bertopic/_bertopic.py::_preprocess_text`: com o padrão
`language="english"`, o BERTopic aplica `re.sub(r"[^A-Za-z0-9 ]+", "", doc)` aos documentos antes de montar o c-TF-IDF.

**Correção:** `BERTopic(language="multilingual", ...)`.

## Impacto

- **Agrupamento e atribuição de tópicos: não afetados** (embeddings pré-calculados; UMAP/HDBSCAN não leem o texto).
- **Palavras representativas e C_v do BERTopic: inválidos.** As palavras truncadas ficavam fora do dicionário de coerência
  e eram descartadas, tornando o C_v 0,358 incomparável com o do LDA (0,625). **Não usar esse par na dissertação.**
- **Mapa tópico × aspecto:** a sugestão por embeddings usa centroides (não afetados), mas a revisão humana depende de
  ler as palavras, que estavam ilegíveis. Por isso o CSV de mapeamento v1 foi arquivado **sem preenchimento**.
- Por segurança, a reexecução refaz também a transformação dos 1,37 M de textos (a assinatura do ajuste só é gravada a
  partir da v2; sem ela não dá para provar que os ids de tópico coincidem).

## Observações da v1 que valem para a análise (independentes do bug)

- A sugestão automática concentrou 86 de 185 tópicos em `localização` e 48 em `comunicação`; tópicos gerais ("rio, janeiro,
  stay", "casa, senti, família") foram sugeridos como aspecto. A confirmação humana é indispensável.
- `OUTLIER_MIN_SIM = 0,45` reduz outliers de 29,8% para 1,0%, forçando frases genéricas em tópicos de aspecto. Candidato a 0,55.
- O C_v do LDA favorece poucos tópicos amplos (K=10); comparar com BERTopic exige a mesma referência de coocorrência.

## Arquivos desta pasta

`topics_bertopic.csv`, `topics_lda.csv`, `lda_grid.csv`, `mapa_topico_aspecto.csv` (matriz de similaridade),
`mapa_aspecto_confirmado_v1_NAO_PREENCHIDO.csv`, `metrics.json`, `run_20261002_005544.log`, `console_full_1_4.out`,
`resultados_20261002_005544.xlsx`. Os artefatos grandes (`text_topics.parquet`, centroides, chunks de transform) ficam em
`outputs/historico_cache/v1_etapa3_bertopic_sem_acentos/` (fora do git).
