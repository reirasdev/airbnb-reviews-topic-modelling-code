# Prompt para o Claude Code: ajustes finais da dissertação (versão UCP)

Você vai aplicar os ajustes pedidos pelo orientador na dissertação "O que as avaliações revelam sobre a nota: decomposição por aspecto do sentimento em avaliações de hóspedes do Airbnb no Rio de Janeiro" (mestrado profissional, UCP). O pipeline de análise, a planilha de resultados e o texto já existem neste repositório. O método está aprovado: não refaça nenhuma análise existente e não altere nenhum número já publicado, a não ser que a correção abaixo o exija explicitamente.

Os ajustes estão registrados em dois arquivos do orientador:

- `Raphael_Eiras-Decomposicao_por_aspecto_do_sentimento_em_avaliacoes_do_airbnb_rj-ucp_2026-UCP_comentado.docx`: a dissertação com 29 comentários, cada um iniciado por um código (F1 a F8, M1 a M6, R1 a R7).
- `Log_de_Ajustes_Dissertacao.docx`: a tabela de ajustes com local, prioridade e tipo de cada código.

Execute tudo até o fim. Onde um ajuste depender de informação que só o pesquisador tem, escreva o texto com um marcador visível `[PENDENTE: o que falta]` e siga em frente.

## Fase 0: Reconhecimento

1. Leia os comentários do documento comentado (extraia `word/comments.xml` e localize o trecho de cada um pelo `commentRangeStart`). Monte uma tabela código → seção → pedido.
2. Descubra qual é a fonte do texto: um projeto LaTeX convertido para o modelo da UCP, ou o próprio `.docx`. Se houver conversão (pandoc, script, modelo de referência), edite a fonte e regenere o `.docx` pelo mesmo processo. Se o `.docx` for a fonte, edite-o preservando os estilos do modelo da UCP (títulos, legendas, "Fonte: Elaborada pelo autor.", espaçamento, paginação a partir da Introdução).
3. Localize a planilha `resultados_final_20261013_000705.xlsx`, os scripts do pipeline, os caches (sentenças, sentimento A e B, tópicos, mapa tópico→aspecto, frases rotuladas pelos dois anotadores) e `historico/HISTORICO_DECISOES.md`.
4. Crie um branch novo. Faça um commit por fase.

## Regras que valem para tudo

- Todo número novo vem de uma aba da planilha ou de um log de execução. Cada análise nova gera aba nova na planilha (sufixo `_v2`) e entrada no histórico de decisões.
- Mesmas sementes, mesmas dobras, mesmas regras de amostra. Modelo principal continua sendo A; B acompanha cada resultado novo.
- Linguagem de associação, nunca causal.
- **Não invente referências.** Toda referência nova deve ser conferida (autor, título, ano, periódico, volume, páginas e DOI) por resolução do DOI ou consulta à Crossref. Se não conseguir conferir, não inclua: deixe `[PENDENTE: referência a confirmar — tema]`.
- Não altere conclusões existentes a menos que uma análise nova as contradiga; se contradisser, ajuste o texto e registre no relatório final.

## Fase 1: Análises novas (sobre dados existentes)

**M2 — Intervalos na classificação dos aspectos.** Para a precisão de atribuição por aspecto (cerca de 27 frases cada), calcule o intervalo de Wilson de 95%. Calcule também a precisão combinando os rótulos dos dois anotadores nas 100 frases em comum, por aspecto, com n. Gere a aba `Classificacao_IC_v2`.

**R2 — Menções negativas com ruído.** Refaça a análise de queixas por tópico exigindo ao menos duas sentenças negativas no tópico (em vez de uma), mesma especificação e mesma correção de Benjamini-Hochberg. Reporte quantas das 15 queixas de maior peso se mantêm e como mudam as diferenças. Aba `Queixas_min2_v2`.

**R3 — Comodidades dividido.** Usando os tópicos já mapeados para comodidades, defina subaspectos por agrupamento dos tópicos (banheiro e chuveiro; climatização; cozinha e utensílios; cama e colchão; internet; manutenção e reparos; demais comodidades). Registre o mapa tópico→subaspecto em aba própria. Refaça apenas a decomposição LMG da nota global com os subaspectos no lugar de comodidades, para A e B. Aba `LMG_comodidades_v2`.

**R4 — Imputação.** Refaça a decomposição LMG da nota global acrescentando um indicador de ausência para cada aspecto imputado. Compare as parcelas com a versão atual. Aba `LMG_ausencia_v2`.

**F3 — Tabela 12 completa.** Extraia da aba `Analise_A` (e `Analise_A_mB`) as 12 linhas (três desfechos × quatro escopos) com M1 − M0, M2 − M1 e M3 − M1 para A e M3 − M1 para B.

**Dados das figuras.** Gere os dados de cada figura da Fase 2 a partir da planilha (não recalcule nada que já exista).

## Fase 2: Figuras (F1)

Gere em vetorial (PDF ou SVG) e em PNG 300 dpi, mesma paleta e tipografia, legendas em português, sem título dentro da imagem (o título vai na legenda):

1. **Pipeline do estudo**: dados → sentenças → sentimento (A e B) → tópicos → aspectos → perfil por anúncio → análises → diagnóstico.
2. **Compressão da nota**: histograma da nota oficial ao lado do histograma do índice sintético (mesma amostra de 22.564 anúncios).
3. **Decomposição da nota global**: barras horizontais da parcela LMG por aspecto, A e B lado a lado, com a classificação (confiável/cautela) indicada.
4. **Queixas e elogios**: gráfico de pontos com intervalos das diferenças associadas (pontos de percentil) para as queixas e elogios das Tabelas 9 e 10. Se os intervalos não estiverem na planilha, calcule-os com a mesma especificação e registre.
5. **Relatório de diagnóstico**: uma página real de um dos três exemplos anonimizados (confira que não há nome de pessoa, endereço ou identificador do anúncio).

Insira cada figura no ponto do texto em que é citada, com legenda "Figura n – ..." e "Fonte: Elaborada pelo autor." no padrão do modelo.

## Fase 3: Texto

Aplique na ordem abaixo. Ao terminar cada item, anote no relatório o que mudou e onde.

- **F2** Criar Lista de Figuras e Lista de Abreviaturas e Siglas (ABSA, AUC, BERT, BH, GBM, HC3, IC, LDA, LGPD, LLM, LMG, PLN e as demais usadas), no lugar previsto pelo modelo da UCP.
- **F7** No abstract, "Key words:" → "Keywords:".
- **F8** Na Introdução, explicitar: objetivo geral; objetivos específicos, um por pergunta de pesquisa, na mesma ordem; justificativa; aderência à área do PPG em Gestão de Sistemas de Engenharia (gestão da qualidade de serviços e apoio à decisão). Use as frases que já existem sempre que possível.
- **M6** Na Seção 1.3, a frase sobre Nova York precisa de fonte. Confira se Deboosere et al. (2019) sustenta a afirmação (leia o resumo pelo DOI); se sim, cite nessa frase; se não, reescreva a frase sem a afirmação ou marque `[PENDENTE]`.
- **M3** Referencial teórico:
  - Nova subseção na Seção 1 sobre formação da satisfação e assimetria de atributos: teoria dos três fatores e modelo de Kano (atributos básicos, de desempenho e de encantamento). Pontos de partida para busca, todos a conferir antes de citar: Kano et al. (1984); Matzler e Sauerwein (2002); Füller e Matzler (2008, Tourism Management).
  - Na Seção 1.4, descrever a busca bibliográfica (bases, termos, período) a partir do que estiver registrado no repositório; se não houver registro, `[PENDENTE: descrição da busca]`. Acrescentar estudos de análise de sentimento por aspecto em hospedagem publicados de 2020 em diante, inclusive com modelos de linguagem de grande porte, todos conferidos.
  - Na Seção 7.1, retomar a assimetria entre queixas (−10 a −26 pontos) e elogios (+5 a +11) à luz dessa teoria, dizendo quais aspectos se comportam como básicos. Deixar claro que é leitura descritiva, sem teste formal.
- **M4** Na Seção 1.7, reescrever o quarto elemento como pergunta: falta saber se um índice construído a partir do texto acrescenta algo à nota oficial.
- **F5** Na Seção 2.1 (ou subseção nova "Aspectos éticos e disponibilidade"): uso de dados públicos; licença do Inside Airbnb (confira no site); tratamento conforme a LGPD, com anonimização de citações e exemplos; ambiente de execução (hardware, tempo de inferência, versões de Python, Transformers, BERTopic e dos dois modelos), extraído dos logs; repositório de código e de resultados agregados (`[PENDENTE: URL]` se não existir).
- **R5** Na Seção 2.3, remeter a um apêndice com o registro datado da regra de escolha do modelo (entrada do histórico de decisões ou commit anterior à execução de B, com data e hash).
- **R6** Na Seção 2.4, explicar a relação entre os 105 mantidos, os 80 alterados e os 66 reclassificados, conforme o histórico. Na Seção 2.6, dizer como são tratados os empates no percentil da nota.
- **M1** Na Seção 2.6, novo parágrafo: nota e texto vêm dos mesmos hóspedes; a análise decompõe o conteúdo da nota e não a prevê por fator independente, e é isso que o estudo pretende; o sentimento usa as 30 avaliações mais recentes e a nota acumula todas, e a sensibilidade com anúncios de até 30 avaliações (que já existe) mostra que isso pouco muda.
- **R2** Na Seção 2.6 ou 4.2, declarar que a previsão "negativo" do modelo A acerta 62% e reportar o resultado da sensibilidade com duas menções.
- **M5** Tabela 2: "Kappa ponderado pela população" → "Kappa de Cohen (estimativa populacional)" e "Kappa ponderado linear pela população" → "Kappa ponderado linear (estimativa populacional)". Nas Conclusões, chamar 0,66 e 0,51 de kappa ponderado linear populacional. Conferir a mesma terminologia no resumo e no abstract.
- **M2** Tabela 6 com os intervalos de Wilson e a precisão combinada dos anotadores; trocar "classificação" por "classificação indicativa" onde for o caso; discutir em um parágrafo a concordância de 33% entre anotadores em limpeza (n = 6), sem esconder que limpeza continua classificada como confiável pela regra.
- **R4 e R3** Na Seção 4.1, um parágrafo para cada sensibilidade nova, com remissão às abas. Se a divisão de comodidades mudar a leitura (por exemplo, banheiro ou climatização concentrando a parcela), dizer isso e conectar com a Tabela 9.
- **R1** Tabelas 9 e 10: "Efeito no percentil" → "Diferença associada (pontos de percentil)". Conferir o texto ao redor.
- **F4** Transformar a Seção 5 e um apêndice novo na apresentação do produto técnico: finalidade; público (anfitriões e empresas gestoras); entradas (dados do Inside Airbnb e identificador do anúncio); saídas (as quatro partes do relatório); como executar (comando, dependências); onde está o código; licença; limites de uso (associação, não causa; aspectos de cautela). A categoria do produto segundo o regulamento do PPG fica como `[PENDENTE: categoria CAPES]`. Inserir a Figura 5 na Seção 5 e os três relatórios no apêndice. Se houver registro de opinião de usuário, incluir; se não, `[PENDENTE: avaliação de utilidade por anfitrião ou gestora]`.
- **R7** Na Seção 6.2, dizer de qual distribuição é o percentil 27–98; na Tabela 11, unidade "R$ por diária".
- **F3** Tabela 12 completa (12 linhas) em página paisagem ou apêndice; no corpo, versão resumida legível com remissão.
- **F6** Revisar as referências contra a NBR 6023: retirar "[S. l.]" de artigos de periódico; prenomes por extenso e padronizados (Efron, Spearman, Thorndike); incluir as referências novas; conferir que toda citação no texto está na lista e vice-versa.

Depois de tudo: atualizar sumário, Lista de Tabelas e Lista de Figuras; conferir numeração e remissões ("Tabela n", "Figura n", "Seção n"). Atualizar resumo, abstract e Conclusões só se algum resultado novo mudar o que eles dizem.

## Fase 4: Verificação

1. Extraia todos os números do texto revisado e confira cada um contra a aba citada. Corrija o que não bater.
2. Confira que cada um dos 29 comentários foi tratado. Gere uma tabela "código → o que foi feito → seção/página".
3. Gere o PDF do `.docx` final, olhe todas as páginas e confira: figuras legíveis, tabelas dentro da margem, nenhuma página em branco, paginação a partir da Introdução, legendas e fontes no padrão.
4. Liste todos os marcadores `[PENDENTE]` que ficaram no texto.

## Entrega

- `.docx` final no modelo da UCP, sem os comentários do orientador.
- Planilha com as abas `_v2`.
- Pasta com as figuras (vetorial e PNG) e o script que as gera.
- Relatório curto com: a tabela da Fase 4, item 2; qualquer resultado novo que contrarie ou enfraqueça algo do texto anterior; a lista de pendências para o pesquisador; o que foi verificado e como.
