# Proposta de estrutura da dissertação

Título: *O que as avaliações revelam sobre a nota: decomposição por aspecto do sentimento em avaliações de hóspedes do Airbnb no Rio de Janeiro.*

Narrativa central: **as notas do Airbnb estão comprimidas no topo e dizem pouco sobre o porquê; o texto das avaliações, medido com validação explícita, permite decompor a nota por aspecto e por queixa concreta, e entregar isso como diagnóstico ao anfitrião. Um índice único construído a partir do texto não substitui a nota.** O resultado nulo do índice é complementar, e o peso do trabalho está na decomposição e no diagnóstico.

Correspondência: "§" = seção de `01_resultados_unificado.md`; "(A)" = apêndice. Capítulos marcados **[escrever]** não existem no material atual.

## Cap. 1. Introdução **[escrever]**
Problema (nota saturada, pouca informação sobre o motivo), pergunta central, quatro perguntas específicas (medição, associação com a nota, aplicação, índice único — `00_enquadramento.md` §3), contribuições (§4 do enquadramento), limites do escopo (associação, não causa; sem desempenho econômico observado) e estrutura do texto. Termina com o título e a organização dos capítulos.

## Cap. 2. Fundamentação teórica **[escrever]**
- Avaliações online e sua função de sinalização; viés de positividade e compressão das notas.
- Análise de sentimento por aspecto (ABSA) e modelos multilíngues; tópicos (BERTopic, LDA).
- Validade e confiabilidade de medidas textuais; concordância entre anotadores; medidas ponderadas por população em amostras estratificadas.
- Estudos sobre Airbnb: avaliações, preço, reputação.
Decisão de leitura: citar o que justifica cada escolha metodológica do Cap. 3 (modelo de sentimento, estratificação, LMG, correção de Benjamini-Hochberg).

## Cap. 3. Dados e método (§1, §2, §3 + decisões do histórico)
1. Base e recorte: Inside Airbnb, 42.013 anúncios, 995.072 avaliações, 28.890 elegíveis (§1).
2. O que a base permite medir: ocupação e receita estimadas são funções exatas do número de avaliações; o objeto é a nota, as subnotas e o texto (§2). *Este ponto abre o capítulo porque define o que o estudo não pode afirmar.*
3. Tratamento do texto: 30 avaliações mais recentes, sentenças, idiomas (§1, §3).
4. Sentimento: dois modelos (A e B) e a regra de escolha pré-registrada (§3, §4.3).
5. Aspectos: BERTopic, mapa tópico → aspecto, tópicos diretos e reatribuídos (§3).
6. Desenho analítico: percentil da nota, LMG, GBM, logística, regressões com validação cruzada 5×5, correção BH, linguagem de associação.
7. Princípios de rastreabilidade: planilha única, todo número do texto vem dela.

## Cap. 4. Validação da medição (§4)
Corpo: 4.1 frases rotuladas (acurácia e kappa na amostra e ponderados pela população), 4.3 regra e modelo principal, segundo anotador (kappa de 0,86 no sentimento e 0,62 no aspecto), 4.5 checagem com LDA, 4.6 classificação confiável/cautela.
Apêndice: 4.2 (concordância A × B completa) e 4.4 (validade de construto, cinco verificações de robustez).
Fecha com a tabela de classificação por aspecto, que condiciona a leitura dos capítulos seguintes.

## Cap. 5. Resultados: o que o texto revela sobre a nota (§5)
- 5.1 Decomposição por aspecto (LMG, GBM, logística, segmentos, sensibilidades); comodidades à frente, com a ressalva do Cap. 4. **Incluir aqui o teste de efeito de tamanho de comodidades** (ver "Lacunas").
- 5.2 Queixas e elogios por tópico — o resultado mais utilizável; 13 de 15 queixas coincidem entre os modelos.
- 5.3 Cuidados de interpretação.

## Cap. 6. Aplicação: diagnóstico por anúncio (§6) **[ampliar]**
Ferramenta, tabelas de referência por bairro e tipo, exemplos anonimizados (`redacao/exemplos_diagnostico/`), como ler a evidência baixa, limites de uso. Vale incluir um caso comentado de ponta a ponta e uma discussão de como uma empresa gestora usaria o relatório. Este é o capítulo que justifica o mestrado profissional.

## Cap. 7. Análise complementar: um índice único acrescenta algo? (§7)
Corpo: construção e decisão sobre shrinkage (7.1), compressão e reordenamento da nota (7.2), poder explicativo e conclusão nula (resumo de 7.3), leitura em duas vias (7.6).
Apêndice: tabelas completas de 7.3, 7.4, 7.5, coeficientes dentro da amostra.

## Cap. 8. Discussão **[escrever]**
Relacionar os achados à literatura (compressão, halo entre subnotas, o que o texto acrescenta à nota); implicações para anfitriões e para a plataforma; o que o resultado nulo do índice sugere; limitações (§8) integradas à discussão, não apenas listadas.

## Cap. 9. Conclusões (§9) e trabalhos futuros
Quatro conclusões na ordem da linha de raciocínio; o que o estudo não conclui; trabalhos futuros (desfechos econômicos observados, painel temporal, comparação com outras cidades, mais anotadores, tratamento de aspectos de cautela, em especial comodidades).

## Apêndices
A. Tabelas completas de validade de construto e concordância A × B (Cap. 4).
B. Tabelas completas do Cap. 7.
C. Protocolo de anotação e planilha do segundo anotador.
D. Mapa tópico → aspecto (BERTopic e LDA).
E. Registro de decisões (resumo de `historico/HISTORICO_DECISOES.md`).

## Lacunas a tratar antes de escrever
1. **Efeito de tamanho em comodidades:** repetir a decomposição normalizando pelo número de frases por aspecto ou dividindo comodidades em subtópicos.
2. **Revisão de literatura** (Cap. 2 e 8): inexistente no material.
3. **Caso de diagnóstico completo** para o Cap. 6.
4. **Tabelas e figuras de corpo:** escolher no máximo 1 ou 2 por capítulo; figuras ainda não foram produzidas (barras da decomposição, dispersão R_syn × nota).

## Ordem de escrita sugerida
Cap. 3 → Cap. 4 → Cap. 5 → Cap. 6 → Cap. 7 → Cap. 9 → Cap. 8 → Cap. 2 → Cap. 1. Os capítulos que já têm material e números vão primeiro; introdução e discussão por último, quando a narrativa estiver fechada.

---

## Adaptação ao modelo da universidade (EngUCP, LaTeX)

O modelo fornecido (`Template_REUCP_v5/Latex_UCP`) é o de **artigo** do *Journal of Engineering of Catholic University of Petrópolis*: coluna única, Times 12 pt, **6 a 20 páginas incluindo figuras, tabelas e referências**, PDF de até 2 MB, sem numeração de páginas, título em maiúsculas, resumo contido na primeira página, introdução começando na segunda. A estrutura de nove capítulos acima não cabe nesse limite; ela vale para uma dissertação completa. Se o formato exigido for o artigo, a versão condensada é a do esqueleto `redacao/latex/artigo_ucp.tex`:

| Seção do artigo | Páginas | Origem no texto unificado |
|---|---:|---|
| Resumo (página 1) | 1 | rascunho já escrito no `.tex` |
| 1 Introdução | 1,25 | `00_enquadramento.md` + escrever |
| 2 Referencial teórico | 1,5 | escrever |
| 3 Dados e método | 3 | seções 1 a 3 |
| 4 Validação da medição | 3,5 | seção 4 (4.1, 4.3, 4.5, 4.6 e segundo anotador; resto resumido) |
| 5 O que o texto revela sobre a nota | 3 | seção 5 |
| 6 Aplicação: diagnóstico | 1,25 | seção 6 |
| 7 Um índice único acrescenta algo? | 1,75 | seção 7 (só os resultados principais) |
| 8 Discussão e limitações | 1,25 | seção 8 + escrever |
| 9 Conclusões | 0,75 | seção 9 |
| Referências | 1 | escrever |

Total aproximado de 19 a 20 páginas. O que não cabe (concordância A × B completa, validade de construto detalhada, tabelas longas do índice único, coeficientes e sensibilidades) fica na planilha final como material suplementar e é citado no texto.

Itens do modelo a respeitar: `\pagestyle{empty}` (já no esqueleto), no máximo seis palavras-chave, resumo sem referências, figuras e tabelas com legenda de 10 pt, referências em ordem alfabética e só as citadas, `pdflatex`. Não há LaTeX instalado nesta máquina, então o esqueleto não foi compilado; use o Overleaf ou instale o MiKTeX.
