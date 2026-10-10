"""Utilitários comuns do montador do texto unificado (formatação pt-BR, tabelas markdown, acesso às tabelas do cache)."""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import CONFIG  # noqa: E402
from src.utils import Store  # noqa: E402

sA, sB = Store(CONFIG, suffix=""), Store(CONFIG, suffix="__B")
ASP = ["limpeza", "localizacao", "checkin", "comunicacao", "custo_beneficio", "ruido_conforto", "seguranca", "precisao", "comodidades", "satisfacao_geral"]
ROT = {"limpeza": "Limpeza", "localizacao": "Localização", "checkin": "Check-in", "comunicacao": "Comunicação", "custo_beneficio": "Custo-benefício", "ruido_conforto": "Ruído e conforto",
       "seguranca": "Segurança", "precisao": "Precisão do anúncio", "comodidades": "Comodidades", "satisfacao_geral": "Satisfação geral"}
SUB = {"limpeza": "cleanliness", "localizacao": "location", "checkin": "checkin", "comunicacao": "communication", "custo_beneficio": "value", "precisao": "accuracy", "satisfacao_geral": "rating (nota global)"}


def f(x, d=2, sinal=False) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    s = f"{abs(x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    neg = x < 0 and float(s.replace(".", "").replace(",", ".")) != 0
    return ("−" if neg else ("+" if sinal else "")) + s


def pc(x, d=0, sinal=False) -> str:
    return f(100 * x, d, sinal) + "%"


def n(x) -> str:
    return f(float(x), 0)


def ic(lo, hi, d=2, sinal=False) -> str:
    return f"[{f(lo, d, sinal)}; {f(hi, d, sinal)}]"


def tabela(cab: list[str], linhas: list[list], alin: str | None = None) -> str:
    alin = alin or ("|---" + "|---:" * (len(cab) - 1) + "|")
    out = ["| " + " | ".join(cab) + " |", alin]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in linhas]
    return "\n".join(out)


def L(s: Store, nome: str) -> pd.DataFrame:
    return s.load(nome)


def abas(*nomes: str) -> str:
    return "\n*Abas da planilha:* " + ", ".join(f"`{x}`" for x in nomes) + ".\n"


def metrica(etapa: str, chave: str, s: Store = sA):
    v = s.metrics[etapa + s.suffix][chave]
    return ast.literal_eval(v) if isinstance(v, str) and v.startswith(("{", "[")) else v
