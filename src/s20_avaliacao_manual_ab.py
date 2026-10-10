"""Etapa 20 — Avaliação de A e de B nas frases rotuladas pelo pesquisador (item 1.5) e aplicação da REGRA 1.6.

Métricas por modelo (mesmas para A e B): acurácia, F1 macro, kappa simples e ponderado linear na amostra; Spearman entre o rótulo humano (-1/0/1) e as estrelas esperadas; matriz de
confusão; acerto por classe prevista; recorte por idioma (destaque para o português); e as estimativas ponderadas pela população.
Pesos de população: os dos estratos ORIGINAIS (aspecto previsto por BERTopic × polaridade prevista por A, em faixas de estrelas de A), os mesmos para A e B (`s18._rotulos`).
Bootstrap estratificado (dentro de cada estrato original) de 2000 réplicas para os IC 95% de cada modelo e da diferença B − A, no kappa ponderado linear e na acurácia
populacionais, no total e só em português. REGRA 1.6 (historico, seção 30): principal = B se o IC 95% de (B − A) no kappa ponderado linear populacional exclui 0 a favor de B.
Saídas compartilhadas: cmp_manual_modelos, cmp_manual_confusao_A/B, cmp_manual_por_classe, cmp_manual_idioma, cmp_manual_diferenca, cmp_regra_modelo_principal.
"""
from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import cohen_kappa_score, f1_score

from .s18_calibracao_sentimento import CLASSES, _rotulos
from .sentimento import load_sentiment
from .utils import Store, stage

log = logging.getLogger("pipeline")
LAB = [0, 1, 2]
BOOT = 2000


def _probs_b_so_para(cfg, text_ids: np.ndarray, store: Store) -> pd.DataFrame:
    """Se a inferência completa de B ainda não existe, calcula B só para os textos rotulados (mesma função e mesmo modelo); a tabela completa tem prioridade quando existe."""
    from .s2_sentimento import _load_model_b, _predict_b

    tok, model = _load_model_b(cfg)
    T = store.load("texts").set_index("text_id").loc[text_ids, "text"]
    p = _predict_b(T.tolist(), tok, model, cfg)
    M = pd.DataFrame(p, columns=[f"p{k}" for k in range(1, 6)])
    M.insert(0, "text_id", text_ids)
    M["stars"] = p @ np.arange(1, 6)
    M["cls"] = np.array([0, 0, 1, 2, 2])[p.argmax(1)]
    return M


def _metricas(y, pred, stars, w) -> dict:
    return {"acuracia": float(np.average(pred == y, weights=w)),
            "kappa": float(cohen_kappa_score(y, pred, labels=LAB, sample_weight=w)),
            "kappa_linear": float(cohen_kappa_score(y, pred, labels=LAB, weights="linear", sample_weight=w)),
            "f1_macro": float(f1_score(y, pred, labels=LAB, average="macro", sample_weight=w, zero_division=0))}


def run(cfg, store: Store) -> None:
    with stage("Etapa 20 — Avaliação de A e B nas frases rotuladas e regra 1.6"):
        sA, sB = Store(cfg, suffix=""), Store(cfg, suffix="__B")
        H, wt = _rotulos(cfg, sA)  # H: rótulos + gabarito de A (inclui sent_id, idioma, aspecto_modelo, estrelas_modelo, pol)
        S = sA.load("sentences")[["sent_id", "text_id"]]
        H = H.merge(S, on="sent_id", how="left")
        A = load_sentiment(sA).set_index("text_id")
        if sB.exists("sentiment"):
            B, origem_b = load_sentiment(sB).set_index("text_id"), "tabela completa de B"
        else:
            B, origem_b = _probs_b_so_para(cfg, H["text_id"].to_numpy(), sA).set_index("text_id"), "inferência direta nas frases rotuladas (B completo ainda não existe)"
        log.info("Origem das probabilidades de B: %s", origem_b)
        y = H["sentimento_humano"].map({c: i for i, c in enumerate(CLASSES)}).to_numpy()
        pa, pb = A.loc[H["text_id"], "cls"].to_numpy(), B.loc[H["text_id"], "cls"].to_numpy()
        ea, eb = A.loc[H["text_id"], "stars"].to_numpy(), B.loc[H["text_id"], "stars"].to_numpy()
        H["cls_A"], H["cls_B"], H["stars_A"], H["stars_B"] = pa, pb, ea, eb
        # conferência: as classes de A recalculadas com a precisão total coincidem com as da aba Val_Manual (probabilidades arredondadas a 3 casas)?
        legado = H[["p_neg", "p_neu", "p_pos"]].to_numpy().argmax(1)
        log.info("Classes de A: %d de %d idênticas às calculadas a partir das probabilidades arredondadas da planilha de rótulos", int((legado == pa).sum()), len(H))

        w = wt
        rows = []
        for nome, pred, stars in (("A", pa, ea), ("B", pb, eb)):
            m_amostra = _metricas(y, pred, stars, None)
            m_pop = _metricas(y, pred, stars, w)
            rows.append({"modelo": nome, "n": len(H), **{f"{k}_amostra": v for k, v in m_amostra.items()}, **{f"{k}_populacao": v for k, v in m_pop.items()},
                         "spearman_rotulo_estrelas": float(stats.spearmanr(y, stars)[0])})
        Mods = pd.DataFrame(rows)

        # confusões (linhas = humano) e acerto por classe prevista; por idioma
        cl = np.array(CLASSES)
        for nome, pred in (("A", pa), ("B", pb)):
            sB_ = pd.crosstab(pd.Series(cl[y], name="humano"), pd.Series(cl[pred], name=f"modelo {nome}")).reindex(index=CLASSES, columns=CLASSES, fill_value=0)
            sA.save(f"cmp_manual_confusao_{nome}", sB_.reset_index())
        por_classe = []
        for nome, pred in (("A", pa), ("B", pb)):
            for k, c in enumerate(CLASSES):
                m = pred == k
                por_classe.append({"modelo": nome, "classe_prevista": c, "n_previstas": int(m.sum()), "acerto": float((y[m] == k).mean()) if m.any() else np.nan,
                                   "acerto_ponderado": float(np.average(y[m] == k, weights=w[m])) if m.any() and w[m].sum() > 0 else np.nan})
        idi = []
        H["grupo"] = H["idioma"].where(H["idioma"].isin(["pt", "en", "es"]), "demais")
        for g, d in H.groupby("grupo"):
            ii = d.index.to_numpy()
            for nome, pred in (("A", pa), ("B", pb)):
                idi.append({"idioma": g, "modelo": nome, "n": len(d), "acuracia_amostra": float((pred[ii] == y[ii]).mean()),
                            "acuracia_ponderada": float(np.average(pred[ii] == y[ii], weights=w[ii])),
                            "kappa_linear_amostra": float(cohen_kappa_score(y[ii], pred[ii], labels=LAB, weights="linear")) if len(d) >= 10 else np.nan})

        # bootstrap estratificado (estratos originais); pt-only reamostra dentro dos mesmos estratos, restrito às frases em português
        cel = H["aspecto_modelo"].astype(str) + "|" + H["pol"].astype(str)
        rng = np.random.default_rng(cfg.SEED)

        def boot(mask):
            base = {c: np.flatnonzero((cel == c).to_numpy() & mask) for c in cel.unique()}
            base = {c: v for c, v in base.items() if len(v)}
            out = []
            for _ in range(BOOT):
                i = np.concatenate([rng.choice(v, len(v), replace=True) for v in base.values()])
                ma, mb = _metricas(y[i], pa[i], None, w[i]), _metricas(y[i], pb[i], None, w[i])
                out.append((ma["acuracia"], mb["acuracia"], ma["kappa_linear"], mb["kappa_linear"], ma["kappa"], mb["kappa"]))
            return np.array(out)

        dif = []
        for escopo, mask in (("total", np.ones(len(H), bool)), ("só português", (H["idioma"] == "pt").to_numpy())):
            r = boot(mask)
            pe = lambda col: (float(np.percentile(col, 2.5)), float(np.percentile(col, 97.5)))
            m_a, m_b = _metricas(y[mask], pa[mask], None, w[mask]), _metricas(y[mask], pb[mask], None, w[mask])
            for medida, ia, ib, ka in (("acurácia populacional", 0, 1, "acuracia"), ("kappa ponderado linear populacional", 2, 3, "kappa_linear"), ("kappa simples populacional", 4, 5, "kappa")):
                d = r[:, ib] - r[:, ia]
                dif.append({"escopo": escopo, "medida": medida, "n_frases": int(mask.sum()), "A": m_a[ka], "A_ic_inf": pe(r[:, ia])[0], "A_ic_sup": pe(r[:, ia])[1],
                            "B": m_b[ka], "B_ic_inf": pe(r[:, ib])[0], "B_ic_sup": pe(r[:, ib])[1], "B_menos_A": m_b[ka] - m_a[ka], "dif_ic_inf": pe(d)[0], "dif_ic_sup": pe(d)[1],
                            "ic_exclui_zero": bool(pe(d)[0] > 0 or pe(d)[1] < 0)})
        Dif = pd.DataFrame(dif)
        regra = Dif[(Dif["escopo"] == "total") & (Dif["medida"] == "kappa ponderado linear populacional")].iloc[0]
        principal = "B" if regra["dif_ic_inf"] > 0 else "A"
        R = pd.DataFrame([{"regra": "B se o IC 95% de (B − A) no kappa ponderado linear populacional exclui 0 a favor de B; senão A",
                           "diferenca_B_menos_A": regra["B_menos_A"], "ic_inf": regra["dif_ic_inf"], "ic_sup": regra["dif_ic_sup"], "modelo_principal": principal,
                           "origem_das_probabilidades_de_B": origem_b}])
        for nome, t in (("cmp_manual_modelos", Mods), ("cmp_manual_por_classe", pd.DataFrame(por_classe)), ("cmp_manual_idioma", pd.DataFrame(idi)),
                        ("cmp_manual_diferenca", Dif), ("cmp_regra_modelo_principal", R)):
            sA.save(nome, t)
        pd.set_option("display.width", 220)
        log.info("Avaliação nas frases rotuladas:\n%s", Mods.round(4).T.to_string())
        log.info("Acerto por classe prevista:\n%s", pd.DataFrame(por_classe).round(3).to_string(index=False))
        log.info("Por idioma:\n%s", pd.DataFrame(idi).round(3).to_string(index=False))
        log.info("Diferença B − A (bootstrap estratificado, %d réplicas):\n%s", BOOT, Dif.round(4).to_string(index=False))
        log.info("REGRA 1.6 -> modelo principal: %s (dif. kappa linear pop. = %.4f; IC95%% [%.4f; %.4f])", principal, regra["B_menos_A"], regra["dif_ic_inf"], regra["dif_ic_sup"])
        sA.metric("etapa20", modelo_principal=principal, dif_kappa_linear_pop=round(float(regra["B_menos_A"]), 4), ic=[round(float(regra["dif_ic_inf"]), 4), round(float(regra["dif_ic_sup"]), 4)])
