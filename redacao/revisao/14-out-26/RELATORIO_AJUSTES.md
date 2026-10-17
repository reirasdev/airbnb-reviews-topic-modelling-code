# Relatório dos ajustes do orientador (14/10/2026)

Entrega: `redacao/UCP/saida/Raphael_Eiras-...-UCP.docx` (e `.pdf`, 69 páginas), sem comentários do orientador. Planilha com as abas novas: `outputs/resultados_final_20261013_000705_v2.xlsx` (cópia da planilha final com 13 abas `_v2` acrescentadas; as 73 originais ficam intactas; fora do GitHub). Figuras: `redacao/figuras/saida/` (PDF vetorial e PNG de 300 dpi) com o gerador `redacao/figuras/gerar_figuras.py`. Análises novas: `ajustes_v2.py`. Verificador dos números novos: `redacao/verificar_numeros_v2.py`. Branch: `ajustes-orientador-14out26` (um commit por fase). Decisões: `historico/HISTORICO_DECISOES.md`, seções 37 e 38.

A numeração de seções é a da versão UCP já com as inclusões: a nova Seção 1.1 desloca de uma unidade as subseções seguintes da Seção 1 (a antiga 1.3, sobre preço e Nova York, é a 1.4) e a nova Seção 2.2 desloca as seguintes da Seção 2 (a antiga 2.3, medição do sentimento, é a 2.4; a antiga 2.6, desenho analítico, é a 2.7). As páginas são as do PDF (a numeração impressa começa na Introdução: página impressa = página do PDF menos 1). Com as inclusões, as Tabelas 9 e 10 do parecer passaram a ser as Tabelas 10 e 11 e a Tabela 12, a Tabela 13 (a completa é a Tabela 17, no Apêndice D; o Apêndice C passou a ser as estratégias de busca, Tabela 16).

## 1. Código → o que foi feito → onde

| Código | O que foi feito | Seção (página do PDF) |
|---|---|---|
| F1 | Cinco figuras (pipeline; parcelas LMG de A e B com a classificação; diferenças associadas com intervalos de 95%; relatório de diagnóstico; histograma da nota oficial e do índice na mesma amostra de 22.564), vetorial e PNG 300 dpi, legenda e "Fonte: Elaborada pelo autor." | Figuras 1 a 5: Seção 2 (20), 4.1 (34), 4.2 (38), 5 (41), 6.2 (45) |
| F2 | Lista de Figuras e Lista de Abreviaturas e Siglas (24 siglas, todas usadas no texto, inclusive ABSA, BH e PLN, definidas na primeira ocorrência) | Pré-textuais (7 e 9) |
| F3 | Tabela de 12 linhas em página paisagem; versão resumida mantida no corpo com remissão | Apêndice D, Tabela 17 (69); Tabela 13 (46) |
| F4 | Produto técnico: finalidade, público, entradas, saídas, execução, repositório, licença, limites, categoria e avaliação de utilidade (os três últimos com `[PENDENTE]`); Figura 4 na Seção 5; três relatórios no Apêndice B (seis figuras, duas por relatório); repositório (público, GPLv3), categoria e critérios da CAPES e ausência de avaliação por usuários declaradas | Seção 5.1 (41 a 42); Apêndice B (62 a 67) |
| F5 | Subseção "Aspectos éticos, ambiente de execução e disponibilidade": licença CC BY 4.0 (conferida no site em 15/10/2026), LGPD e anonimização, dispensa de avaliação ética (Resolução CNS n. 510/2016, art. 1º, parágrafo único, II e III, conferida no texto oficial do Ministério da Saúde), hardware, versões, tempos de execução, revisões dos modelos, repositório | Seção 2.2 (21 e 22) |
| F6 | `[S. l.]` retirado dos periódicos; prenomes por extenso (Efron, Spearman, Thorndike); 13 referências novas (sete de ABSA e teoria, seis da lista do Consensus sobre tópicos em avaliações do Airbnb); Kano et al. (1984) retirado; 64 referências, todas citadas | Referências (55 a 60) |
| F7 | "Keywords:" | Abstract (6) |
| F8 | Objetivo geral, objetivos específicos (um por pergunta, na mesma ordem), justificativa e aderência à área (com `[PENDENTE]` para a linha de pesquisa) | Introdução (12 e 13) |
| M1 | Parágrafo sobre circularidade (decomposição do conteúdo da nota, mesmos hóspedes, descompasso de período) e sensibilidade com até 30 avaliações (comodidades 41,2% em A e 46,8% em B; limpeza 18,5% e 18,2%) | Seção 2.7 (25); Seção 4.1 (35); limitações 7.3 (51) |
| M2 | Intervalo de Wilson e precisão com os dois anotadores na tabela de classificação, que passa a "indicativa"; parágrafo sobre limpeza (33%, n = 6) sem alterar a regra | Seção 3.6, Tabela 6 (31 a 33) |
| M3 | Subseção sobre os três fatores e Kano; ABSA em hospedagem de 2020 em diante (Airbnb, transformadores multilíngues, LLM); busca bibliográfica (bases, datas, termos, tipos de documento e Apêndice C com 13 consultas); lacuna reescrita com a ressalva de bases, datas e estratégias; assimetria queixa × elogio retomada | Seções 1.1 (15), 1.5 (17), 1.8 (19), 1.9 (19), 7.1 (49); Apêndice C (68) |
| M4 | Quarto elemento da lacuna reescrito como pergunta | Seção 1.8 (19) |
| M5 | Rótulos da Tabela 2 ("Kappa de Cohen (estimativa populacional)", "Kappa ponderado linear (estimativa populacional)"); Conclusões chamam 0,66 e 0,51 de kappa ponderado linear populacional; resumo e abstract não citam esses kappas | Tabela 2 (27); Conclusões (53) |
| M6 | Frase sobre Nova York com a fonte (Deboosere et al., 2019; dados de agosto de 2014 a setembro de 2016, conferido no resumo do artigo) | Seção 1.4 (17) |
| R1 | "Diferença associada (pontos de percentil da nota)" nas duas tabelas; texto e legenda ajustados | Tabelas 10 e 11 (37 a 38) |
| R2 | Precisão de 62% das previsões negativas declarada; sensibilidade com duas menções negativas | Seção 2.7 (25); Seção 4.2 (39) |
| R3 | Comodidades em sete subaspectos (mapa tópico → subaspecto na aba `Mapa_comodidades_v2`); LMG refeita para A e B em duas leituras; Tabela 9 | Seção 4.1, Tabela 9 (35 a 36) |
| R4 | LMG com indicador de ausência para cada aspecto | Seção 4.1 (35) |
| R5 | Remissão ao Apêndice A, com datas e hashes dos commits | Seção 2.4 (23); Apêndice A (61) |
| R6 | 105 mantidos, 80 alterados e 66 reclassificados (estes estão entre os 80, confirmado pelo pesquisador) explicados conforme o histórico; tratamento dos empates no percentil da nota (posto médio; nota 5,0 = percentil 83,8) | Seção 2.5 (24); Seção 2.7 (25) |
| R7 | Distribuição do percentil 27 a 98 (todos os 22.564 anúncios com índice); preço "por diária (mediana, em R$)" | Seção 6.2, Tabela 12 (45) |

Desdobramentos sugeridos nos comentários (classificador direto de aspecto; teste formal da assimetria) estão nas Conclusões (54).

## 2. Resultados novos que qualificam ou enfraquecem algo

1. **Comodidades dividido (R3).** Com a regra do estudo (ao menos 2 sentenças por subaspecto), os subaspectos têm dado próprio em 5% a 25% dos anúncios (62% em "demais"), o $R^2$ total cai (0,320 para 0,266 em A; 0,291 para 0,231 em B) e a soma dos sete subaspectos é de 25,2% em A e 29,8% em B: limpeza (25,3%) e, em A, satisfação geral (23,5%) passam à frente de qualquer subaspecto e o bloco deixa de ser claramente o primeiro. Com ao menos 1 sentença, a soma volta a 42,1% (A) e 48,3% (B), igual ao aspecto inteiro, e nenhum subaspecto se aproxima de limpeza (o maior é banheiro e chuveiro, 9,9% e 10,5%). O texto declara que o primeiro lugar de comodidades como bloco depende de medi-lo com todas as sentenças. A conclusão "comodidades é o aspecto de maior parcela" foi mantida com essa ressalva.
2. **Classificação (M2).** Os intervalos de Wilson dos três aspectos "confiáveis" incluem 0,60 (limpeza 48% a 81%; localização e custo-benefício 55% a 87%); em limpeza os anotadores concordam em 2 de 6 frases e, nas 9 frases atribuídas a limpeza pelo modelo, ambos concordam com ele em 2. A regra não foi alterada; a classificação passou a "indicativa".
3. **Queixas com duas menções (R2).** Confirmam e reforçam (diferença média de −18,9 para −20,9 pontos em A), mas, com o piso de 100 anúncios mantido, 4 das 15 queixas de maior peso (reparos, wi-fi, "experiência geral" e fechadura eletrônica) deixam de ser testáveis (52 a 86 anúncios).
4. **Indicadores de ausência (R4).** Nada contradiz: a ordem dos aspectos não muda (comodidades 34,3% e 37,3% só com o sentimento; 41,8% e 45,6% somando a ausência).
5. Nenhuma conclusão do texto foi invertida.

## 3. Pendências do pesquisador

Nenhum marcador `[PENDENTE]` resta no texto. Último pedido atendido: o período de publicação não foi limitado (o texto diz "sem restrição de período de publicação") e o produto técnico foi enquadrado na categoria "Software/Aplicativo (Programa de computador)", prevista na Ficha de Avaliação da Área Interdisciplinar (Área 45) para 2025 a 2028, conforme a redação que você forneceu. Conferi que o Documento de Área 2025–2028 não lista essa categoria (ela não aparece nele) e não tive acesso à Ficha de Avaliação; a atribuição à Ficha segue a sua indicação.

Continuam em aberto os itens institucionais anteriores (folha de aprovação, ficha catalográfica, centro e título do grau na capa).

## 4. O que foi verificado e como

- **Números:** `redacao/verificar_numeros_v2.py` confere 169 números novos do texto (tabelas 6 e 9, R2, R3, R4, sensibilidade de 30 avaliações, empates, percentis) contra as abas `_v2` e o cache: 169 conferidos, 0 falhas. As análises reproduzem as abas existentes antes de gerar as novas (conferência por `assert` em `ajustes_v2.py`: LMG original e queixas com 1 menção coincidem).
- **Referências:** Matzler e Sauerwein (2002), Füller e Matzler (2008), Vassilikopoulou et al. (2022), Bi et al. (2020), Suryabrata et al. (2026), Xu et al. (2026) e Giritli et al. (2026) conferidos no Crossref (autores, título, periódico, volume, número, páginas e DOI). Só os metadados foram conferidos; não li os textos completos e o texto descreve cada trabalho no nível do título e do resumo. Deboosere et al. (2019): confirmado pelo resumo que usa dados de Nova York. Kano et al. (1984) foi retirado a seu pedido. Citações × lista: 64 de 64. As seis referências do Consensus foram conferidas no Crossref da mesma forma e descritas só no nível do título; o Consensus não é declarado como base de busca no texto (a Seção 1.8 cita Scopus, Web of Science e Google Acadêmico).
- **Licença do Inside Airbnb:** página `get-the-data` do site, em 15/10/2026 (CC BY 4.0). A página de política de dados não abriu.
- **Documento:** PDF gerado pelo Word (66 páginas); olhei a montagem de todas as páginas e, em tamanho cheio, as páginas das Tabelas 6 e 9, da Figura 4, do Apêndice B (uma página) e do Apêndice C (paisagem). Não olhei todas as 66 páginas em tamanho cheio. Nenhuma página em branco; tabelas dentro da margem; paginação visível a partir da Introdução.
- **Ambiente de execução (Seção 2.2):** as versões dos pacotes foram lidas do ambiente virtual em 14/10/2026 (não foram registradas nos logs da época); hardware lido do sistema; tempos dos logs (633,6; 757,1 e 23,8 minutos); revisões dos modelos lidas do cache do Hugging Face (o modelo A tem duas revisões no cache; usei a de `refs/main`).

## 5. Ressalvas

- **Licença do repositório:** o texto da dissertação diz GPLv3, como o arquivo `LICENSE` do repositório. O `README.md` ainda diz AGPLv3; para ficar coerente, ajuste o README (ou troque o `LICENSE` pelo texto da AGPLv3 e me peça para atualizar o texto).

- Os relatórios anonimizados usam como código os seis primeiros caracteres do MD5 do identificador do anúncio, sem sal: não há nome, bairro, frase ou identificador, mas o código pode ser recalculado por quem testar identificadores. Se o PPG exigir anonimização mais forte, gerar o código com sal.
- As versões em LaTeX (fonte) e ABNT: os `.tex` foram atualizados (inclusive figuras, apêndices e bib), mas o PDF do LaTeX e o `.docx` ABNT não foram regenerados (o gerador ABNT não desenha figuras). Compile o LaTeX para conferir; o campo `pendente` do `.bib` (Kano 1984) é ignorado pelo BibTeX.
- Durante o trabalho, heredocs do shell corromperam barras invertidas em alguns `.tex`; os capítulos foram reparados e conferidos (ambientes balanceados, nenhum caractere de controle) antes de gerar o documento.
