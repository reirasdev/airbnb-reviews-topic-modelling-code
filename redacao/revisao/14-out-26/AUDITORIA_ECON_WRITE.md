# Auditoria da dissertação com o skill econ-write (modo de revisão)

Versão auditada: `redacao/UCP/saida/...-UCP.docx` do branch `awesome-ai-for-economists` (69 páginas, depois da aplicação das sugestões do skill ao Resumo, à Introdução e às Conclusões). Roteiro: `review-checklist.md` do skill (revisão rápida, três revisores simulados, lista contra padrões de escrita de IA e nota de 0 a 100). O roteiro foi feito para artigos de economia; a nota é uma referência, não uma avaliação formal. Nada no texto foi alterado por esta auditoria.

## Nota: 73/100 ("trabalho sólido, precisa de mais uma rodada")

| Componente | Nota | Observação |
|---|---:|---|
| Título | 6/10 | Nomeia objeto e desfecho, mas tem 22 palavras (o roteiro pede menos de 15) |
| Resumo | 8/10 | Concreto e com números; 183 palavras (o roteiro pede menos de 150, mas o Guia da UCP exige ao menos 150) |
| Introdução | 15/20 | Gancho com fato; o resultado principal só aparece no 4º parágrafo; literatura fica no Referencial, como o modelo da UCP pede |
| Método e identificação | 11/15 | Validação em camadas é um ponto forte; faltam intervalos para as parcelas LMG e controles adicionais nas queixas |
| Apresentação dos resultados | 11/15 | Efeitos em pontos de percentil, sem tradução para a escala de estrelas |
| Qualidade da escrita | 11/15 | Frases variadas, mas parágrafos longos |
| Tabelas e figuras | 7/10 | Figuras boas; tabelas quase sem nota explicativa |
| Conclusão | 4/5 | Abre pelo achado; perto do limite de uma página |

## As três mudanças de maior impacto

1. **Intervalos de confiança para as parcelas LMG.** A conclusão central (comodidades 42,5%, limpeza 19,6%) é apresentada sem incerteza. Um *bootstrap* sobre os 28.889 anúncios, com a mesma semente, dá intervalos de 95% para cada parcela e mostra se a ordem entre aspectos se sustenta. Cabe numa aba `_v2` nova e em uma frase na Seção 4.1.
2. **Notas sob as tabelas.** Só uma tabela tem "Nota:". As Tabelas de queixas e elogios deveriam dizer, sob o título, o que a diferença associada controla (volume de avaliações e de sentenças), o erro padrão (HC3), a correção (BH) e a unidade. A tabela de classificação deveria explicar "ambos" e "ao menos um". O custo é baixo e o efeito é de uma tabela que se lê sozinha.
3. **Tradução das diferenças de percentil para a escala da nota.** "Quedas de 10 a 26 pontos de percentil" é difícil de dimensionar. Uma linha dizendo quantas estrelas, em média, separam anúncios com e sem a queixa (ou a probabilidade de nota 5,0) tornaria o resultado utilizável pelo anfitrião. Exige uma análise curta nova sobre dados que já existem.

## Revisor 1: o metodologista
- Há pontos fortes: regra de escolha do modelo fixada antes da execução (com data e hash no Apêndice A), validação ponderada pela população, segundo anotador, correção de Benjamini e Hochberg, erro padrão HC3, sensibilidades por segmento e por modelo, e a circularidade nota-texto declarada na Seção 2.7.
- Falta intervalo nas parcelas LMG e nos pesos por aspecto (mudança 1).
- As queixas controlam só o volume de avaliações e de sentenças. Tipo de acomodação, bairro e preço podem confundir a diferença associada. Uma sensibilidade com esses controles responderia à objeção óbvia de uma banca.
- Os erros padrão tratam os anúncios como independentes. Uma sensibilidade com agrupamento por bairro seria uma checagem simples.
- A seleção está descrita (28.889 anúncios com texto de 42.013), mas não se discute se a diferença entre anúncios incluídos e excluídos pode alterar as parcelas.

## Revisor 2: o especialista da área
- A contribuição está posicionada em relação a Luo e Tang (2019), Cheng e Jin (2019) e Sutherland e Kiatkawsin (2020), e agora também a Ding et al. (2020, 2021) e Zhang (2019).
- A literatura é descrita estudo por estudo na Seção 1.3 ("X concluem… Y adaptam… Z extraem…"). O roteiro chama isso de enumeração sem história; vale ligar os estudos com um "mas" que leve ao que falta (a validação da medida por aspecto).
- A Seção 7.1 compara os resultados com Cheng e Jin e com Sutherland e Kiatkawsin, apontando coincidências e a diferença de desfecho. Não há discussão de estudos que cheguem a conclusões opostas; vale dizer se existem.
- As implicações práticas estão contidas (associação, não causa), o que é adequado. A dimensão econômica fica na mudança 3.
- A validade externa (um município, uma plataforma, uma coleta) é declarada na Seção 7.3.

## Revisor 3: o crítico de escrita
- Estrutura: frases com extensão variada (23% até 12 palavras, 45% de 13 a 25, 32% acima de 25; desvio-padrão de 11 palavras). Os parágrafos têm em média 107 palavras e 120 passam de 25 palavras; 20 passam de 150 e 9 de 200 (o maior tem 271). Dividir os mais longos melhora a leitura.
- Voz passiva: cerca de 130 construções passivas em 15 mil palavras, em geral em descrições de método, onde o skill aceita. Vale trocar as que aparecem em frases de resultado.
- Poucos marcadores de cautela ("parece" aparece 6 vezes). A Seção 4 e a Seção 7 já cautelam bem; os trechos de resultados poderiam usar "provavelmente" e "uma leitura é" onde a evidência é indireta.
- Nenhum parágrafo abre com citação; apenas um abre com "Esta seção". Sem preâmbulos do tipo "É importante notar".
- Tabelas: ver mudança 2.

## Lista contra padrões de escrita de IA
- Palavras do roteiro, ou seus equivalentes em português ("crucial", "abrangente", "multifacetado", "notavelmente", "além disso" em excesso): só "além disso" aparece (3 vezes), sem abuso. "Robusto" aparece em sentido estatístico.
- Extensão de frases e parágrafos: variada, sem a uniformidade típica.
- Termos específicos e instituições nomeadas: abundantes (Inside Airbnb, BERTopic, HC3, LMG, nomes de bairros e de tópicos).
- Sinais estruturais a vigiar: a lista de contribuições da Introdução e as sequências "A primeira… A segunda…" são perfeitamente paralelas. Cabe variar a construção em um ou dois itens.
- O roteiro recomenda travessões e apostos como marca de texto humano. Fica sem aplicação, porque você não usa travessão.

## Menores
- Título mais curto (por exemplo, "O que as avaliações revelam sobre a nota: decomposição por aspecto do sentimento em avaliações do Airbnb"), se o programa permitir mudar.
- O resultado principal poderia subir para o 3º parágrafo da Introdução, logo depois da pergunta central.
- Conferir o item "todo número em tabela é discutido no texto". Não verifiquei tabela por tabela.

## O que não se aplica a este trabalho
Identificação causal (DiD, IV, RDD), propostas teóricas e provas, pré-registro formal (a regra do modelo principal faz esse papel) e tabelas de regressão com erros padrão por coeficiente.
