# Relatório da formatação ABNT da dissertação

**Arquivo gerado:** `saida/Raphael_Eiras-Decomposicao_por_aspecto_do_sentimento_em_avaliacoes_do_airbnb_rj-ucp_2026-ABNT.docx` (45 páginas no Word; sumário e lista de tabelas atualizados no Word).
**Origem:** capítulos em `redacao/latex/capitulos/` e `redacao/latex/referencias.bib`, lidos sem alteração. Nada foi alterado fora de `redacao/abnt/`.
**Método:** skill `dissertacao-abnt` (esta pasta), partindo de `templates/template-dissertacao-abnt.docx`. Gerador: `scripts/gerar_dissertacao.py`; atualização de campos: `scripts/atualizar_campos_e_pdf.ps1`; extração para triagem: `scripts/extrair_texto.py`.

## 1. Escopo e limitações da análise
- **PDF não gerado.** A exportação automática do Word para PDF travou nesta máquina (o Word acusa licença não original). Para obter o PDF: abrir o `.docx` no Word e usar Arquivo > Exportar > Criar PDF.
- **Inspeção visual não feita.** Sem PDF, não conferi visualmente capa, tabelas e quebras de página. Os campos (sumário, lista de tabelas) foram atualizados pelo Word, e a estrutura foi conferida por extração do texto.
- **Manual do programa não disponível.** Valores institucionais seguem o template (convenções usuais) e estão listados como pendência.

## 2. Estrutura produzida
Capa; folha de rosto; ficha catalográfica (página reservada); folha de aprovação; resumo e palavras-chave; abstract e keywords; lista de tabelas; sumário; seções 1 a 9 (Introdução, Referencial teórico, Dados e método, Validação da medição, O que o texto revela sobre a nota, Aplicação, Um índice único acrescenta algo?, Discussão e limitações, Conclusões); referências.

## 3. Decisões adotadas (e origem)
| Item | Decisão | Origem |
| --- | --- | --- |
| Sistema de citação | Autor-data com sobrenome em maiúscula e minúscula, convenção da NBR 10520:2023 (`(Hu; Zhang; Pavlou, 2009)` e `Hu, Zhang e Pavlou (2009)`); mais de 3 autores: `et al.`. Nas referências, o sobrenome continua em caixa-alta (NBR 6023) | NBR 10520:2023 |
| Referências | Ordem alfabética, uma entrada por obra, destaque em negrito no título do periódico ou da obra, DOI quando existe, `Disponível em` e `Acesso em: 10 out. 2026` para fontes só com URL (datas em que as páginas foram consultadas) | NBR 6023 |
| Local e editora não informados | `[S. l.]` e `[s. n.]` | NBR 6023 |
| Formato de página, fonte, espaçamento | Template: A4, margens 3 cm (sup. e esq.) e 2 cm (inf. e dir.), Times New Roman 12, entrelinha 1,5 | Convenção usual do template, a confirmar no manual |
| Numeração das seções | Progressiva digitada ("1", "2.1") | NBR 6024 |
| Tabelas | Título acima ("Tabela N – título", campo SEQ), traços horizontais, sem linhas verticais, fonte reduzida nas largas, **"Fonte: Elaborada pelo autor."** abaixo; lista de tabelas automática | NBR 14724 / norma de apresentação tabular |
| Agradecimentos e apêndice | Removidos (elementos opcionais) | NBR 14724 |
| Capa e folha de rosto | Instituição, programa, autor, título (subtítulo sem negrito), local e ano; sem coorientador e sem unidade/faculdade | Dados informados pelo autor |
| Citações em Seção/tabela | Texto, tabelas e remissões mantidos como no LaTeX | Preservar o conteúdo do autor |
| Resumo em inglês | Tradução do resumo em português preparada para este arquivo | Necessário para NBR 6028 |

## 4. Pendências (não decidi sem fonte)
1. **Manual institucional da UCP/programa:** margens, fonte, capa, paginação e modelo de referências.
2. **Ficha catalográfica:** elaborada pela biblioteca (página reservada).
3. **Folha de aprovação:** data da defesa e nomes e instituições dos dois examinadores (marcadores entre colchetes).
4. **Unidade ou faculdade** na capa (removida por não estar confirmada).
5. **Título do grau** ("Mestre" sem área) e área de concentração.
6. **Resumo em inglês:** revisão da tradução pelo autor.
7. **Locais e editoras** de anais e livros sem esses dados na base de referências (marcados `[S. l.]` e `[s. n.]`).

## 5. Conciliação de citações e referências
- Por chave do BibTeX (exata): 51 chaves na lista, 51 citadas no texto, nenhuma citação sem entrada.
- O script de triagem (`audit_dissertation_text.py`), que é heurístico, acusou 12 citações sem referência e 22 referências sem citação. São falsos positivos: ele só reconhece o primeiro autor e lê números de página como ano (ex.: "BRIDGES (2057)"). Ele também acusou "marcador TODO" no texto da seção 3.5 por causa da palavra "todo" em português. Saídas: `saida/triagem.json`, `saida/texto_extraido.txt`.

## 6. Defeitos encontrados nos arquivos de origem (LaTeX)
Os dois defeitos abaixo foram corrigidos no LaTeX (commit `ab89c37`) e o arquivo ABNT foi regenerado depois da correção.
1. `referencias.bib`, entrada `souza2020`: `F{'a}bio` e `El{'e}trica` estavam sem a barra invertida; agora `F{'a}bio` e `El{'e}trica`.
2. `cap2_referencial.tex`, seção "Lacuna": a frase final estava quebrada; agora é uma lista única separada por ponto e vírgula, com "e" antes do último item.

## 7. Checklist final
| Área | Situação |
| --- | --- |
| Base normativa | Edições de referência da skill (NBR 14724:2024, 10520:2023, 6023:2025, 6024:2012, 6027:2012, 6028:2021); manual da UCP não confirmado |
| Estrutura | Elementos obrigatórios presentes, exceto ficha e aprovação preenchidas (pendências) |
| Pré-textuais | Capa, folha de rosto, resumo, abstract, lista de tabelas e sumário presentes e coerentes |
| Paginação | Pelo template: capa não conta, número visível a partir da introdução; conferir no PDF |
| Seções | Numeração progressiva e sumário coincidem (campo atualizado pelo Word) |
| Citações | Sistema único autor-data |
| Referências | Padronizadas pelo gerador; conciliação exata por chave sem divergência |
| Ilustrações | 13 tabelas com número, título, fonte e chamada no texto; não há figuras |
| Arquivo final | DOCX gerado e campos atualizados; **PDF pendente** (exportar no Word) |
| Transparência | Incertezas e pendências listadas acima |

## 8. Atualização de 2026-10-12 (noite)
- Citações no estilo da NBR 10520:2023 (inicial maiúscula), a pedido do autor; antes estavam em caixa-alta.
- Páginas de Reimers e Gurevych (2019) corrigidas para 3982-3992 (conferidas no PDF do artigo) em `referencias.bib`.
