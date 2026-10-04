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


def write_excel(cfg, store: Store, path: Path, timestamp: str) -> None:
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
        "Formula_Ocupacao": pd.concat([get("formula_ocupacao"), pd.DataFrame({"": [""]}), get("coef_forma_flexivel")], ignore_index=True),
        "Sem_LTM": pd.concat([get("sem_ltm_modelos"), pd.DataFrame({"": [""]}), get("sem_ltm_diferencas"), pd.DataFrame({"": [""]}), get("sem_ltm_faixas")], ignore_index=True),
        "Investigacao_Coef": pd.concat([get("investigacao_coef"), pd.DataFrame({"": [""]}), get("investigacao_coef_correlacoes")], ignore_index=True),
        "Resumo_Log": resumo,
    }
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        for name, df in sheets.items():
            df.to_excel(xw, sheet_name=name, index=False)
            ws = xw.sheets[name]
            ws.freeze_panes = "A2"
            for i, col in enumerate(df.columns, 1):
                width = min(60, max(10, len(str(col)) + 2, int(np.nan_to_num(df[col].astype(str).str.len().head(200).max())) + 2))
                ws.column_dimensions[ws.cell(1, i).column_letter].width = width
    log.info("Excel gravado em %s", path)
