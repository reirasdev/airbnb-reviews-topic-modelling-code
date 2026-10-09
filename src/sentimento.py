"""Acesso ao sentimento por texto único com a polaridade discreta `cls` (0 = negativo, 1 = neutro, 2 = positivo).

A: cls = argmax(P(neg), P(neu), P(pos)) (como sempre foi no pipeline).
B: cls pela classe mais provável entre 1 e 5 estrelas (1-2 negativo, 3 neutro, 4-5 positivo); gravado pela etapa 2.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .utils import Store

POLARIDADE = np.array(["neg", "neu", "pos"])


def load_sentiment(store: Store) -> pd.DataFrame:
    M = store.load("sentiment")
    if "cls" not in M.columns:  # tabela de A, anterior à introdução da coluna
        M["cls"] = M[["p_neg", "p_neu", "p_pos"]].to_numpy().argmax(1)
    return M
