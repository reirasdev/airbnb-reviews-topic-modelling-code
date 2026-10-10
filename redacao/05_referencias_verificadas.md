# Referências verificadas (para o `referencias.bib`)

Arquivo BibTeX: `redacao/latex/referencias.bib` (52 entradas). Cada uma foi conferida em 2026-10-10 em fonte primária: **Crossref** (autores, título, periódico, volume, páginas e DOI), **JMLR**, **ACL Anthology**, **arXiv**, **Hugging Face** e a página do **Inside Airbnb**. Onde não há DOI (JMLR, arXiv, livros), o `.bib` traz URL ou ISBN. O uso indicado é uma sugestão; nenhum trecho de texto foi escrito.

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

## Bloco 2 (19 entradas, verificadas no Crossref pelo DOI, em 2026-10-10)
| Tema | Chaves |
|---|---|
| Análise de sentimento por aspecto (pesquisas e tarefas) | `schouten2016` (*IEEE TKDE* 28), `zhang2023absa` (*IEEE TKDE* 35), `pontiki2016` (SemEval-2016 Tarefa 5) |
| Sentimento em português | `souza2020` (BERTimbau, BRACIS 2020), `freitas2013` (opinião por característica em avaliações em português, WWW 2013) |
| Viés e inflação de avaliações online | `dellarocas2008` (*Management Science* 54), `filippas2022` (*Marketing Science* 41), `proserpio2017` (*Marketing Science* 36), `thorndike1920` (efeito halo) |
| Texto de avaliações do Airbnb | `sutherland2020` (*Sustainability* 12; tópicos da experiência do hóspede) |
| Concordância entre anotadores | `cohen1968` (kappa ponderado), `hallgren2012`, `mchugh2012`; para a amostra ponderada pela população, `kish1965` (tamanho efetivo da amostra; livro, sem DOI) |
| Inferência e coerência | `efron1979` (bootstrap), `roder2015` (coerência de tópicos, base do C_v), `gromping2006` (pacote *relaimpo*, LMG), `brown1910` e `spearman1910` (confiabilidade corrigida de Spearman-Brown) |

Observações:
- `hallgren2012` tem um erratum publicado (`10.20982/tqmp.09.2.p095`); vale citar o artigo corrigido.
- `kish1965` foi incluído de memória (sem DOI) e não foi checado em catálogo; confirme editora e ano antes de citar.
- O Crossref grafava "Marry L. McHugh"; corrigi para Mary L. McHugh.
- Não encontrei, com a verificação por DOI, um trabalho específico de ABSA aplicada a hospedagem em português; `freitas2013` é sobre opinião em português em geral. Se existir referência brasileira que você já conheça, me diga o título.

## Ainda falta (revisão de literatura)
Estas referências sustentam o método, mas a revisão de literatura propriamente dita (o que se sabe sobre o que explica a nota de hospedagem, e a lacuna que a dissertação preenche) ainda precisa ser lida e organizada por você e por mim, a partir dos próprios artigos.
