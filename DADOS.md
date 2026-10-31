# Dados de origem e disponibilidade

**Fonte.** Inside Airbnb (https://insideairbnb.com/get-the-data/), Rio de Janeiro, coleta de 19 a 21 de março de 2025. Licença CC BY 4.0 (conferida em 15/10/2026).

**Arquivos esperados na raiz (não versionados).** `listings.csv` e `reviews.csv`, mais os dicionários de dados correspondentes.

| Arquivo | Linhas (com cabeçalho) | SHA-256 |
|---|---:|---|
| `listings.csv` | 80.361 (as linhas quebradas por campos de texto podem alterar a contagem de `wc -l`; a base tem 42.013 anúncios) | `69df7d813c8f5b4ac0404c235efc27ba21999e87ffad20618de35f512567f00f` |
| `reviews.csv` | 995.073 (995.072 avaliações) | `0de8564c8f659f112f093bc07c8d2dee8e4df7a08c9ba15df9f49e789516f913` |

Conferir antes de rodar: `sha256sum listings.csv reviews.csv`. Com os mesmos arquivos, a mesma configuração (`config.py`, semente 42) e as versões de `requirements-lock.txt`, o pipeline reproduz as abas da planilha final.

**O que o repositório publica.** Código, configuração, mapa de tópicos para aspectos (`data/mapa_aspecto_confirmado.*`), as 297 sentenças rotuladas e as 100 do segundo anotador (`data/validacao_*.xlsx`, textos já processados pelo pipeline, com o primeiro nome do anfitrião mascarado) e os resultados agregados nos textos. Bases brutas, dicionários e a pasta `outputs/` (cache e planilhas) não são versionados.

**Privacidade.** O nome e o identificador do avaliador não entram nas análises (o identificador serve para remover duplicatas). Os relatórios de exemplo são anonimizados (código no lugar do identificador do anúncio, bairro omitido, sem frases). Por usar informações de acesso público, a pesquisa não é registrada nem avaliada pelo sistema CEP/CONEP (Resolução CNS n. 510/2016, art. 1º, parágrafo único, II e III).
