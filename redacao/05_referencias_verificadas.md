# Referências verificadas (para o `referencias.bib`)

Arquivo BibTeX: `redacao/latex/referencias.bib` (33 entradas). Cada uma foi conferida em 2026-10-10 em fonte primária: **Crossref** (autores, título, periódico, volume, páginas e DOI), **JMLR**, **ACL Anthology**, **arXiv**, **Hugging Face** e a página do **Inside Airbnb**. Onde não há DOI (JMLR, arXiv, livros), o `.bib` traz URL ou ISBN. O uso indicado é uma sugestão; nenhum trecho de texto foi escrito.

## Plataforma, notas e avaliações online
| Chave | Referência | Para que serve |
|---|---|---|
| `zervas2021` | Zervas, Proserpio & Byers (2021), *Marketing Letters* 32(1) | Notas do Airbnb concentradas no topo da escala (compressão) |
| `bridges2018` | Bridges & Vásquez (2018), *Current Issues in Tourism* 21(18) | Avaliações do Airbnb majoritariamente positivas; análise de linguagem |
| `fradkin2021` | Fradkin, Grewal & Holtz (2021), *Marketing Science* 40(6) | Reciprocidade e viés nas avaliações do Airbnb |
| `hu2009` | Hu, Zhang & Pavlou (2009), *Communications of the ACM* 52(10) | Distribuição em J das avaliações online |
| `chevalier2006` | Chevalier & Mayzlin (2006), *Journal of Marketing Research* 43(3) | Avaliações online e vendas |
| `zervas2017` | Zervas, Proserpio & Byers (2017), *Journal of Marketing Research* 54(5) | Contexto do impacto do Airbnb |
| `cheng2019` | Cheng & Jin (2019), *Int. J. Hospitality Management* 76 | O que os usuários do Airbnb comentam nas avaliações |
| `luo2019` | Luo & Tang (2019), *Int. J. Hospitality Management* 80 | Dimensões ocultas em avaliações do Airbnb (análise latente por aspecto) |

## Determinantes de preço e reputação (contexto)
`wang2017` (*Int. J. Hospitality Management* 62), `gyodi2021` (*Tourism Management* 86), `chicaolmo2020` (*Tourism Management* 77), `deboosere2019` (*Regional Studies, Regional Science* 6). Vêm do PDF de revisão, mas foram conferidas uma a uma.

## Sentimento, tópicos e embeddings
| Chave | Referência | Para que serve |
|---|---|---|
| `liu2012` | Liu (2012), livro | Análise de sentimento e mineração de opinião |
| `pontiki2014` | Pontiki et al. (2014), SemEval-2014 Tarefa 4 | Análise de sentimento por aspecto |
| `barbieri2022` | Barbieri et al. (2022), LREC | Modelo A (XLM-T, cardiffnlp) |
| `hf_cardiffnlp`, `hf_nlptown` | Fichas dos modelos A e B no Hugging Face | Modelo B (nlptown) não tem artigo próprio; cita-se a ficha |
| `devlin2019` | Devlin et al. (2019), NAACL | BERT, base do modelo B |
| `wolf2020` | Wolf et al. (2020), EMNLP (demos) | Biblioteca Transformers |
| `reimers2019`, `reimers2020` | Sentence-BERT; versão multilíngue por destilação | Embeddings (`paraphrase-multilingual-MiniLM-L12-v2`) |
| `grootendorst2022` | BERTopic (arXiv:2203.05794) | Tópicos |
| `mcinnes2018umap`, `mcinnes2017` | UMAP (arXiv); HDBSCAN (*JOSS* 2(11)) | Redução de dimensão e agrupamento do BERTopic |
| `blei2003` | Blei, Ng & Jordan (2003), *JMLR* 3 | LDA |
| `pedregosa2011` | scikit-learn, *JMLR* 12 | Implementação de modelos e validação cruzada |

## Estatística e validação
`cohen1960` e `landis1977` (kappa e sua leitura), `benjamini1995` (correção de múltiplos testes), `gromping2007` e `lindeman1980` (decomposição LMG/Shapley da importância relativa), `efron1975` (encolhimento empírico-bayesiano, base da opção de shrinkage).

## Dados
`insideairbnb`: a página "data assumptions" descreve o modelo "San Francisco": taxa de avaliação de 50%, estadia média (3 noites por padrão) ou mínimo de noites, limite de 70% de ocupação. Isso é coerente com a fórmula que verificamos em 100% dos anúncios (ocupação = min(255, avaliações em 12 meses × 2 × max(3, estadia mínima))). A página não traz fórmula de receita; o texto não deve atribuir a ela a de receita.

## Não incluído
- **Ayouba et al. (2020)** (do PDF de revisão): o título trata do mercado de aluguel privado na França, não de sentimento; a atribuição feita no PDF parece errada.
- **Kirkos (2021)**, **Sengupta et al.**, **Safari (2025)** e outras do PDF não foram verificadas.
- **Spearman-Brown, Shapley (1953) e livros-texto de regressão** não foram incluídos; entram se o texto os citar.

## Ainda falta (revisão de literatura)
Nada aqui cobre sozinho o referencial: faltam trabalhos sobre ABSA aplicada a hospedagem em português, vieses de seleção em avaliações (quem avalia) e métodos de medida de concordância para amostras estratificadas. Posso procurar e verificar esses blocos se você pedir.
