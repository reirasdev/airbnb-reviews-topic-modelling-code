# Investigação do coeficiente negativo de R_syn no teto

> **Status:** análise **exploratória** (51 especificações; sem correção para comparações múltiplas), executada em
> `run_20261004_135242` (módulo `src/s12_investigacao_coef.py`, aba `Investigacao_Coef` do Excel).
> **Conclusão curta: a hipótese não foi identificada.** O efeito é pequeno, sensível à especificação e sem poder preditivo
> fora da amostra; não deve ser interpretado como efeito de demanda.

## 1. O achado

Na Análise A (especificação principal, sem shrinkage), o coeficiente de R_syn (padronizado) sobre a ocupação estimada,
estimado dentro da amostra com controles e erro-padrão robusto HC3, é **negativo e significativo nos tetos**:
−1,03 noite por desvio-padrão de R_syn em R_off ≥ 4,9 (n = 9.747; p = 0,003) e −1,34 em R_off = 5,0 (n = 4.711; p = 0,0001). Na
amostra completa o coeficiente é ≈ 0 (+0,18; p = 0,44). Fora da amostra não há ganho de R² (ΔR² entre −0,0001 e +0,0006,
intervalos incluem zero). O sinal é oposto ao da tese, o que justifica investigar se há uma explicação sistemática.

Dimensão do efeito: a ocupação média é ~87 noites; o RMSE out-of-sample dos controles no grupo de nota 5,0 é ~27 noites.
Um coeficiente de −1,3 equivale a **~5% do desvio-padrão residual**.

## 2. Hipóteses testadas

| Hip. | Ideia | Como foi testada |
|---|---|---|
| H1 | A ocupação estimada depende de `minimum_nights` (duração de estadia) **[conferir na documentação da Inside Airbnb]** | acrescentar log de `minimum_nights` e `minimum_nights_avg_ntm` |
| H2 | Características do anúncio | acrescentar capacidade, disponibilidade (365), reserva instantânea, nº de anúncios do anfitrião |
| H3 | Quantidade de texto (anúncios com mais aspectos cobertos têm sentimento médio menor) | acrescentar nº de aspectos e log do nº de sentenças |
| H4 | Zeros por construção (sem avaliação recente → ocupação 0) | restringir a ocupação > 0 |
| H5 | Um único aspecto guia o efeito | R_syn sem cada aspecto (leave-one-out) |

## 3. Resultados (coeficiente de R_syn em noites por desvio-padrão; EP HC3)

| Especificação | Amostra completa (n = 20.882) | R_off ≥ 4,9 (n = 9.747) | R_off = 5,0 (n = 4.711) |
|---|---:|---:|---:|
| S0 controles da Análise A | +0,18 (p = 0,44) | −1,03 (p = 0,003) | −1,34 (p = 0,0001) |
| S1 + `minimum_nights` (H1) | −0,75 (p = 0,0007) | −0,76 (p = 0,022) | −1,13 (p = 0,0005) |
| S2 + características (H2) | −0,09 (p = 0,72) | −0,95 (p = 0,007) | −1,36 (p = 0,0001) |
| S3 = S1 + S2 | −0,62 (p = 0,007) | −0,63 (p = 0,058) | −1,13 (p = 0,0006) |
| S4 = S3 + quantidade de texto (H3) | −1,09 (p < 0,0001) | −1,35 (p = 0,0001) | −1,34 (p = 0,0001) |
| S5 = S3 sem `log_ltm` | +5,50 (p < 0,0001) | +1,32 (p = 0,009) | +0,50 (p = 0,28) |
| S6 = S3 só com ocupação > 0 (H4) | −1,00 (p < 0,0001) | −0,62 (p = 0,041) | −1,11 (p = 0,0005) |
| S7 sem um aspecto (H5), faixa | de +0,02 a +0,27 | de −0,64 a −1,22 | de −0,94 a −1,57 |

(S7: faixa entre as exclusões de cada um dos 10 aspectos; na exclusão de `seguranca` em R_off = 5,0 o erro-padrão não foi
estimável por singularidade numérica e esse caso deve ser ignorado.)

Correlações de postos no grupo de nota 5,0 (n = 4.711):

| Variável | ρ com R_syn | ρ com ocupação |
|---|---:|---:|
| avaliações nos últimos 12 meses (log) | −0,001 | **0,970** |
| total de avaliações (log) | −0,035 | 0,667 |
| nº de aspectos cobertos | −0,202 | 0,525 |
| nº de sentenças (log) | −0,106 | 0,594 |
| preço (log) | +0,038 | −0,121 |
| `minimum_nights` (log) | −0,046 | −0,048 |

## 4. Interpretação

1. **O desfecho é quase função de uma só variável.** A ocupação estimada tem ρ = 0,97 com as avaliações dos últimos 12
   meses. Sobra pouca variância para qualquer rating explicar, e é nessa sobra que o coeficiente é estimado.
2. **O sinal depende da especificação.** Na amostra completa, o coeficiente é ≈ 0 (S0), vira negativo ao acrescentar
   `minimum_nights` (S1, S3: −0,6 a −0,8), e vira fortemente **positivo** (+5,5) ao retirar o volume recente (S5), porque o
   sentimento se correlaciona com o volume. Isso é típico de efeito supressor em desfecho construído, não de uma relação
   estável com a demanda.
3. **No teto, nenhuma hipótese testada elimina o sinal.** `minimum_nights` explica parte em R_off ≥ 4,9 (de −1,03 para −0,63;
   p = 0,058 em S3), mas em R_off = 5,0 o coeficiente permanece entre −1,1 e −1,4 em S1–S4 e S6; nenhum aspecto isolado o
   gera (H5: −0,9 a −1,6); não é artefato de zeros (S6). Só desaparece em S5 (sem o controle de volume recente), o que
   mostra que o coeficiente é condicional ao volume.
4. **Quantidade de texto não explica.** R_syn tem ρ = −0,20 com o número de aspectos cobertos (anúncios com mais texto
   tendem a ter sentimento médio menor, plausivelmente porque críticas ficam mais visíveis), e esse número correlaciona 0,53
   com a ocupação; ainda assim, controlá-lo (S4) não altera o coeficiente em R_off = 5,0.

## 5. Conclusão e uso na dissertação

- O coeficiente negativo no teto é **estatisticamente significativo dentro da amostra, pequeno (~5% do DP residual), instável
  entre especificações e sem ganho preditivo fora da amostra**. A causa não foi identificada pelas hipóteses testadas.
- **Recomendação de redação:** reportá-lo como achado exploratório sem interpretação de demanda, junto com a ressalva de que o
  desfecho é construído a partir do volume de avaliações, e de que o teste não foi pré-especificado nem corrigido para
  múltiplas comparações.
- **Se a banca pedir mais:** (a) um desfecho menos mecânico (por exemplo, avaliações ou notas posteriores ao período, ou
  prêmio de preço), que exige outro recorte de dados e está fora do núcleo mínimo; (b) conferir na documentação oficial como a
  ocupação estimada é construída, para sustentar H1 com referência.
