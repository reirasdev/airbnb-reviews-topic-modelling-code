"""Calendário de eventos do estudo de sazonalidade (Etapa 16, OPCIONAL), definido ANTES de olhar os resultados.

LAG principal = 14 dias (limite da plataforma) para eventos longos e 5 dias para feriados de um dia (sensibilidade: 7 e 3).
Cada evento é uma janela de ESTADIA [estadia_ini, estadia_fim]. Como a plataforma só permite avaliar após o check-out e até
14 dias depois, as avaliações atribuídas ao evento são as datadas em [estadia_ini + 1, estadia_fim + LAG].

Fontes:
  * Feriados nacionais e do estado do RJ: biblioteca `holidays` (BR, subdivisão RJ), versão registrada no log.
  * Carnaval, Semana Santa e Corpus Christi: calculados a partir da data da Páscoa (dateutil.easter).
  * São Sebastião (20/jan): feriado municipal do Rio, incluído manualmente [conferir em lei municipal].
  * Rock in Rio: datas das edições de 2017, 2019, 2022 e 2024 (Wikipédia; [conferir no site oficial]).
  * Todo Mundo no Rio (megashow gratuito em Copacabana, uma noite): 04/mai/2024 (Madonna), 03/mai/2025 (Lady Gaga), 02/mai/2026
    (Shakira) [datas informadas pelo pesquisador]. Só a edição de 2024 cai dentro do período dos dados (até 20/mar/2025).
Eventos NÃO incluídos de propósito: Natal e Confraternização (contidos na janela do Réveillon); Copa 2014 (antes do período com volume
suficiente); Olimpíadas 2016 (evento único, não recorrente; removido após a primeira execução); feriados em que o dia coincide com outros eventos já listados.
"""
from __future__ import annotations

from datetime import date, timedelta

import holidays
import pandas as pd
from dateutil.easter import easter

YEARS = range(2016, 2026)
ROCK_IN_RIO = {2017: ((9, 15), (9, 24)), 2019: ((9, 27), (10, 6)), 2022: ((9, 2), (9, 11)), 2024: ((9, 13), (9, 22))}
TODO_MUNDO_NO_RIO = {2024: date(2024, 5, 4), 2025: date(2025, 5, 3), 2026: date(2026, 5, 2)}  # megashow de uma noite (sábado)
# feriados da biblioteca que NÃO entram em "feriado_curto" (já cobertos por outros eventos)
EXCLUIR_BIBLIOTECA = {"Confraternização Universal", "Carnaval", "Sexta-feira Santa", "Natal"}


def eventos() -> pd.DataFrame:
    rows = []
    for y in YEARS:
        e = easter(y)
        terca = e - timedelta(days=47)  # terça-feira de Carnaval
        rows.append(("carnaval", y, terca - timedelta(days=4), terca + timedelta(days=1), "sexta antes até quarta-feira de cinzas"))
        rows.append(("semana_santa", y, e - timedelta(days=3), e, "quinta-feira santa até o domingo de Páscoa"))
        rows.append(("corpus_christi", y, e + timedelta(days=60), e + timedelta(days=63), "quinta-feira (feriado facultativo) até domingo"))
        rows.append(("reveillon", y, date(y, 12, 28), date(y + 1, 1, 2), "28/dez a 02/jan (ano = o do mês de dezembro)"))
        if y in ROCK_IN_RIO:
            (m1, d1), (m2, d2) = ROCK_IN_RIO[y]
            rows.append(("rock_in_rio", y, date(y, m1, d1), date(y, m2, d2), "datas do festival"))
        h = holidays.country_holidays("BR", subdiv="RJ", years=[y], language="pt_BR")
        for d, nome in sorted(h.items()):
            if nome not in EXCLUIR_BIBLIOTECA:
                rows.append(("feriado_curto", y, d - timedelta(days=1), d + timedelta(days=1), nome))
        rows.append(("feriado_curto", y, date(y, 1, 20) - timedelta(days=1), date(y, 1, 20) + timedelta(days=1), "São Sebastião (municipal)"))
    for y, d in TODO_MUNDO_NO_RIO.items():  # estadia: quinta (d-2) a domingo (d+1) do fim de semana do show
        rows.append(("todo_mundo_no_rio", y, d - timedelta(days=2), d + timedelta(days=1), "megashow gratuito em Copacabana"))
    E = pd.DataFrame(rows, columns=["evento", "ano", "estadia_ini", "estadia_fim", "descricao"])
    E["estadia_ini"], E["estadia_fim"] = pd.to_datetime(E["estadia_ini"]), pd.to_datetime(E["estadia_fim"])
    return E.sort_values(["estadia_ini"]).reset_index(drop=True)


def janelas_avaliacao(E: pd.DataFrame, lag: int) -> pd.DataFrame:
    """Janela de DATAS DE AVALIAÇÃO atribuída a cada evento: [estadia_ini + 1, estadia_fim + lag]."""
    W = E.copy()
    # feriados de um dia: estadias curtas, avaliações concentradas logo após o check-out; lag longo cobriria ~30% do calendário
    lag_ev = W["evento"].map(lambda e: (5 if lag >= 14 else 3) if e == "feriado_curto" else lag)
    W["aval_ini"] = W["estadia_ini"] + pd.Timedelta(days=1)
    W["aval_fim"] = W["estadia_fim"] + pd.to_timedelta(lag_ev, unit="D")
    return W


def marcar_dias(dias: pd.DatetimeIndex, E: pd.DataFrame, lag: int) -> pd.DataFrame:
    """Matriz dia × evento (0/1, evento = grupo; um dia pode pertencer a mais de um)."""
    W = janelas_avaliacao(E, lag)
    M = pd.DataFrame(0, index=dias, columns=sorted(W["evento"].unique()))
    for r in W.itertuples():
        M.loc[(M.index >= r.aval_ini) & (M.index <= r.aval_fim), r.evento] = 1
    return M
