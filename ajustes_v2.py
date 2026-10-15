"""Ajustes do orientador (14/10/2026), Fase 1: análises novas sobre dados já existentes (abas com sufixo _v2).

Uso (venv em C:\\vairbnb), a partir da raiz do repositório:
    python ajustes_v2.py                 # calcula tudo e grava os parquet em outputs/ajustes_v2/ e a planilha *_v2.xlsx

Nada do pipeline é refeito: lê o cache (outputs/cache/<hash>/tables), as frases rotuladas (data/) e a planilha final.
Mesmas sementes, dobras e regras do pipeline (modelo A principal, B acompanha).
  M2  Classificacao_IC_v2        Wilson 95% da precisão de atribuição por aspecto + precisão com os dois anotadores (100 frases)
  R2  Queixas_min2_v2 (+resumo)  queixas por tópico exigindo >= 2 sentenças negativas (mesma especificação, mesma correção BH)
  R3  Mapa_comodidades_v2, LMG_comodidades_v2   comodidades dividido em subaspectos; LMG da nota global
  R4  LMG_ausencia_v2            LMG com indicador de ausência para cada aspecto imputado
  F3  Tabela12_completa_v2       12 linhas (3 desfechos x 4 escopos): M1-M0, M2-M1, M3-M1 (A) e M3-M1 (B)
  F1  Fig*_dados_v2              dados das figuras (a partir de abas existentes)
"""
from __future__ import annotations

import shutil
import sys
from math import factorial
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import CONFIG, GENERAL_BUCKET
from src.s15_importancia import lmg, prep, tabela_anuncio_aspecto
from src.s18_calibracao_sentimento import _rotulos
from src.sentimento import POLARIDADE, load_sentiment
from src.utils import Store

cfg = CONFIG
ROOT = Path(__file__).resolve().parent
SAIDA = ROOT / "outputs" / "ajustes_v2"
SAIDA.mkdir(parents=True, exist_ok=True)
PLANILHA_BASE = ROOT / "outputs" / "resultados_final_20261013_000705.xlsx"
PLANILHA_V2 = ROOT / "outputs" / "resultados_final_20261013_000705_v2.xlsx"
sA, sB = Store(cfg, suffix=""), Store(cfg, suffix="__B")
ASP = list(cfg.ASPECT_SEEDS)
NOME = {"limpeza": "Limpeza", "localizacao": "Localização", "checkin": "Check-in", "comunicacao": "Comunicação",
        "custo_beneficio": "Custo-benefício", "ruido_conforto": "Ruído e conforto", "seguranca": "Segurança",
        "precisao": "Precisão do anúncio", "comodidades": "Comodidades", "satisfacao_geral": "Satisfação geral", "geral": "Fora do perfil (geral)"}
RES: dict[str, pd.DataFrame] = {}
NAO_TESTADOS: dict = {}  # min_mencoes -> {tópico: nº de anúncios com a menção} dos tópicos com < 100 anúncios (não testados)


def wilson(k, n, z=1.959964):
    k, n = np.asarray(k, float), np.asarray(n, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        p = k / n
        den = 1 + z ** 2 / n
        c = (p + z ** 2 / (2 * n)) / den
        h = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / den
    return c - h, c + h


# ------------------------------------------------------------------------------------------------ M2
def classificacao_ic() -> None:
    H, _ = _rotulos(cfg, sA)
    H["asp_h"] = H["aspecto_humano"].replace({"nenhum": GENERAL_BUCKET})
    H["ok1"] = H["asp_h"] == H["aspecto_modelo"]
    g = H.groupby("aspecto_modelo").agg(n_rotuladas=("ok1", "size"), acertos=("ok1", "sum")).reset_index().rename(columns={"aspecto_modelo": "aspecto"})
    g["precisao"] = g["acertos"] / g["n_rotuladas"]
    g["wilson_inf"], g["wilson_sup"] = wilson(g["acertos"], g["n_rotuladas"])

    # segundo anotador (100 frases em comum): chave (rótulos do 1º anotador) + planilha preenchida (2º anotador)
    K = pd.read_excel(ROOT / "data" / "validacao_segundo_anotador_CHAVE.xlsx")
    A2 = pd.read_excel(ROOT / "data" / "validacao_segundo_anotador.xlsx", sheet_name="Amostra")[["id_cego", "aspecto_humano"]].rename(columns={"aspecto_humano": "aspecto_anotador2"})
    D = K.merge(A2, on="id_cego")
    for c in ("aspecto_anotador1", "aspecto_anotador2"):
        D[c] = D[c].replace({"nenhum": GENERAL_BUCKET})
    D["ok1"], D["ok2"] = D["aspecto_anotador1"] == D["aspecto_modelo"], D["aspecto_anotador2"] == D["aspecto_modelo"]
    D["ambos"], D["pelo_menos_um"], D["anotadores_iguais"] = D["ok1"] & D["ok2"], D["ok1"] | D["ok2"], D["aspecto_anotador1"] == D["aspecto_anotador2"]
    h = D.groupby("aspecto_modelo").agg(n_100=("ok1", "size"), acerto_anot1=("ok1", "sum"), acerto_anot2=("ok2", "sum"), ambos_concordam_com_modelo=("ambos", "sum"),
                                         pelo_menos_um_concorda=("pelo_menos_um", "sum"), anotadores_iguais=("anotadores_iguais", "sum")).reset_index().rename(columns={"aspecto_modelo": "aspecto"})
    for c in ("acerto_anot1", "acerto_anot2", "ambos_concordam_com_modelo", "pelo_menos_um_concorda", "anotadores_iguais"):
        h[f"{c}_prop"] = h[c] / h["n_100"]
        h[f"{c}_wilson_inf"], h[f"{c}_wilson_sup"] = wilson(h[c], h["n_100"])
    T = g.merge(h, on="aspecto", how="left")
    tot = {"aspecto": "TOTAL", "n_rotuladas": len(H), "acertos": int(H["ok1"].sum()), "n_100": len(D), "acerto_anot1": int(D["ok1"].sum()), "acerto_anot2": int(D["ok2"].sum()),
           "ambos_concordam_com_modelo": int(D["ambos"].sum()), "pelo_menos_um_concorda": int(D["pelo_menos_um"].sum()), "anotadores_iguais": int(D["anotadores_iguais"].sum())}
    tot["precisao"] = tot["acertos"] / tot["n_rotuladas"]
    tot["wilson_inf"], tot["wilson_sup"] = wilson(tot["acertos"], tot["n_rotuladas"])
    for c in ("acerto_anot1", "acerto_anot2", "ambos_concordam_com_modelo", "pelo_menos_um_concorda", "anotadores_iguais"):
        tot[f"{c}_prop"] = tot[c] / tot["n_100"]
        tot[f"{c}_wilson_inf"], tot[f"{c}_wilson_sup"] = wilson(tot[c], tot["n_100"])
    T = pd.concat([T, pd.DataFrame([tot])], ignore_index=True)

    # classificação pela regra do texto (precisão >= 0,60 e Spearman >= 0,20 nos dois modelos) e leitura com o intervalo
    vc = {m: s.load("validacao_construto").set_index("aspecto")["spearman"] for m, s in (("A", sA), ("B", sB))}
    T["spearman_A"] = T["aspecto"].map(vc["A"])
    T["spearman_B"] = T["aspecto"].map(vc["B"])
    regra = (T["precisao"] >= 0.60) & (T["spearman_A"] >= 0.20) & (T["spearman_B"] >= 0.20)
    T["classe_pela_regra"] = np.where(T["aspecto"].isin(["TOTAL", GENERAL_BUCKET]), "", np.where(regra, "confiável", "cautela"))
    T["limiar_060_no_IC"] = np.where(T["aspecto"].isin(["TOTAL", GENERAL_BUCKET]), "", np.where((T["wilson_inf"] <= 0.60) & (T["wilson_sup"] >= 0.60), "sim", "não"))
    T["classificacao_indicativa"] = np.where(T["classe_pela_regra"] == "", "", np.where((T["classe_pela_regra"] == "confiável") & (T["limiar_060_no_IC"] == "sim"),
                                                                                     "confiável (indicativa; IC inclui 0,60)", T["classe_pela_regra"]))
    T["aspecto_nome"] = T["aspecto"].map(NOME).fillna("Total")
    T = T.sort_values("aspecto", key=lambda s: s.map(lambda x: 1 if x == "TOTAL" else 0)).reset_index(drop=True)
    RES["Classificacao_IC_v2"] = T
    # concordância entre anotadores por aspecto (limpeza etc.), da chave dos anotadores
    P = D.groupby("aspecto_anotador1").agg(n=("anotadores_iguais", "size"), concordam=("anotadores_iguais", "sum")).reset_index()
    P["concordancia"] = P["concordam"] / P["n"]
    P["wilson_inf"], P["wilson_sup"] = wilson(P["concordam"], P["n"])
    RES["Concord_anotadores_v2"] = P


# ------------------------------------------------------------------------------------------------ R2
def _queixas(store: Store, min_mencoes: int) -> pd.DataFrame:
    """Mesma especificação de s15.importancia_topicos (queixas), com a regra de menção >= min_mencoes."""
    F = tabela_anuncio_aspecto(cfg, store)
    A = store.load("sentencas_aspecto")
    A = A[A["topic_direto"] & (A["topic"] >= 0)]
    A = A.merge(load_sentiment(store)[["text_id", "cls"]], on="text_id")
    A["cls"] = POLARIDADE[A["cls"].to_numpy()]
    T = store.load("topics_bertopic")[["topic", "top_words"]]
    asp_of = A.drop_duplicates("topic").set_index("topic")["aspecto"]
    F = F.set_index("id")
    y = F["review_scores_rating"].rank(pct=True)
    ctrl = sm.add_constant(pd.DataFrame({"log_v": F["log_v"], "log_used": np.log1p(F["n_used"])}))
    NAO_TESTADOS[min_mencoes] = {}
    cnt = A[A["cls"] == "neg"].groupby(["listing_id", "topic"]).size().unstack(fill_value=0).reindex(F.index, fill_value=0)
    rows = []
    for t in cnt.columns:
        x = (cnt[t] >= min_mencoes).astype(float)
        n1 = int(x.sum())
        if n1 < 100 or n1 > len(x) - 100:
            NAO_TESTADOS[min_mencoes][int(t)] = n1
            continue
        fit = sm.OLS(y.to_numpy(), pd.concat([x.rename("x"), ctrl], axis=1).to_numpy(float), missing="drop").fit(cov_type="HC3")
        rows.append({"topic": int(t), "aspecto": asp_of.get(t), "n_anuncios_com_mencao": n1, "prevalencia": n1 / len(x),
                     "efeito_pontos_percentil_nota": 100 * fit.params[0], "ep": 100 * fit.bse[0], "p": fit.pvalues[0]})
    R = pd.DataFrame(rows).merge(T, on="topic", how="left")
    p = R["p"].to_numpy()
    o = np.argsort(p)
    q = np.empty_like(p)
    q[o] = np.minimum.accumulate((p[o] * len(p) / (np.arange(len(p)) + 1))[::-1])[::-1]
    R["q_BH"] = np.minimum(q, 1)
    R["impacto_x_prevalencia"] = R["efeito_pontos_percentil_nota"] * R["prevalencia"]
    return R.sort_values("impacto_x_prevalencia").reset_index(drop=True)


def queixas_min2() -> None:
    det, res = [], []
    for modelo, st in (("A", sA), ("B", sB)):
        base_pq = st.load("imp_topicos_queixas")
        r1 = _queixas(st, 1)
        # conferência: a reexecução com a regra original reproduz a aba existente
        m = r1.merge(base_pq[["topic", "efeito_pontos_percentil_nota", "q_BH"]], on="topic", suffixes=("", "_orig"))
        assert len(m) == len(base_pq) and np.allclose(m["efeito_pontos_percentil_nota"], m["efeito_pontos_percentil_nota_orig"], atol=1e-6), "reexecução diverge da aba existente"
        r2 = _queixas(st, 2)
        r1["rank_base"], r2["rank_min2"] = np.arange(1, len(r1) + 1), np.arange(1, len(r2) + 1)
        d = r1[["topic", "aspecto", "top_words", "n_anuncios_com_mencao", "prevalencia", "efeito_pontos_percentil_nota", "ep", "q_BH", "rank_base"]].rename(
            columns={"n_anuncios_com_mencao": "n_base", "prevalencia": "prev_base", "efeito_pontos_percentil_nota": "efeito_base", "ep": "ep_base", "q_BH": "q_base"}).merge(
            r2[["topic", "n_anuncios_com_mencao", "prevalencia", "efeito_pontos_percentil_nota", "ep", "q_BH", "rank_min2"]].rename(
                columns={"n_anuncios_com_mencao": "n_min2", "prevalencia": "prev_min2", "efeito_pontos_percentil_nota": "efeito_min2", "ep": "ep_min2", "q_BH": "q_min2"}), on="topic", how="left")
        d["diferenca_efeito"] = d["efeito_min2"] - d["efeito_base"]
        d["n_min2_se_nao_testada"] = d["topic"].map(NAO_TESTADOS.get(2, {}))
        d.insert(0, "modelo", modelo)
        det.append(d)
        top15 = r1.head(15)["topic"].tolist()
        top15_m2 = r2.head(15)["topic"].tolist()
        t15 = d[d["topic"].isin(top15)]
        sig = lambda x: int(((x["efeito_min2"] < 0) & (x["q_min2"] < 0.05)).sum())
        res.append({"modelo": modelo, "testadas_base": len(r1), "testadas_min2": len(r2), "queixas_q05_base": int(((r1["efeito_pontos_percentil_nota"] < 0) & (r1["q_BH"] < 0.05)).sum()),
                    "queixas_q05_min2": int(((r2["efeito_pontos_percentil_nota"] < 0) & (r2["q_BH"] < 0.05)).sum()),
                    "top15_base_que_seguem_no_top15_min2": len(set(top15) & set(top15_m2)), "top15_base_testadas_em_min2": int(t15["efeito_min2"].notna().sum()),
                    "top15_base_com_q05_e_sinal_igual_em_min2": sig(t15), "efeito_medio_base_nas_testadas": float(t15.dropna(subset=["efeito_min2"])["efeito_base"].mean()), "efeito_medio_min2_nas_testadas": float(t15["efeito_min2"].mean()),
                    "variacao_media_efeito_top15": float(t15["diferenca_efeito"].mean()), "variacao_min_top15": float(t15["diferenca_efeito"].min()), "variacao_max_top15": float(t15["diferenca_efeito"].max()),
                    "intervalo_efeito_base_nas_testadas": f"{t15.dropna(subset=['efeito_min2'])['efeito_base'].min():.1f} a {t15.dropna(subset=['efeito_min2'])['efeito_base'].max():.1f}", "intervalo_efeito_min2_nas_testadas": f"{t15['efeito_min2'].min():.1f} a {t15['efeito_min2'].max():.1f}",
                    "nao_testadas_em_min2_n_anuncios": "; ".join(f"{int(r.topic)}: {int(r.n_min2_se_nao_testada)}" for r in t15[t15["efeito_min2"].isna()].itertuples()),
                    "coincidencia_top15_A_B_min2": np.nan})
    RES["Queixas_min2_v2"] = pd.concat(det, ignore_index=True)
    Rz = pd.DataFrame(res)
    a2 = set(RES["Queixas_min2_v2"].query("modelo=='A'").sort_values("rank_min2")["topic"].head(15))
    b2 = set(RES["Queixas_min2_v2"].query("modelo=='B'").sort_values("rank_min2")["topic"].head(15))
    Rz["coincidencia_top15_A_B_min2"] = len(a2 & b2)
    RES["Queixas_min2_resumo_v2"] = Rz


# ------------------------------------------------------------------------------------------------ R3
# subaspecto de cada tópico de comodidades: pela palavra de maior peso do tópico (primeira de top_words), conferida com as demais
SUB = {
    "banheiro_chuveiro": [18, 32, 99, 114],
    "climatizacao": [10],
    "cozinha_utensilios": [31, 39, 172, 157],
    "cama_colchao": [34, 69],
    "internet": [130, 149, 138],
    "manutencao_reparos": [136, 53],
}
SUB_NOME = {"banheiro_chuveiro": "Banheiro e chuveiro", "climatizacao": "Climatização", "cozinha_utensilios": "Cozinha e utensílios", "cama_colchao": "Cama e colchão",
            "internet": "Internet", "manutencao_reparos": "Manutenção e reparos", "demais_comodidades": "Demais comodidades"}


def _lmg_players(Z: pd.DataFrame, y: pd.Series) -> tuple[np.ndarray, float]:
    """LMG rápido (vetorizado) para muitos preditores. Z já padronizado, sem NaN."""
    p = Z.shape[1]
    R = np.corrcoef(np.column_stack([Z.to_numpy(), y.to_numpy()]), rowvar=False)
    Rxx, rxy = R[:p, :p], R[:p, p]
    r2 = np.zeros(1 << p)
    for mask in range(1, 1 << p):
        idx = [i for i in range(p) if mask >> i & 1]
        r = rxy[idx]
        r2[mask] = r @ np.linalg.solve(Rxx[np.ix_(idx, idx)] + 1e-9 * np.eye(len(idx)), r)
    pop = np.zeros(1 << p, dtype=np.int16)
    for j in range(p):
        pop += ((np.arange(1 << p) >> j) & 1).astype(np.int16)
    w = np.array([factorial(k) * factorial(p - k - 1) / factorial(p) for k in range(p)])
    out = np.zeros(p)
    allm = np.arange(1 << p)
    for j in range(p):
        sem = allm[((allm >> j) & 1) == 0]
        out[j] = np.sum(w[pop[sem]] * (r2[sem | (1 << j)] - r2[sem]))
    return out, float(r2[-1])


def _z(X: pd.DataFrame) -> pd.DataFrame:
    return (X - X.mean()) / X.std()


def comodidades() -> None:
    mapa = []
    topics = pd.read_parquet(sA.tables / "topics_bertopic.parquet")[["topic", "top_words"]]
    sub_of = {t: s for s, ts in SUB.items() for t in ts}
    allrows = []
    for modelo, st in (("A", sA), ("B", sB)):
        F = tabela_anuncio_aspecto(cfg, st)
        S = st.load("sentencas_aspecto")
        S = S[S["aspecto"] == "comodidades"]
        if modelo == "A":
            tops = S.groupby("topic").size().rename("n_sentencas_comodidades").reset_index()
            tops["subaspecto"] = tops["topic"].map(sub_of).fillna("demais_comodidades")
            mp = tops.merge(topics, on="topic", how="left")
            mp["subaspecto_nome"] = mp["subaspecto"].map(SUB_NOME)
            mp["palavra_guia"] = mp["top_words"].str.split(",").str[0]
            mapa.append(mp.sort_values(["subaspecto", "n_sentencas_comodidades"], ascending=[True, False]))
        S = S.assign(sub=S["topic"].map(sub_of).fillna("demais_comodidades"))
        g = S.groupby(["listing_id", "sub"])["stars"].agg(["mean", "count"]).reset_index()
        mm = g.pivot(index="listing_id", columns="sub", values="mean").reindex(columns=list(SUB_NOME))
        cc = g.pivot(index="listing_id", columns="sub", values="count").reindex(columns=list(SUB_NOME)).fillna(0)
        outros = [a for a in ASP if a != "comodidades"]
        Xb, yb, _ = prep(F, ASP, "review_scores_rating")
        cb, r2b = lmg(Xb, yb)
        base = dict(zip(ASP, cb / r2b))
        ex = st.load("imp_lmg").query("alvo.str.startswith('nota_global')", engine="python").set_index("aspecto")["parcela_do_R2"]
        assert np.allclose([base[a] for a in ASP], ex.reindex(ASP).to_numpy(), atol=1e-6), "LMG original não reproduz a aba"
        for i, a in enumerate(ASP):
            allrows.append({"modelo": modelo, "variante": "original (10 aspectos)", "preditor": a, "tipo": "aspecto", "contribuicao_R2": cb[i], "parcela_do_R2": cb[i] / r2b,
                            "R2_total": r2b, "n": len(yb), "proporcao_anuncios_com_dado_proprio": float(F[f"s_{a}"].notna().mean())})
        for minimo, rotulo in ((cfg.MIN_SENT_PER_ASPECT, "subaspectos, mínimo de 2 sentenças (regra do estudo)"), (1, "subaspectos, mínimo de 1 sentença (sensibilidade)")):
            m = mm.where(cc >= minimo).add_prefix("s_")
            F2 = F.merge(m, left_on="id", right_index=True, how="left")
            cols = [f"s_{a}" for a in outros] + [f"s_{k}" for k in SUB_NOME]
            X = F2[cols].copy()
            pres = X.notna().mean()
            X = _z(X.fillna(X.mean()))
            d = pd.concat([X, F2["review_scores_rating"]], axis=1).dropna()
            y = d["review_scores_rating"].rank(pct=True)
            y = (y - y.mean()) / y.std()
            contrib, r2 = _lmg_players(d[cols], y)
            for c_, v in zip(cols, contrib):
                nome = c_[2:]
                allrows.append({"modelo": modelo, "variante": rotulo, "preditor": nome, "tipo": "subaspecto de comodidades" if nome in SUB_NOME else "aspecto",
                                "contribuicao_R2": v, "parcela_do_R2": v / r2, "R2_total": r2, "n": len(d), "proporcao_anuncios_com_dado_proprio": float(pres[c_])})
    RES["Mapa_comodidades_v2"] = mapa[0]
    L = pd.DataFrame(allrows)
    soma = L[L["tipo"] == "subaspecto de comodidades"].groupby(["modelo", "variante"]).agg(contribuicao_R2=("contribuicao_R2", "sum"), parcela_do_R2=("parcela_do_R2", "sum"),
                                                                                        R2_total=("R2_total", "first"), n=("n", "first")).reset_index()
    soma["preditor"], soma["tipo"] = "Soma dos 7 subaspectos de comodidades", "soma"
    RES["LMG_comodidades_v2"] = pd.concat([L, soma], ignore_index=True)


# ------------------------------------------------------------------------------------------------ R4
def ausencia() -> None:
    rows = []
    for modelo, st in (("A", sA), ("B", sB)):
        F = tabela_anuncio_aspecto(cfg, st)
        cols = [f"s_{a}" for a in ASP]
        X = F[cols].copy()
        pres = X.notna().astype(float)
        pres.columns = [f"tem_{a}" for a in ASP]
        keep = [c for c in pres.columns if pres[c].std() > 0]
        Z = pd.concat([_z(X.fillna(X.mean())), _z(pres[keep])], axis=1)
        d = pd.concat([Z, F["review_scores_rating"]], axis=1).dropna()
        y = d["review_scores_rating"].rank(pct=True)
        y = (y - y.mean()) / y.std()
        pl = cols + keep
        contrib, r2 = _lmg_players(d[pl], y)
        sh = dict(zip(pl, contrib))
        Xb, yb, _ = prep(F, ASP, "review_scores_rating")
        cb, r2b = lmg(Xb, yb)
        for i, a in enumerate(ASP):
            s_, t_ = sh[f"s_{a}"], sh.get(f"tem_{a}", np.nan)
            rows.append({"modelo": modelo, "aspecto": a, "parcela_original": cb[i] / r2b, "R2_total_original": r2b,
                         "parcela_sentimento_com_indicadores": s_ / r2, "parcela_indicador_de_ausencia": t_ / r2 if t_ == t_ else np.nan,
                         "parcela_sentimento_mais_indicador": (s_ + (t_ if t_ == t_ else 0)) / r2, "R2_total_com_indicadores": r2, "n": len(d),
                         "proporcao_sem_dado_proprio_imputada": float(F[f"s_{a}"].isna().mean())})
    R = pd.DataFrame(rows)
    R["variacao_pontos_sentimento"] = 100 * (R["parcela_sentimento_com_indicadores"] - R["parcela_original"])
    RES["LMG_ausencia_v2"] = R


# ------------------------------------------------------------------------------------------------ F3
def tabela12() -> None:
    code = {"M1 R_off − M0 controles": "M1_menos_M0", "M2 R_syn − M1 R_off": "M2_menos_M1", "M3 R_off + R_syn − M1 R_off": "M3_menos_M1"}
    out = None
    for modelo, st, cs in (("A", sA, list(code.values())), ("B", sB, ["M3_menos_M1"])):
        d = st.load("analise_a_diferencas")
        d = d[d["comparacao"].isin(code)].assign(c=lambda x: x["comparacao"].map(code))
        for c in cs:
            s = d[d["c"] == c].set_index(["desfecho", "escopo"])[["n", "delta_r2_medio", "p2.5", "p97.5"]]
            s.columns = ["n", f"{modelo}_{c}", f"{modelo}_{c}_ic_inf", f"{modelo}_{c}_ic_sup"]
            if out is None:
                out = s
            else:
                out = out.join(s.drop(columns=["n"]))
    out = out.reset_index()
    order = {d: i for i, d in enumerate(["estimated_occupancy_l365d", "estimated_revenue_l365d", "number_of_reviews_ltm"])}
    out["_o"] = out["desfecho"].map(order)
    out["_e"] = out["escopo"].map(lambda e: 0 if e.startswith("amostra") else float(e.split(">=")[1]))
    RES["Tabela12_completa_v2"] = out.sort_values(["_o", "_e"]).drop(columns=["_o", "_e"]).reset_index(drop=True)


# ------------------------------------------------------------------------------------------------ F1 (dados das figuras)
def dados_figuras() -> None:
    rs = sA.load("rating_sintetico")
    bins = np.arange(0.95, 5.0001 + 0.1, 0.1)
    # Fig. 2: histograma da nota oficial e do índice sintético (R_syn_raw), mesma amostra
    edges = np.round(np.arange(1.0, 5.0 + 0.0001, 0.1), 2)
    h1, _ = np.histogram(rs["R_off"], bins=np.append(edges, 5.1))
    h2, _ = np.histogram(rs["R_syn_raw"], bins=np.append(edges, 5.1))
    RES["Fig2_histograma_v2"] = pd.DataFrame({"faixa_inicio": edges, "n_nota_oficial": h1[: len(edges)], "n_indice_sintetico": h2[: len(edges)]}).assign(n_total=len(rs))
    RES["Fig2_resumo_v2"] = pd.DataFrame({"medida": ["n", "média", "dp", "mediana", "p10", "p90", "% = 5,0"], "nota_oficial": [len(rs), rs["R_off"].mean(), rs["R_off"].std(), rs["R_off"].median(),
                                          rs["R_off"].quantile(.1), rs["R_off"].quantile(.9), 100 * (rs["R_off"] >= 5).mean()],
                                          "indice_sintetico": [len(rs), rs["R_syn_raw"].mean(), rs["R_syn_raw"].std(), rs["R_syn_raw"].median(), rs["R_syn_raw"].quantile(.1),
                                                               rs["R_syn_raw"].quantile(.9), 100 * (rs["R_syn_raw"] >= 5).mean()]})
    # Fig. 3: LMG A e B + classificação
    LA, LB = sA.load("imp_lmg"), sB.load("imp_lmg")
    f = lambda L, m: L[L["alvo"].str.startswith("nota_global")][["aspecto", "parcela_do_R2"]].rename(columns={"parcela_do_R2": f"parcela_{m}"})
    cl = {"limpeza": "confiável", "localizacao": "confiável", "custo_beneficio": "confiável"}
    L3 = f(LA, "A").merge(f(LB, "B"), on="aspecto")
    L3["classificacao"] = L3["aspecto"].map(cl).fillna("cautela")
    L3["R2_total_A"], L3["R2_total_B"] = LA["R2_total"].iloc[0], LB["R2_total"].iloc[0]
    RES["Fig3_LMG_v2"] = L3.sort_values("parcela_A", ascending=False).reset_index(drop=True)
    # Fig. 4: diferenças (pontos de percentil) com IC 95% (efeito +- 1,96 ep, ep robusto HC3 da mesma especificação) para as linhas das Tabelas 9 e 10
    Q, E = sA.load("imp_topicos_queixas"), sA.load("imp_topicos_elogios")
    Q12 = Q.head(15)
    for t, nome in ((Q, "queixa"), (E, "elogio")):
        t["ic_inf"] = t["efeito_pontos_percentil_nota"] - 1.959964 * t["ep"]
        t["ic_sup"] = t["efeito_pontos_percentil_nota"] + 1.959964 * t["ep"]
    cols = ["tipo", "topic", "aspecto", "top_words", "n_anuncios_com_mencao", "prevalencia", "efeito_pontos_percentil_nota", "ep", "ic_inf", "ic_sup", "q_BH", "impacto_x_prevalencia"]
    RES["Fig4_diferencas_v2"] = pd.concat([Q[cols].head(15), E[cols].head(15)], ignore_index=True)
    # Fig. 1: números do pipeline (da aba Estat_Corpus e das tabelas)
    cs = sA.load("corpus_stats")
    RES["Fig1_numeros_v2"] = cs


def main() -> None:
    partes = {f.__name__: f for f in (classificacao_ic, queixas_min2, comodidades, ausencia, tabela12, dados_figuras)}
    escolhidas = sys.argv[1:] or list(partes)
    for f in SAIDA.glob("*.parquet"):  # partes não recalculadas mantêm o resultado já gravado
        RES[f.stem] = pd.read_parquet(f)
    for nome in escolhidas:
        print("==>", nome, flush=True)
        partes[nome]()
    for k, v in RES.items():
        v.to_parquet(SAIDA / f"{k}.parquet", index=False)
    shutil.copy(PLANILHA_BASE, PLANILHA_V2)
    with pd.ExcelWriter(PLANILHA_V2, engine="openpyxl", mode="a", if_sheet_exists="replace") as w:
        for k, v in RES.items():
            v.to_excel(w, sheet_name=k[:31], index=False)
    print("planilha:", PLANILHA_V2)


if __name__ == "__main__":
    main()
