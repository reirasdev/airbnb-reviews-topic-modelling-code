# Investigação do coeficiente negativo de R_syn no teto — **RESOLVIDA**

> **Status (revisado em 2026-10-04):** a investigação inicial (51 especificações, `run_20261004_135242`) não achou a causa.
> Uma verificação posterior (`run_20261004_143317`, módulo `src/s13_sem_ltm.py`) a **encontrou: o coeficiente negativo é um
> artefato de especificação**, provocado pela forma como o desfecho é construído. Ele não deve ser interpretado como efeito
> sobre a demanda e **não deve ser reportado como achado**; reporte-se, no máximo, a explicação abaixo.

## 1. O achado original

Na Análise A (R_syn sem shrinkage, controles com avaliações dos últimos 12 meses), o coeficiente padronizado de R_syn sobre a
ocupação estimada foi negativo e significativo nos tetos: −1,03 noite por desvio-padrão em R_off ≥ 4,9 (n = 9.747; p = 0,003)
e −1,34 em R_off = 5,0 (n = 4.711; p = 0,0001); ≈ 0 na amostra completa (+0,18; p = 0,44). Sem ganho de R² fora da amostra.

## 2. A causa: a ocupação estimada é uma função exata de duas variáveis

A documentação da Inside Airbnb (página *Data Assumptions*, consultada em 2026-10-04) descreve a ocupação estimada como:
reservas = avaliações ÷ taxa de avaliação (50%); noites = reservas × duração média de estadia (3 noites, ou o mínimo de noites
se maior); ocupação limitada a 70% (255 noites/ano); receita = ocupação × preço. **Verifiquei essa estrutura nos dados do
estudo (aba `Formula_Ocupacao`):**

| Fórmula testada | Anúncios | Reprodução exata |
|---|---:|---:|
| `ocupação = min(255, avaliações_12m × 2 × max(3, minimum_nights))` | 42.013 | **100,0%** (R² = 1) |
| mesma, com `minimum_nights_avg_ntm` no lugar de `minimum_nights` | 42.013 | 95,0% |
| mesma, com duração fixa de 3 noites | 42.013 | 89,7% |
| `receita = preço × ocupação` | 38.356 | **100,0%** |
| `avaliações_12m = 0 ⇒ ocupação = 0` | 12.979 | 100,0% |

(Nota: a página diz "avaliações × 0,50", mas os dados exigem multiplicar por 2, isto é, dividir pela taxa de avaliação.)

**Consequência.** A ocupação e a receita estimadas **não medem demanda real**: são transformações determinísticas do número de
avaliações dos últimos 12 meses, de `minimum_nights` e (receita) do preço.

## 3. Por que o coeficiente apareceu

Os controles da Análise A incluíam `log(avaliações_12m)` linearmente. Como o desfecho é `min(255, 2 × ltm × max(3, minimum_nights))`
(multiplicativo, com piso e teto), um controle linear em log não o captura, e a parte não modelada (não linear) pode se
correlacionar com R_syn. Teste direto, em R_off = 5,0 (n = 4.711) e ≥ 4,9 (n = 9.747):

| Controles | Coef. de R_syn (R_off ≥ 4,9) | Coef. de R_syn (R_off = 5,0) | R² dentro da amostra |
|---|---:|---:|---:|
| Os da Análise A (`log_ltm` linear) | −1,03 (p = 0,003) | −1,34 (p = 0,0001) | 0,81 / 0,75 |
| + forma flexível (ltm, ltm², produto ltm×estadia, quadrado, indicador de teto) | −0,42 (p = 0,15) | −0,09 (p = 0,62) | 0,95 / 0,94 |
| + a fórmula exata `min(255, 2·ltm·estadia)` | 0,00 | 0,00 | 1,00 / 1,00 |

Com uma forma funcional flexível, o coeficiente se aproxima de zero e perde significância; com a fórmula exata, o desfecho é
reproduzido sem resíduo e não resta nada para R_syn explicar. O sinal negativo era resíduo de má especificação.

As 51 especificações da primeira investigação (`minimum_nights`, características, texto, zeros, aspectos) eram consistentes
com isso: nenhuma incluía a forma exata, e o sinal variava com o conjunto de controles (efeito supressor típico).

## 4. Implicações mais amplas (ver `01_resultados.md`, seções 7 e 7.2)

1. **Controlar por `number_of_reviews_ltm` é "controlar o desfecho"**; foi uma escolha de controle minha (a especificação
   original pedia só o volume total de avaliações). Os resultados "R² = 0,80 só com controles" vinham desse controle.
2. Sem esse controle (**especificação principal desde 2026-10-04**), o teste passa a ter poder: a nota oficial acrescenta R²
   detectável (+0,008 na ocupação), e R_syn não acrescenta nada além dela (seção 7).
3. Para a dissertação, as variáveis `estimated_occupancy_l365d` e `estimated_revenue_l365d` devem ser descritas como
   **índices derivados do volume recente de avaliações**, e não como medidas de ocupação ou receita observadas; a leitura
   adequada é "popularidade/volume recente de avaliações", com a ressalva de que depende também de `minimum_nights` e preço.
4. A relação com a descrição da ocupação estimada vem de fonte oficial (Inside Airbnb) **e** foi verificada nos dados; o
   dicionário de dados do repositório (`listings-dictionary.csv`) não define os campos `estimated_*`.
