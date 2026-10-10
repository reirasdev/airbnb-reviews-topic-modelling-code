"""Segundo anotador da validação manual.

  python segundo_anotador.py gerar                      # cria data/validacao_segundo_anotador.xlsx (enviar) e ..._CHAVE.xlsx (NÃO enviar)
  python segundo_anotador.py kappa data/validacao_segundo_anotador.xlsx   # concordância entre anotadores (depois de preenchida)
"""
from __future__ import annotations

import argparse
import logging
import sys

import pandas as pd

from config import CONFIG
from src.s21_segundo_anotador import gerar, kappa

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)


def main() -> None:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("gerar")
    k = sp.add_parser("kappa")
    k.add_argument("planilha")
    k.add_argument("--chave", default=None)
    a = ap.parse_args()
    if a.cmd == "gerar":
        print(*gerar(CONFIG), sep="\n")
    else:
        pd.set_option("display.width", 200)
        for nome, t in kappa(CONFIG, a.planilha, a.chave).items():
            print(f"\n== {nome}\n{t.round(3).to_string(index=False)}")


if __name__ == "__main__":
    main()
