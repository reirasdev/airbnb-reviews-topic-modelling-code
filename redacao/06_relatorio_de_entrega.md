# Relatório de entrega (estado em 13/10/2026)

Dissertação: *O que as avaliações revelam sobre a nota: decomposição por aspecto do sentimento em avaliações de hóspedes do Airbnb no Rio de Janeiro* (Raphael Rodrigues Eiras; orientador: Prof. Dr. Rodolfo Nicolay). Branch: `estrategia-v3-sentimento-b-unificado`.

## 1. Modelo principal e os números que decidiram
O modelo principal é o **A** (`cardiffnlp/twitter-xlm-roberta-base-sentiment`). A regra foi registrada antes da execução do modelo B: B seria o principal se o IC de 95% da diferença B menos A no kappa ponderado linear populacional excluísse zero a favor de B.

| Medida (297 sentenças rotuladas, ponderadas pela população) | A | B | Diferença B − A (IC 95%) |
|---|---:|---:|---|
| Kappa ponderado linear | 0,66 | 0,51 | **−0,141 [−0,272; −0,012]** (exclui zero, a favor de A) |
| Acurácia | 87,2% | 84,9% | −0,023 [−0,078; 0,021] |
| Kappa ponderado linear, só português | — | — | −0,169 [−0,323; 0,011] (inclui zero) |
| Acurácia na amostra (não ponderada) | 58,9% | 63,3% | B melhor, porque a amostra foi estratificada pelas previsões de A |

O tamanho efetivo da amostra ponderada é de 72 sentenças (intervalos largos). B acompanha todos os resultados como robustez. Segundo anotador (100 sentenças): concordância no sentimento kappa 0,86 (IC 0,76 a 0,94) e no aspecto kappa 0,62 (IC 0,51 a 0,73).

## 2. O que mudou em relação à versão anterior, por bloco
As abas do modelo A são idênticas às da versão anterior (conferido por comparação de planilhas); o que muda é o que se acrescenta e como se lê.

| Bloco | Mudança |
|---|---|
| Enquadramento | Ocupação e receita estimadas passam a ser tratadas como **índices de volume de avaliações** (a fórmula reproduz o campo em 100% dos 42.013 anúncios). O objeto central é a nota e o texto, e não desempenho econômico. |
| Medição (Seções 3 e 4) | Novo: segundo modelo (B), regra pré-registrada, acurácias e kappas populacionais, segundo anotador, checagem com LDA (mapa confirmado) e classificação dos aspectos: **confiáveis** limpeza, localização e custo-benefício; **cautela** os outros sete. |
| Importância dos aspectos | A inalterado: comodidades 42,5% do R² da nota global e limpeza 19,6%. B confirma a ordem (47,8% e 18,8%). Das 15 queixas de maior peso, 13 coincidem nos dois modelos. Satisfação geral pesa 17,5% em A e 9,9% em B. |
| Aplicação (diagnóstico por anúncio) | Sem mudança; os três exemplos anonimizados saem idênticos. |
| Índice sintético (R_syn) | Resultado **nulo e secundário** nos dois modelos (ganho de R² fora da amostra além da nota oficial com intervalo incluindo zero em 12 de 12 comparações). Coeficientes dentro da amostra: 6 de 12 (A) e 8 de 12 (B) com q < 0,05, mas **não robustos** (mudam de sinal por escopo e por modelo; não confirmados fora da amostra). Só 5.142 dos 9.373 anúncios de nota 5,0 têm o índice. Shrinkage: decisão tomada depois de ver o resultado; as duas versões são reportadas. |
| Limite de 30 avaliações | Truncados 32% dos elegíveis (5,2% entre os de nota 5,0); confiabilidade do sentimento por anúncio 0,50 com 30 avaliações. |
| Sazonalidade e eventos | **Retirada do trabalho** por decisão do pesquisador (era opcional e o resultado não foi excelente). Arquivada em `historico/`. |

**Conclusões do texto antigo contrariadas ou enfraquecidas**
1. Menor proporção de frases negativas nos eventos de música e em Corpus Christi: **não replica com o modelo B** (razões de chances de 0,97 a 0,99, sem significância); o conteúdo por aspecto nos eventos coincidia entre os modelos em apenas 5 de 70 combinações. Por isso a seção foi retirada.
2. Coeficientes de R_syn dentro da amostra, antes lidos como achado: agora declarados não robustos e fora da síntese.
3. Peso da satisfação geral na nota global: enfraquecido por B (17,5% em A, 9,9% em B).
4. Peso de comodidades: mantido nos dois modelos, mas com a ressalva de que o aspecto tem 44% de precisão de atribuição e não tem subnota para validar.
5. Leitura econômica de ocupação e receita: abandonada (índices de volume). O coeficiente de R_syn de −1,34 que resultava do controle pelas avaliações dos últimos 12 meses é artefato desse controle e some com a fórmula exata.
6. Escolha do modelo: B é melhor na amostra e A na população; a escolha vem da regra, e não de uma preferência.

## 3. Caminhos
| Item | Caminho |
|---|---|
| Rascunho unificado de resultados | `redacao/01_resultados_unificado.md` e `.pdf` (9 seções) |
| Dissertação em LaTeX (formato EngUCP) | `redacao/latex/Raphael_Eiras-...-Latex.tex` e `.pdf`, capítulos em `redacao/latex/capitulos/`, bibliografia `redacao/latex/referencias.bib` (51 entradas) |
| Dissertação em formato ABNT | `redacao/abnt/saida/Raphael_Eiras-...-ABNT.docx` e `.pdf`, relatório `RELATORIO_ABNT.md` |
| Dissertação no formato do Guia da UCP | `redacao/UCP/saida/Raphael_Eiras-...-UCP.docx` e `.pdf`, relatório `RELATORIO_UCP.md` |
| Planilha final (73 abas, os dois modelos lado a lado) | `outputs/resultados_final_20261013_000705.xlsx` (não vai ao GitHub) |
| Arquivados | `historico/rascunhos_v2/` (resultados da estratégia anterior e texto de sazonalidade retirado), `historico/v1_*`, `historico/v2_*` |
| Decisões | `historico/HISTORICO_DECISOES.md` (seções 29 a 36) |
| Referências | `redacao/05_referencias_verificadas.md`; PDFs e planilha de conferência em `fontes/referencias/` (fora do repositório) |
| Enquadramento e estrutura | `redacao/00_enquadramento.md`, `redacao/04_estrutura_capitulos.md` |

## 4. Correção pedida → o que foi feito → onde
As seções citadas são as do rascunho unificado (`01_resultados_unificado.md`); na dissertação (LaTeX, ABNT e UCP) a numeração é outra (por exemplo, a validação é a Seção 4 no LaTeX e a Seção 3 na versão UCP).
| Correção pedida | O que foi feito | Onde |
|---|---|---|
| Segundo modelo de sentimento (B) | Rodado em todo o corpus; cadeia a jusante refeita com A e B | Seções 3 a 7 do rascunho; abas `*_mB` e `LadoALado_*` |
| Regra de escolha do modelo | Pré-registrada e aplicada; principal = A | Seção 4.3; `Diferenca_B_menos_A` |
| Enquadramento dos desfechos | Índices de volume de avaliações | Seção 2; `00_enquadramento.md` |
| Fusão das duas estratégias | Texto contínuo, cada seção liga à anterior e cita as abas | `01_resultados_unificado.md` |
| R_syn discrimina a nota 5,0 | 5.142 de 9.373 (54,9%), com tabela de seleção | Seção 7.2; `Selecao_Teto` |
| Coeficientes dentro da amostra | q de Benjamini-Hochberg e rótulo "não robustos" | Seção 7.3; `Comparacoes_Multiplas` |
| Estrelas esperadas | Uso ordinal, com a correlação com o rótulo manual | Seções 3 e 4.1 (0,64 em A e 0,63 em B) |
| Shrinkage | Justificativa teórica primeiro, registro da decisão posterior, duas versões | Seções 7.1 e 7.5 |
| A e B discordam | Números dos dois, sem escolher o conveniente | Seções 4 e 7 |
| Resultado nulo | Apresentado como legítimo, com duas leituras | Seção 7.6 |
| C_v e LDA | C_v só descritivo; LDA como checagem, mapa confirmado | Seções 3 e 4.5 |
| Segundo anotador | Planilha cega rotulada; kappa 0,86 e 0,62 | Seção 4.6; aba `Segundo_Anotador` |
| Sazonalidade | Retirada do trabalho | `HISTORICO_DECISOES.md`, seção 36 |
| Redação final | Dissertação completa em três formatos, com referências verificadas | `redacao/latex`, `redacao/abnt`, `redacao/UCP` |

## 5. Pendências
Resolvidas pelo pesquisador: mapa do LDA (confirmado sem alterações), rotulagem do segundo anotador (feita) e título (escolhido).

Em aberto:
1. Folha de aprovação: nota, data e banca. Ficha catalográfica (solicitar à biblioteca).
2. Confirmar o centro ("Centro de Engenharia e Computação") e o título do grau na capa e na folha de rosto.
3. Revisão da tradução do abstract.
4. Locais e editoras de alguns anais e periódicos que a base de referências não traz (marcados `[S. l.]` e `[s. n.]`).
5. Revisão da prosa pelo orientador.

## 6. O que foi verificado e como, e o que não foi
**Verificado**
- **Números do rascunho × planilha:** `verificar_numeros.py` confere cada número contra as abas citadas na própria seção: 994 conferidos; 19 não localizados, todos limiares de critério, contagens de desenho ou totais derivados de somas (nenhum é resultado sem fonte). A planilha foi regenerada em 13/10 e a contagem se manteve.
- **Dissertação × rascunho:** todos os números dos capítulos em LaTeX aparecem no rascunho unificado (único arredondamento: 0,106 para 0,1058).
- **Regressão:** as abas do modelo principal coincidem com as da planilha de 04/10.
- **Referências:** 51 entradas conferidas em Crossref, JMLR, ACL Anthology, arXiv e Hugging Face; o pesquisador obteve 47 PDFs, cuja identidade conferi e dos quais conferi por busca de trechos as afirmações do Capítulo 2 (quatro frases foram ajustadas); Kish 1992 conferido por leitura; conciliação citação × referência por chave: 51 de 51.
- **PDFs (LaTeX, ABNT e UCP):** inspeção visual de capa, folhas iniciais, sumário, tabelas, seções e referências, mais medição automática de margens, fontes e quebras de tabela; defeitos encontrados foram corrigidos e reconferidos.
- **Guia da UCP:** lido por inteiro e aplicado na versão UCP.

**Não verificado**
- Textos de artigos fechados lidos só em partes (trechos e resumos); Lindeman et al. (1980) é livro e não foi lido; NBR 6023:2025 não foi consultada.
- Inspeção visual feita por amostra de páginas, e não nas 45 de cada versão; eu não exportei PDF pelo Word (você exportou).
- Compilação do LaTeX feita por você, não por mim.
- Os itens institucionais da seção 5.
- Causalidade: nenhum resultado a sustenta, e o texto usa linguagem de associação.
- O mapa do LDA e o segundo anotador foram confirmados por você; a qualidade da rotulagem de referência (um pesquisador, 297 sentenças) é uma limitação declarada.
