# Enquadramento da pesquisa (v2 — a partir de 2026-10-04)

> **Mudança de estratégia.** Até o commit `e9e2895` (tag `estrategia-v1-tese-final`) o trabalho foi conduzido como o teste de uma
> hipótese: *o rating sintético por sentimento recupera informação que a nota oficial esconde, sobretudo no teto da escala*.
> A partir deste ponto o enquadramento passa a ser o de um **mestrado profissional**, de mensuração e aplicação, sem hipótese
> a ser "provada". Os resultados da v1 continuam válidos e são reaproveitados (seção 4).

## 1. Contexto e objetivo

Avaliações de hóspedes no Airbnb são ricas em texto, mas a plataforma resume a experiência em notas fortemente comprimidas
no topo da escala (no Rio de Janeiro, 22,8% dos anúncios analisados têm nota exatamente 5,0). O texto pode dizer **o que**
agrada e desagrada, e isso interessa a anfitriões de temporada e a empresas que administram imóveis. O trabalho constrói um
pipeline reprodutível de análise de sentimento por aspecto sobre ~1,5 milhão de sentenças em vários idiomas, e o confronta
com as notas e subnotas oficiais.

## 2. Perguntas de pesquisa

1. **Adequação (validade de construto).** O sentimento por aspecto extraído do texto é adequado às notas e subnotas
   oficiais? Em que medida e para quais aspectos concorda, e onde diverge?
2. **Importância.** Quais aspectos e tópicos mais se associam à nota que o imóvel recebe, e quais concentram as queixas?
   (Associação; sem linguagem causal.)
3. **Aplicação.** Como transformar isso em diagnóstico prático para um anfitrião ou empresa gestora (comparação com o bairro
   e o tipo de imóvel, tópicos prioritários)?
4. **Sazonalidade.** Como feriados e eventos se associam ao volume de avaliações e às queixas por aspecto?
5. **Complementar.** O rating sintético (R_syn) acrescenta poder explicativo sobre o volume recente de avaliações além da
   nota oficial? (Resultado já obtido na v1: não acrescenta; consistente com a Pergunta 1, pois o texto e a nota carregam
   informação semelhante.)

## 3. Contribuições esperadas

- **Científica:** evidência sobre a validade de sentimento multilíngue por aspecto frente às notas oficiais, com limites
  (atenuação por notas comprimidas, volume de avaliações, idioma).
- **Aplicada (mestrado profissional):** ranking de aspectos e tópicos de maior associação com a nota, calendário de eventos e
  queixas, e uma ferramenta de diagnóstico por anúncio com referência ao bairro e tipo.

## 4. O que se mantém da v1 e o que muda

| Elemento | Situação |
|---|---|
| Pipeline de dados, sentimento, tópicos, mapeamento de aspectos, perfil ABSA (Etapas 1 a 7) | **Mantido** |
| Análises A e B (poder explicativo/monotonicidade) e sensibilidades | **Mantidas como complementares** (Pergunta 5) |
| Teste do teto | Vira análise descritiva complementar |
| Shrinkage e quantile mapping | Secundários (R_syn principal é sem shrinkage; calibração só para exibição) |
| Desfechos `estimated_*` | Descritos como índices de volume recente de avaliações (fórmula verificada), não como ocupação/receita |
| Linguagem | De "tese não sustentada" para "o sentimento é adequado às notas; R_syn não acrescenta além delas" |
| **Novo** | Validação ampliada de construto (s14), importância de aspectos/tópicos (s15), sazonalidade (s16), diagnóstico por anúncio |

## 5. Estrutura prevista da dissertação

1. Introdução e perguntas de pesquisa · 2. Dados e método (pipeline, modelos, mapeamento de aspectos) · 3. Adequação do sentimento
às notas · 4. Importância de aspectos e tópicos · 5. Sazonalidade e eventos · 6. Diagnóstico para anfitriões e gestoras
(ferramenta e exemplos anonimizados) · 7. Resultado complementar: R_syn e volume de avaliações · 8. Limitações · 9. Conclusões
e recomendações práticas.

## 6. Limitações a declarar (resumo)

Sentimento calculado sobre as 30 avaliações mais recentes por anúncio; anúncios com pouco texto ficam fora de R_syn (55% dos de
nota 5,0 entram); modelo de sentimento treinado em tweets; mapeamento tópico → aspecto feito por um pesquisador; desfechos
`estimated_*` construídos algebricamente; análise temporal restrita a 2023-2025 para conteúdo (volume de avaliações cobre
2016-2025); data da avaliação ≠ data da estadia (janela de até 14 dias após o check-out); todas as associações são
descritivas, sem inferência causal.
