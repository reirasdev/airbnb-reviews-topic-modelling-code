"""Gera o .xlsx final: uma aba por resultado de etapa, para auditoria."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from .utils import Store

log = logging.getLogger("pipeline")


def _flat(d: dict, prefix: str = "") -> list[tuple[str, str]]:
    out = []
    for k, v in d.items():
        if isinstance(v, dict):
            out += _flat(v, f"{prefix}{k}.")
        else:
            out.append((f"{prefix}{k}", str(v)))
    return out


def build_sheets(cfg, store: Store, timestamp: str) -> dict:
    def get(name):
        return store.load(name) if store.exists(name) else pd.DataFrame({"aviso": [f"'{name}' não gerado nesta execução"]})

    conf = pd.DataFrame(_flat({k: v for k, v in cfg.as_dict().items()}), columns=["parametro", "valor"])
    conf.loc[len(conf)] = ["timestamp_execucao", timestamp]
    conf.loc[len(conf)] = ["cache_key", cfg.cache_key()]
    val = get("validacao_construto")
    absa = get("perfil_absa")
    resumo = pd.DataFrame([(e, k, str(v)) for e, kv in store.metrics.items() for k, v in kv.items()],
                          columns=["etapa", "metrica", "valor"])
    mapa = get("mapa_topico_aspecto")
    ab = [get("analise_b_faixas"), get("analise_b_isotonica")]
    sheets = {
        "Config": conf,
        "Estat_Corpus": pd.concat([get("corpus_stats").rename(columns={"metrica": "item", "valor": "valor"}),
                                   get("lang_dist").rename(columns={"idioma": "item"})], ignore_index=True),
        "Validacao_Construto": val,
        "Topicos_BERTopic": get("topics_bertopic"),
        "Topicos_LDA": pd.concat([get("topics_lda"), get("lda_grid")], axis=1),
        "Mapa_Topico_Aspecto": mapa,
        "Perfil_ABSA": absa,
        "Rating_Sintetico": get("rating_sintetico"),
        "Analise_A": pd.concat([get("analise_a_modelos"), pd.DataFrame({"": [""]}), get("analise_a_diferencas"),
                                pd.DataFrame({"": [""]}), get("analise_a_coefs")], ignore_index=True),
        "Analise_B": pd.concat([ab[0], pd.DataFrame({"": [""]}), ab[1]], ignore_index=True),
        "Sensibilidade": get("sensibilidade"),
        "Descritivo_Teto": get("descritivo_teto"),
        "Selecao": get("selecao"),
        "Val_Volume_Convergente": pd.concat([get("val_volume"), pd.DataFrame({"": [""]}), get("val_convergente")], ignore_index=True),
        "Val_Matriz": get("val_matriz"),
        "Val_Confiab_AUC": pd.concat([get("val_confiabilidade"), pd.DataFrame({"": [""]}), get("val_auc_kendall")], ignore_index=True),
        "Val_Recortes": get("val_recortes"),
        "Val_Manual": pd.concat([get("manual_resumo"), pd.DataFrame({"": [""]}), get("manual_confusao_sentimento"),
                                 pd.DataFrame({"": [""]}), get("manual_confusao_aspecto"), pd.DataFrame({"": [""]}),
                                 get("manual_aspecto_por_classe")], ignore_index=True),
        "Imp_Aspectos": pd.concat([get("imp_lmg"), pd.DataFrame({"": [""]}), get("imp_betas")], ignore_index=True),
        "Imp_Modelos": pd.concat([get("imp_gbm"), pd.DataFrame({"": [""]}), get("imp_logit")], ignore_index=True),
        "Imp_Segmentos_Sens": pd.concat([get("imp_segmentos"), pd.DataFrame({"": [""]}), get("imp_sensibilidade")], ignore_index=True),
        "Imp_Topicos_Queixas": get("imp_topicos_queixas"),
        "Imp_Topicos_Elogios": get("imp_topicos_elogios"),
        "Sazon_Volume": pd.concat([get("sazon_volume"), pd.DataFrame({"": [""]}), get("sazon_volume_por_ano")], ignore_index=True),
        "Sazon_Conteudo": pd.concat([get("sazon_aspecto"), pd.DataFrame({"": [""]}), get("sazon_topico")], ignore_index=True),
        "Sazon_Criterio": pd.concat([get("sazon_criterio"), pd.DataFrame({"": [""]}), get("sazon_calendario")], ignore_index=True),
        "Benchmark_Bairro_Tipo": pd.concat([get("benchmark_cidade_tipo"), pd.DataFrame({"": [""]}), get("benchmark_bairro_tipo")], ignore_index=True),
        "Calib_Sentimento": pd.concat([get("calib_cv"), pd.DataFrame({"": [""]}), get("calib_correlacoes")], ignore_index=True),
        "Formula_Ocupacao": pd.concat([get("formula_ocupacao"), pd.DataFrame({"": [""]}), get("coef_forma_flexivel")], ignore_index=True),
        "Resumo_Log": resumo,
        # abas de REFERÊNCIA (análise anterior com o controle de avaliações recentes e investigação resolvida); ao final por não serem resultado principal
        "REF_Sem_LTM": pd.concat([get("sem_ltm_modelos"), pd.DataFrame({"": [""]}), get("sem_ltm_diferencas"), pd.DataFrame({"": [""]}), get("sem_ltm_faixas")], ignore_index=True),
        "REF_Investigacao_Coef": pd.concat([get("investigacao_coef"), pd.DataFrame({"": [""]}), get("investigacao_coef_correlacoes")], ignore_index=True),
    }
    return sheets


def _salvar(sheets: dict, path: Path) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        for name, df in sheets.items():
            df.to_excel(xw, sheet_name=name[:31], index=False)
            ws = xw.sheets[name[:31]]
            ws.freeze_panes = "A2"
            for i, col in enumerate(df.columns, 1):
                width = min(60, max(10, len(str(col)) + 2, int(np.nan_to_num(df[col].astype(str).str.len().head(200).max())) + 2))
                ws.column_dimensions[ws.cell(1, i).column_letter].width = width
    log.info("Excel gravado em %s", path)


def write_excel(cfg, store: Store, path: Path, timestamp: str) -> None:
    _salvar(build_sheets(cfg, store, timestamp), path)


# abas que dependem do modelo de sentimento (a planilha final traz as do modelo principal com o nome normal e as do outro com sufixo)
DEPENDENTES = ["Validacao_Construto", "Perfil_ABSA", "Rating_Sintetico", "Analise_A", "Analise_B", "Sensibilidade", "Descritivo_Teto", "Selecao", "Val_Volume_Convergente",
               "Val_Matriz", "Val_Confiab_AUC", "Val_Recortes", "Val_Manual", "Imp_Aspectos", "Imp_Modelos", "Imp_Segmentos_Sens", "Imp_Topicos_Queixas", "Imp_Topicos_Elogios",
               "Sazon_Conteudo", "Sazon_Criterio", "Benchmark_Bairro_Tipo"]


def _mapa_revisao(cfg) -> pd.DataFrame:
    """Contagens da revisão humana do mapa tópico → aspecto (a partir de data/mapa_aspecto_confirmado.xlsx)."""
    p = Path(cfg.MAPPING_CSV).with_suffix(".xlsx")
    M = pd.read_excel(p)
    n = len(M)
    c = lambda m: int(m.sum())
    resumo = pd.DataFrame({"medida": ["tópicos", "sugestão automática aceita pelo pesquisador (aspecto_usuario == sugestao)", "alterados pelo pesquisador (aspecto_usuario != sugestao)",
                                      "reclassificados após discussão (alterado_por_claude)", "tópicos no mapa final em satisfacao_geral", "tópicos no mapa final em geral"],
                           "valor": [n, c(M["aspecto_usuario"] == M["sugestao"]), c(M["aspecto_usuario"] != M["sugestao"]), c(M["alterado_por_claude"]),
                                     c(M["aspecto_confirmado"] == "satisfacao_geral"), c(M["aspecto_confirmado"] == "geral")]})
    por = M.groupby("aspecto_confirmado").agg(topicos=("topic", "size"), frases_na_amostra_de_ajuste=("n_fit", "sum")).reset_index()
    return pd.concat([resumo, pd.DataFrame({"": [""]}), por], ignore_index=True)


def write_excel_final(cfg, path: Path, timestamp: str, principal: str, regra: pd.DataFrame | None) -> None:
    """Planilha única: abas do modelo principal com os nomes atuais, as do outro modelo com sufixo _mA/_mB, e as abas novas de comparação entre modelos."""
    sA, sB = Store(cfg, suffix=""), Store(cfg, suffix="__B")
    sp, so = (sA, sB) if principal == "A" else (sB, sA)
    outro = "B" if principal == "A" else "A"
    sheets = build_sheets(cfg, sp, timestamp)
    other = build_sheets(cfg, so, timestamp)
    conf = sheets["Config"]
    extra = [["MODELO_PRINCIPAL_DE_SENTIMENTO", f"{principal} ({cfg.SENTIMENT_MODEL if principal == 'A' else cfg.SENTIMENT_MODEL_B})"],
             ["MODELO_COMPARACAO_(robustez)", f"{outro} ({cfg.SENTIMENT_MODEL if outro == 'A' else cfg.SENTIMENT_MODEL_B})"],
             ["REGRA_1.6", "principal = B se o IC 95% (bootstrap estratificado) de (B − A) no kappa ponderado linear populacional de sentimento exclui 0 a favor de B; senão A. Registrada antes da execução (historico, seção 30)."],
             ["SEGUNDO_ANOTADOR", "pendente (planilha cega e script de kappa prontos; nenhum rótulo real preenchido)"],
             ["MAPA_LDA", "provisório: a confirmar pelo pesquisador (aba Checagem_LDA, coluna decisao_pesquisador)"]]
    if regra is not None and len(regra):
        r = regra.iloc[0]
        extra.append(["REGRA_1.6_RESULTADO", f"diferença B − A = {r['diferenca_B_menos_A']:.4f}; IC95% [{r['ic_inf']:.4f}; {r['ic_sup']:.4f}]; principal = {r['modelo_principal']}"])
    sheets["Config"] = pd.concat([conf, pd.DataFrame(extra, columns=conf.columns)], ignore_index=True)
    for nome in DEPENDENTES:
        if nome in other:
            sheets[f"{nome}_m{outro}"[:31]] = other[nome]

    def g(nome, store=sA):
        return store.load(nome) if store.exists(nome) else pd.DataFrame({"aviso": [f"'{nome}' não gerado"]})

    def juntar(*dfs):
        out = []
        for d in dfs:
            out += [d, pd.DataFrame({"": [""]})]
        return pd.concat(out[:-1], ignore_index=True)

    sheets["Comparacao_Sentimento_AB"] = juntar(g("cmp_descritivas"), g("cmp_concordancia"), g("cmp_confusao_polaridade"), g("cmp_concordancia_aspecto"))
    sheets["Avaliacao_Rotuladas_AB"] = juntar(g("cmp_manual_modelos"), g("cmp_manual_por_classe"), g("cmp_manual_idioma"), g("cmp_manual_confusao_A"), g("cmp_manual_confusao_B"))
    sheets["Diferenca_B_menos_A"] = juntar(g("cmp_regra_modelo_principal"), g("cmp_manual_diferenca"))
    sheets["Checagem_LDA"] = juntar(g("lda_shared_mapa"), g("lda_concordancia_sentencas", sp), g("lda_perfil_correlacao", sp), g("lda_validade", sp), g("lda_importancia_comparacao", sp))
    sheets["Resumo_AB"] = g("cmp_resumo_AB")
    sheets["Aspecto_Rotuladas"] = juntar(g("cmp_manual_aspecto"), g("cmp_manual_aspecto_por_classe"))
    sheets["Limite_30_Avaliacoes"] = g("limite30", sp)
    sheets["Sazon_NegativaGeral"] = g("sazon_negativa_geral", sp)
    sheets["Sazon_NegativaGeral_m" + outro] = g("sazon_negativa_geral", so)
    sheets["Mapa_Revisao"] = _mapa_revisao(cfg)
    sheets["Comparacoes_Multiplas"] = g("cmp_comparacoes_multiplas")
    sheets["Selecao_Teto"] = g("cmp_selecao_teto")
    sheets["RSyn_Resumo_AB"] = juntar(g("cmp_rsyn_resumo"), g("cmp_queixas_sobreposicao"), g("cmp_queixas_listas"))
    sheets["Analise_A_Intersecao"] = juntar(g("cmp_inter_diferencas"))
    for nome in ("validacao_construto", "analise_a_diferencas", "imp_lmg", "sensibilidade", "val_convergente", "imp_gbm", "imp_logit", "analise_b_faixas", "perfil_cobertura", "imp_segmentos", "imp_sensibilidade", "analise_a_coefs", "sazon_aspecto"):
        sheets[f"LadoALado_{nome}"[:31]] = g(f"cmp_ladoalado_{nome}")
    ordem = ["Config", "Resumo_AB"] if "Resumo_AB" in sheets else ["Config"]
    sheets = {k: sheets[k] for k in ordem + [k for k in sheets if k not in ordem]}
    _salvar(sheets, path)

