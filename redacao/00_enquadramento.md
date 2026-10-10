# Enquadramento da pesquisa (v3 — 2026-10-09, após a avaliação do orientador)

> **Histórico do enquadramento.** v1 (até a tag `estrategia-v1-tese-final`): teste da hipótese de que um rating sintético por sentimento recupera informação que a nota oficial esconde. v2 (2026-10-04):
> mestrado profissional de mensuração e aplicação, sem hipótese a provar. **v3 (este documento)** incorpora três correções pedidas pelo orientador: (1) um segundo modelo de sentimento, treinado em
> avaliações; (2) o enquadramento passa a deixar claro que os desfechos "econômicos" disponíveis são **índices de volume recente de avaliações** e que a contribuição **não é o rating sintético**; (3) um
> único texto de resultados, com linha de raciocínio contínua (`01_resultados_unificado.md`).

## 1. Contexto

As avaliações de hóspedes no Airbnb são ricas em texto, mas a plataforma as resume em notas fortemente comprimidas no topo da escala (no Rio de Janeiro, 22,8% dos anúncios analisados têm nota exatamente
5,0). O texto diz **o que** agrada e desagrada, e isso interessa a anfitriões de temporada e a empresas que administram imóveis. Os dados (Inside Airbnb) trazem a nota e seis subnotas por anúncio, mas **não trazem
ocupação nem receita observadas**: os campos `estimated_occupancy_l365d` e `estimated_revenue_l365d` são funções exatas do número de avaliações em 12 meses, da estadia mínima e do preço (verificado em 100% dos
anúncios). O objeto central do estudo são, portanto, a nota, as subnotas e o texto; o volume de avaliações entra apenas como desfecho auxiliar.

## 2. Objetivo geral

Medir, por análise de sentimento por aspecto sobre avaliações de hóspedes do Airbnb no Rio de Janeiro, **o que o texto revela sobre a nota e as subnotas oficiais**, e transformar essa medição em diagnóstico prático para
anfitriões e empresas gestoras.

## 3. Objetivos específicos e perguntas de pesquisa (em ordem de importância)

1. **Medição.** Construir e validar a medição do sentimento por aspecto (dois modelos de sentimento, tópicos por BERTopic, mapa tópico → aspecto). *A medição é confiável? Para quais aspectos?* Evidência: frases rotuladas, concordância
   entre modelos, validade de construto contra as subnotas, checagem com um segundo método de tópicos (LDA).
2. **Associação com a nota.** Estimar quais aspectos e tópicos mais se associam à nota global e a cada subnota, e quais concentram as queixas. *O que o texto revela sobre a nota?* (Associação; sem linguagem causal.) **É a contribuição central.**
3. **Aplicação.** Entregar o resultado como diagnóstico por anúncio, comparado ao bairro e ao tipo de acomodação. *Como um anfitrião usa isso?*
4. **Índice único.** Verificar se um índice sintético (R_syn) acrescenta algo à nota oficial. *Um número único substitui a decomposição por aspecto?* Resultado secundário; um resultado nulo é legítimo e esperado.
5. **Sazonalidade (exploratório).** Como feriados e eventos se associam ao volume de avaliações e às queixas por aspecto?

## 4. Contribuições esperadas

- **Científica:** evidência sobre a validade de sentimento multilíngue por aspecto frente a notas oficiais comprimidas, comparando um modelo genérico (treinado em tweets) com um treinado em avaliações, e o que cada
  escolha implica.
- **Aplicada (mestrado profissional):** ranking de aspectos e tópicos associados à nota (e das queixas que mais pesam), e uma ferramenta de diagnóstico por anúncio com referência a anúncios semelhantes.

## 5. Título (provisório; a escolher pelo pesquisador)

- **Proposto:** *O que as avaliações revelam sobre a nota: decomposição por aspecto do sentimento em avaliações de hóspedes do Airbnb no Rio de Janeiro.*
- Opção 2: *Decompondo a nota do Airbnb: aspectos e tópicos nas avaliações de hóspedes no Rio de Janeiro.*
- Opção 3: *Além da nota: análise de sentimento por aspecto em avaliações do Airbnb e diagnóstico para anfitriões no Rio de Janeiro.*

## 6. Estrutura da dissertação (alinhada ao texto unificado de resultados)

1. Introdução e perguntas de pesquisa · 2. Dados e o que eles permitem medir · 3. Método: como o texto é medido · 4. A medição é confiável? · 5. O que o texto revela sobre a nota · 6. Aplicação: diagnóstico por anúncio ·
7. Um índice único acrescenta algo? · 8. Sazonalidade e eventos (exploratório) · 9. Limitações · 10. Conclusões.

## 7. Limitações a declarar (resumo)

Sentimento calculado sobre as 30 avaliações mais recentes por anúncio; anúncios com pouco texto ficam fora de R_syn (só ~55% dos de nota 5,0 entram); mapeamento tópico → aspecto e validação manual feitos por um pesquisador
(segundo anotador pendente); desfechos `estimated_*` construídos algebricamente; análise de sazonalidade restrita (data da avaliação ≠ data da estadia; só anúncios ativos na coleta); todas as associações são
descritivas, sem inferência causal.
