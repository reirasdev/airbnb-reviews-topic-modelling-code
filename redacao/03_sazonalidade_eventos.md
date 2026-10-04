# Sazonalidade e eventos (Etapa 16, opcional) — texto e tabelas para a dissertação

> **Status:** material preparado para inclusão na dissertação. Fonte: `run_20261004_203720` (abas `Sazon_Volume`, `Sazon_Conteudo`, `Sazon_Criterio`) e
> checagem exploratória do histórico (seção 22). Plano e critério foram congelados antes dos resultados (histórico, seção 19); correções de
> implementação e emenda posterior (remoção das Olimpíadas; inclusão do *Todo Mundo no Rio*) estão nas seções 20 e 21.

## 1. Texto sugerido (volume de avaliações)

O volume de avaliações em janelas de eventos foi de 1,24 a 1,73 vez o de dias comuns do mesmo mês (IC 95% excluindo 1). A medida é o volume de
**avaliações escritas** (um proxy de estadias que terminaram no período), e **não** a ocupação dos imóveis: os dados disponíveis não trazem o
calendário histórico de disponibilidade nem de preços. As avaliações foram atribuídas a cada evento por uma janela entre o dia seguinte ao início da estadia e
até 14 dias depois do seu fim (limite que a plataforma impõe para avaliar). **Ressalva:** os dados só incluem avaliações de anúncios que ainda estavam
ativos na coleta (março de 2025), de modo que os anos mais antigos estão sub-representados; os efeitos fixos de ano-mês absorvem o nível, mas não eliminam
essa limitação. **Evitar:** "ocupação 2 vezes maior".

## 2. Tabela: razão de taxas do volume de avaliações em janelas de evento

Razão entre o volume diário médio de avaliações na janela do evento e o de dias comuns do mesmo ano-mês, controlado por dia da semana (GLM de Poisson,
erro-padrão robusto HAC com 21 defasagens; anos de 2020 e 2021 excluídos). A janela principal usa 14 dias de defasagem; a de 7 dias é uma sensibilidade
(feriados de um dia usam 5 e 3 dias).

| Evento | Defasagem 14 dias [IC 95%] | Defasagem 7 dias [IC 95%] |
|---|---|---|
| Rock in Rio | **1,73** [1,16; 2,58] | 2,42 [2,12; 2,77] |
| Corpus Christi | **1,34** [1,15; 1,56] | 1,65 [1,45; 1,89] |
| Réveillon | **1,34** [1,22; 1,46] | 1,45 [1,32; 1,59] |
| Todo Mundo no Rio (2024) ¹ | **1,31** [1,01; 1,69] | 1,66 [1,37; 2,01] |
| Carnaval | **1,26** [1,09; 1,45] | 1,51 [1,36; 1,69] |
| Semana Santa | **1,25** [1,13; 1,37] | 1,27 [1,16; 1,39] |
| Feriados curtos (nacionais, do RJ e São Sebastião) | **1,24** [1,13; 1,36] | 1,26 [1,16; 1,37] |

¹ Megashow gratuito em Copacabana (Madonna, 4/mai/2024). Só essa edição cai dentro do período dos dados (as de 2025 e 2026 são posteriores à
coleta); o limite inferior do IC com 14 dias fica praticamente em 1, portanto a evidência é mais fraca. A defasagem de 7 dias dá valores maiores porque
considera só os dias logo após o check-out, onde o efeito se concentra; a de 14 dias inclui mais dias comuns e dilui o efeito. Eventos entram só se a janela
cai inteira no período analisado (isso exclui, por exemplo, o Carnaval de 2025, cortado pelo fim dos dados).

## 3. Tendência a sentimentos mais positivos nos eventos de música

Nas janelas de dois eventos de música e em Corpus Christi, a **proporção de frases negativas** no corpus inteiro é menor do que em dias comuns do mesmo
mês; nas demais janelas não há mudança geral. Resultado de uma checagem exploratória (pós-hoc), em avaliações de jan/2023 a fev/2025 (binomial diário,
mesmos efeitos fixos, HAC), razão de chances de a frase ser negativa:

| Evento | Defasagem 14 dias [IC 95%] | Leitura |
|---|---|---|
| Todo Mundo no Rio (2024) | **0,84** [0,78; 0,92] | menos frases negativas |
| Rock in Rio | **0,87** [0,83; 0,92] | menos frases negativas |
| Corpus Christi | **0,91** [0,86; 0,95] | menos frases negativas |
| Carnaval | 0,99 [0,89; 1,10] | sem mudança geral |
| Réveillon | 1,02 [0,92; 1,14] | sem mudança geral |
| Semana Santa | 1,05 [0,98; 1,13] | sem mudança geral |
| Feriados curtos | 1,00 [0,95; 1,05] | sem mudança geral |

**Interpretação (hipótese do pesquisador, não testada):** o público de festivais de música tende a ser mais jovem e possivelmente mais tolerante a ruído e
a acomodações simples. Os dados não têm idade do hóspede e não distinguem essa explicação de entusiasmo com o próprio evento. **Consequência para a leitura
dos aspectos:** nessas janelas as razões de chances por aspecto abaixo de 1 refletem em boa parte esse deslocamento geral; nas janelas sem deslocamento
(Carnaval e Réveillon), os aumentos específicos de queixa são mais informativos — no Carnaval, em precisão do anúncio (razão de chances 1,79; o tópico
"fotos conforme a descrição" chega a 2,57), custo-benefício (1,57) e localização (1,23); no Réveillon, em localização (1,20) e custo-benefício (1,60).

## 4. Limitações a declarar

Data da avaliação não é data da estadia; janelas de evento se sobrepõem em ~2% dos dias; feriados municipais e datas do Rock in Rio devem ser conferidos em
fonte oficial; só uma edição do *Todo Mundo no Rio* está nos dados; conteúdo do Carnaval vem de apenas duas edições (2023 e 2024); todas as medidas são
associações, não efeitos causais; o conteúdo por aspecto e por tópico foi testado com correção de Benjamini-Hochberg, mas é exploratório.
