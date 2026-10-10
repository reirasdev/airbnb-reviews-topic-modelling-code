"""Etapa 16 (OPCIONAL) — sazonalidade e feriados. Plano e critério congelados em historico/HISTORICO_DECISOES.md, seção 19.

(V) Volume: GLM de Poisson (EP robusto HAC, 21 defasagens) sobre a contagem diária de TODAS as avaliações, com efeitos fixos de ano-mês e dia da semana.
(C) Conteúdo (2023-01 a 2025-02): GLM binomial diário por aspecto e por tópico de queixa. IRR/OR de cada grupo de evento vs. dias fora
    de evento, no mesmo ano-mês. Associações; a data da avaliação não é a data da estadia (atribuição por janela de até 14 dias).
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm

from config import GENERAL_BUCKET
from .calendario import eventos, marcar_dias
from .sentimento import load_sentiment
from .utils import Store, stage

log = logging.getLogger("pipeline")
LONG = ["carnaval", "reveillon", "semana_santa", "rock_in_rio", "corpus_christi", "todo_mundo_no_rio"]
LAGS = (14, 7)  # principal e sensibilidade
FIM = pd.Timestamp("2025-02-28")  # último mês COMPLETO (os dados terminam em 20/mar/2025: o mês truncado não tem linha de base)
HAC_LAGS = 21  # autocorrelação dos contadores diários


def completos(E: pd.DataFrame, days: pd.DatetimeIndex, lag: int) -> pd.DataFrame:
    """Mantém só eventos cuja janela de avaliações cai INTEIRA nos dias analisados (descarta, p.ex., o Carnaval de 2025, cortado
    pelo fim dos dados, e o Réveillon de 2019, cuja janela entra em 2020, ano excluído por causa da pandemia)."""
    from .calendario import janelas_avaliacao
    W = janelas_avaliacao(E, lag)
    ok = [set(pd.date_range(r.aval_ini, r.aval_fim)) <= set(days) for r in W.itertuples()]
    return E[np.array(ok)]


def _bh(p: pd.Series) -> pd.Series:
    p = p.fillna(1.0).to_numpy()
    o = np.argsort(p)
    q = np.empty_like(p)
    q[o] = np.minimum.accumulate((p[o] * len(p) / (np.arange(len(p)) + 1))[::-1])[::-1]
    return pd.Series(np.minimum(q, 1), dtype=float)


def _design(days: pd.DatetimeIndex, M: pd.DataFrame) -> pd.DataFrame:
    D = M.copy()
    D["ym"] = days.strftime("%Y-%m")
    D["dow"] = days.dayofweek.astype(str)
    return D


def _fit(endog, D: pd.DataFrame, ev_cols: list[str], family):
    X = patsy.dmatrix("C(ym) + C(dow) + " + " + ".join(ev_cols), D, return_type="dataframe")
    f = sm.GLM(endog, X, family=family).fit(cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS})
    ci = f.conf_int()
    out = pd.DataFrame({"evento": ev_cols, "razao": np.exp(f.params[ev_cols].to_numpy()), "ic_inf": np.exp(ci.loc[ev_cols, 0].to_numpy()),
                        "ic_sup": np.exp(ci.loc[ev_cols, 1].to_numpy()), "p": f.pvalues[ev_cols].to_numpy()})
    return out


# ---------------------------------------------------------------- (V) volume
def volume(cfg, E: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    R = pd.read_csv(cfg.REVIEWS_CSV, usecols=["date"])
    d = pd.to_datetime(R["date"]).dt.normalize()
    days = pd.date_range("2016-01-01", min(d.max(), FIM))
    n = d.value_counts().reindex(days, fill_value=0)
    keep = ~((days.year == 2020) | (days.year == 2021))  # pandemia: nível e sazonalidade atípicos
    days, n = days[keep], n[keep]
    rows, rows_y = [], []
    for lag in LAGS:
        El = completos(E, days, lag)
        M = marcar_dias(days, El, lag)
        M = M.loc[:, M.sum() > 0]
        D = _design(days, M)
        D["y"] = n.to_numpy()
        out = _fit(D["y"].to_numpy(), D, [c for c in M.columns], sm.families.Poisson())
        rows.append(out.assign(defasagem=lag))
        # por ano de evento (eventos longos)
        My = pd.DataFrame(index=days)
        W = El[El["evento"].isin(LONG)]
        from .calendario import janelas_avaliacao
        Wl = janelas_avaliacao(W, lag)
        cols = []
        for r in Wl.itertuples():
            c = f"{r.evento}_{r.ano}"
            if r.ano in (2020, 2021) or r.ano < 2016:
                continue
            My[c] = ((days >= r.aval_ini) & (days <= r.aval_fim)).astype(int)
            cols.append(c)
        for c in ("feriado_curto",):
            if c in M.columns:
                My[c] = M[c].to_numpy()
                cols.append(c)
        Dy = _design(days, My)
        Dy["y"] = n.to_numpy()
        keepc = [c for c in cols if Dy[c].sum() > 0]
        rows_y.append(_fit(Dy["y"].to_numpy(), Dy, keepc, sm.families.Poisson()).assign(defasagem=lag))
    return pd.concat(rows), pd.concat(rows_y)


# ---------------------------------------------------------------- (C) conteúdo
def conteudo(cfg, store: Store, E: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    A = store.load("sentencas_aspecto")
    A["date"] = pd.to_datetime(A["date"]).dt.normalize()
    A = A.merge(load_sentiment(store)[["text_id", "cls"]], on="text_id")
    A["neg"] = (A["cls"] == 0)
    days = pd.date_range("2023-01-01", min(A["date"].max(), FIM))
    A = A[A["date"] >= days[0]]
    tot = A.groupby("date").size().reindex(days, fill_value=0)
    asp = [a for a in cfg.ASPECT_SEEDS]
    cnt = A[A["aspecto"] != GENERAL_BUCKET].groupby(["date", "aspecto"]).agg(n=("neg", "size"), neg=("neg", "sum")).reset_index()
    n_a = cnt.pivot(index="date", columns="aspecto", values="n").reindex(days).fillna(0)
    g_a = cnt.pivot(index="date", columns="aspecto", values="neg").reindex(days).fillna(0)
    # tópicos de queixa (da etapa 15): top 30 por prevalência × impacto, apenas tópicos diretos
    Q = store.load("imp_topicos_queixas").head(30)
    Ad = A[A["topic_direto"] & A["topic"].isin(Q["topic"])]
    tn = Ad[Ad["neg"]].groupby(["date", "topic"]).size().unstack(fill_value=0).reindex(days, fill_value=0)
    tot_d = A[A["topic_direto"]].groupby("date").size().reindex(days, fill_value=0)
    ev_cols = ["carnaval", "reveillon", "semana_santa", "rock_in_rio", "corpus_christi", "todo_mundo_no_rio", "feriado_curto"]
    fam = sm.families.Binomial()
    rows_a, rows_t = [], []
    for lag in LAGS:
        M = marcar_dias(days, completos(E, days, lag), lag)
        M = M[[c for c in ev_cols if c in M.columns]]
        M = M.loc[:, M.sum() > 0]
        D = _design(days, M)
        ec = list(M.columns)
        for a in asp:
            if a == GENERAL_BUCKET:
                continue
            for medida, succ, base in (("participação do aspecto nas sentenças", n_a[a], tot), ("proporção negativa dentro do aspecto", g_a[a], n_a[a])):
                m = base.to_numpy() > 0
                if m.sum() < 100:
                    continue
                endog = np.column_stack([succ.to_numpy()[m], (base - succ).to_numpy()[m]])
                o = _fit(endog, D[m].reset_index(drop=True), ec, fam)
                rows_a.append(o.assign(defasagem=lag, aspecto=a, medida=medida))
        for t in tn.columns:
            m = tot_d.to_numpy() > 0
            endog = np.column_stack([tn[t].to_numpy()[m], (tot_d - tn[t]).to_numpy()[m]])
            o = _fit(endog, D[m].reset_index(drop=True), ec, fam)
            rows_t.append(o.assign(defasagem=lag, topic=int(t)))
    rows_g = []  # proporção GERAL de frases negativas (corpus inteiro) por evento: deslocamento geral de positividade
    for lag in LAGS:
        M = marcar_dias(days, completos(E, days, lag), lag)
        M = M[[c for c in ev_cols if c in M.columns]]
        M = M.loc[:, M.sum() > 0]
        D = _design(days, M)
        m = tot.to_numpy() > 0
        neg_all = A[A["neg"]].groupby("date").size().reindex(days, fill_value=0)
        endog = np.column_stack([neg_all.to_numpy()[m], (tot - neg_all).to_numpy()[m]])
        rows_g.append(_fit(endog, D[m].reset_index(drop=True), list(M.columns), fam).assign(defasagem=lag))
    G = pd.concat(rows_g)
    G["q_BH"] = np.nan
    for _, idx in G.groupby("defasagem").groups.items():
        G.loc[idx, "q_BH"] = _bh(G.loc[idx, "p"]).to_numpy()
    store.save("sazon_negativa_geral", G)
    Ra, Rt = pd.concat(rows_a), pd.concat(rows_t)
    for R, keys in ((Ra, ["defasagem", "medida"]), (Rt, ["defasagem"])):
        R["q_BH"] = np.nan
        for _, idx in R.groupby(keys).groups.items():
            R.loc[idx, "q_BH"] = _bh(R.loc[idx, "p"]).to_numpy()
    Rt = Rt.merge(Q[["topic", "aspecto", "top_words", "prevalencia"]], on="topic", how="left")
    return Ra, Rt


def criterio(V: pd.DataFrame, Ra: pd.DataFrame, Rt: pd.DataFrame) -> pd.DataFrame:
    """Aplica o critério congelado de 'resultado interessante' (histórico, seção 19)."""
    rows = []
    for ev in sorted(V["evento"].unique()):
        v = V[V["evento"] == ev].set_index("defasagem")
        a = all(((v.loc[l, "ic_inf"] > 1) | (v.loc[l, "ic_sup"] < 1)) and abs(v.loc[l, "razao"] - 1) >= 0.10 for l in LAGS if l in v.index)
        cnt = {}
        for l in LAGS:
            x = Ra[(Ra.defasagem == l) & (Ra.evento == ev) & (Ra.medida == "proporção negativa dentro do aspecto") & (Ra.q_BH < 0.05) & (Ra.razao >= 1.15)]
            y = Rt[(Rt.defasagem == l) & (Rt.evento == ev) & (Rt.q_BH < 0.05) & (Rt.razao >= 1.15)]
            cnt[l] = len(x) + len(y)
        rows.append({"evento": ev, "criterio_a_volume": a, "queixas_q<0,05_OR>=1,15 (def.14)": cnt[14], "queixas_q<0,05_OR>=1,15 (def.7)": cnt[7],
                     "criterio_b_conteudo": min(cnt.values()) >= 3,
                     "interessante": bool(a or min(cnt.values()) >= 3)})
    return pd.DataFrame(rows)


def run(cfg, store: Store) -> None:
    with stage("Etapa 16 (opcional) — Sazonalidade e feriados"):
        import holidays
        log.info("holidays %s | eventos: %s", holidays.__version__, "pt-BR")
        E = eventos()
        store.save("sazon_calendario", E.astype({"estadia_ini": "datetime64[ns]", "estadia_fim": "datetime64[ns]"}))
        V, Vy = volume(cfg, E)
        store.save("sazon_volume", V)
        store.save("sazon_volume_por_ano", Vy)
        log.info("(V) Volume de avaliações — razão de taxas (IRR) por evento:\n%s",
                 V.pivot_table(index="evento", columns="defasagem", values=["razao", "ic_inf", "ic_sup", "p"]).round(3).to_string())
        Ra, Rt = conteudo(cfg, store, E)
        store.save("sazon_aspecto", Ra)
        store.save("sazon_topico", Rt)
        C = criterio(V, Ra, Rt)
        store.save("sazon_criterio", C)
        log.info("(C) Aspectos, queixas (OR de proporção negativa), defasagem 14, q < 0,10:\n%s",
                 Ra[(Ra.defasagem == 14) & (Ra.medida == "proporção negativa dentro do aspecto") & (Ra.q_BH < 0.10)].sort_values("q_BH")
                 .round(3).to_string(index=False))
        log.info("(C) Tópicos, queixas, defasagem 14, q < 0,05 (top 20 por OR):\n%s",
                 Rt[(Rt.defasagem == 14) & (Rt.q_BH < 0.05)].sort_values("razao", ascending=False).head(20)
                 [["evento", "topic", "aspecto", "top_words", "razao", "ic_inf", "ic_sup", "q_BH"]].round(3).to_string(index=False))
        log.info("Critério congelado de 'resultado interessante':\n%s", C.to_string(index=False))
        store.metric("etapa16", eventos_interessantes=list(C.loc[C["interessante"], "evento"]))
