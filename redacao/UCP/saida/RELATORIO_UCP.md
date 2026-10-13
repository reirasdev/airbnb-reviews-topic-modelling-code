# Versão da dissertação no formato do Guia da UCP

**Norma aplicada:** "Guia para elaboração e normalização de trabalhos de conclusão de curso" (UCP, 2023; arquivo `2024-Normas-para-trabalhos-academicos-13-03-24-1.pdf`, 61 páginas, lido por inteiro).
**Arquivo gerado:** `saida/Raphael_Eiras-Decomposicao_por_aspecto_do_sentimento_em_avaliacoes_do_airbnb_rj-ucp_2026-UCP.docx` (45 páginas no Word; sumário e lista de tabelas atualizados).
**Geração:** `scripts/gerar_dissertacao_ucp.py` (usa, em leitura, o gerador de `redacao/abnt/scripts` e os capítulos de `redacao/latex/`); `scripts/atualizar_campos.ps1` atualiza os campos no Word; `scripts/extrair_texto_ucp.py` extrai o texto para conferência. Nada foi alterado fora de `redacao/UCP/`.
**Limitações:** o PDF não foi gerado (a exportação automática pelo Word trava nesta máquina; exportar manualmente em Arquivo > Exportar > Criar PDF) e eu não conferi o layout visualmente.

## 1. O que o Guia da UCP define e como foi aplicado
| Regra do Guia (página) | Aplicação |
| --- | --- |
| Estrutura de dissertação: capa, folha de rosto, ficha, aprovação, resumo e resumo em língua estrangeira, sumário, introdução, desenvolvimento, conclusão, referências (p. 6) | Todos presentes; dedicatória, epígrafe, agradecimentos, glossário, apêndice e anexo são opcionais e não foram incluídos |
| Capa: instituição, centro, curso, autor, título: subtítulo, local, ano (p. 7-8) | Universidade Católica de Petrópolis; Centro de Engenharia e Computação; Mestrado Profissional em Gestão de Sistemas de Engenharia; autor; título; Petrópolis; 2026 |
| Folha de rosto: autor, título, natureza do trabalho (fonte 10, espaço simples, do meio da folha à margem direita), orientador, local, ano (p. 9-10) | Aplicado; natureza no modelo "Dissertação apresentada ao Centro... da UCP, como requisito parcial para obtenção do título de Mestre em..." (p. 13) |
| Ficha catalográfica solicitada à biblioteca (biblioteca@ucp.br) (p. 11) | Página reservada |
| Folha de aprovação: autor, título, natureza, orientador com assinatura, nota, data, banca com nome, titulação e instituição (p. 11-12) | Aplicada, com nota, data e banca como pendências |
| Resumo de 150 a 500 palavras em dissertações, palavras-chave com inicial minúscula separadas por ponto e vírgula e finalizadas por ponto; resumo em língua estrangeira com "Key words" (p. 17) | Aplicado (resumo com cerca de 190 palavras) |
| Lista de tabelas: "Tabela N – título ... página" (p. 20) | Gerada pelo Word |
| Sumário centralizado; Introdução, Conclusão e Referências aparecem no sumário; pré-textuais não aparecem (p. 23) | Aplicado |
| Margens: esquerda e superior 3 cm, direita e inferior 2 cm (p. 30) | Do template |
| Paginação: contada desde a folha de rosto, visível a partir da introdução, no canto superior direito a 2 cm das bordas; tamanho 10 (p. 30, 33) | Contagem e início pela introdução do template; distância do cabeçalho ajustada para 2 cm e número em corpo 10 |
| Fonte Times New Roman ou Arial, corpo 12; corpo 10 para citação longa, nota, paginação, legendas e fontes de ilustrações e tabelas e natureza do trabalho (p. 33) | Aplicado (legenda, fonte e natureza em corpo 10) |
| Espaçamento 1,5 no texto; simples em citação longa, nota, referências, legendas e natureza (p. 34) | Aplicado |
| Seções primárias em página nova; título com indicativo numérico alinhado à esquerda; **títulos sem indicativo (resumos, sumário, introdução, conclusão, referências, listas) centralizados** (p. 34) | **Introdução e Conclusões sem número e centralizadas; as demais seções renumeradas de 1 a 7** |
| Tabela e ilustração com palavra designativa, número, travessão, título e **fonte abaixo (obrigatória, mesmo de produção própria)** (p. 36) | "Tabela N – título" acima e "Fonte: Elaborada pelo autor." abaixo |
| Citação autor-data com sobrenome em maiúscula e minúscula (ex.: `(Boaventura, 2001, p. 9)`) (p. 37-39) | `(Hu; Zhang; Pavlou, 2009)`, `Hu, Zhang e Pavlou (2009)`, `Zhang et al. (2023)` |
| Referências em espaço simples, alinhadas à esquerda, com uma linha em branco entre entradas, ordem alfabética, destaque tipográfico uniforme no título, `In:` e `et al.` em itálico, "Disponível em" e "Acesso em" para fontes online (p. 41-42) | Aplicado; título em negrito; `In` e `et al.` em itálico |
| Periódico com local de publicação; evento com nome, número, ano e cidade; trabalho acadêmico com tipo, grau, vinculação, local e data (p. 42-48) | Aplicado; local e editora não informados na base estão como `[S. l.]` e `[s. n.]` |

## 2. Diferenças em relação à versão ABNT genérica (`redacao/abnt/saida`)
1. Introdução e Conclusão sem número e centralizadas; as seções de desenvolvimento começam em 1. As remissões internas ("Seção 4" etc.) foram renumeradas, e duas frases da introdução foram ajustadas ("O texto está organizado em Introdução, sete seções numeradas e Conclusões", "as Conclusões encerram o trabalho").
2. Capa com o centro e o curso; folha de rosto com natureza em corpo 10; folha de aprovação com nota, orientador e três linhas de banca.
3. Citações com inicial maiúscula (a versão ABNT genérica usa caixa-alta, convenção anterior à NBR 10520:2023).
4. `In:` e `et al.` em itálico nas referências; local `[S. l.]` também nos periódicos; eventos com nome, ano e cidade.
5. Número de página em corpo 10, a 2 cm da borda superior; "Key words" no resumo em inglês.

## 3. Pendências
1. **Centro:** assumi "Centro de Engenharia e Computação", que é o que aparece no modelo de natureza do Guia (p. 13) para engenharia; confirmar.
2. **Título do grau e área de concentração** (natureza do trabalho): usei "Mestre em Gestão de Sistemas de Engenharia" sem área de concentração.
3. **Folha de aprovação:** nota, data e banca.
4. **Ficha catalográfica:** solicitar à biblioteca.
5. **Cidade e editora** de alguns eventos e periódicos, que a base de referências não traz (`[S. l.]`, `[s. n.]`).
6. **PDF** e conferência visual (capa, folhas pré-textuais, tabelas, início de seções).
7. **Revisão da tradução do abstract.**

## 4. Conferência com as regras do agente `dissertacao-abnt`
O agente prevê que a norma ABNT vigente e o manual institucional sejam fontes distintas e que o manual prevaleça nos detalhes do programa. A versão UCP segue o fluxo do agente (diagnóstico, base normativa, estrutura, apresentação gráfica, resumo, citações, referências, auditoria, relatório) com estas particularidades:
| Item do agente | Situação nesta versão |
| --- | --- |
| Template institucional | **Não há template em Word da UCP**; usei o template genérico do agente, ajustado ao Guia da UCP (capa, folha de rosto, folha de aprovação, títulos sem número, paginação, corpo 10, referências). O Guia é o manual institucional, e prevalece sobre o template |
| Edições das normas | O Guia cita NBR 14724:2011, 6023:2018, 6028:2021 e 10520:2023. Segui o Guia onde ele é específico e as edições mais recentes (10520:2023: sobrenome em maiúscula e minúscula) onde ele coincide com elas. A NBR 6023:2025 (edição citada pelo agente) não foi consultada no texto integral |
| Preservar o conteúdo do autor | Texto, tabelas e números idênticos aos do LaTeX; mudanças só de forma (numeração das seções e duas frases da introdução, descritas na seção 2) |
| Não fabricar dados | Pendências marcadas (nota, banca, data, ficha, centro, grau); local e editora ausentes como `[S. l.]` e `[s. n.]` |
| Conciliação citação e referência | Por chave do BibTeX: 51 de 51, sem divergência; a triagem automática (`saida/triagem.json`) é heurística e repete os mesmos falsos positivos da versão ABNT |
| Entrega: arquivo editável, PDF e lista de verificação | Editável e relatório entregues; **PDF pendente** e **inspeção visual não feita** |

## 5. Achado nas referências
A entrada `reimers2019` (Sentence-BERT) trazia as páginas 3980-3990, e a primeira página do PDF do artigo mostra 3982-3992. O `referencias.bib` foi corrigido em 2026-10-12, e as três versões (LaTeX, ABNT e UCP) usam 3982-3992. Conferi nos PDFs as páginas de Devlin 2019, Pontiki 2014 e 2016, Wolf 2020, Reimers 2020 e Barbieri 2022, que coincidem com a base; Röder 2015 e Freitas e Vieira 2013 não puderam ser conferidas na primeira página.
