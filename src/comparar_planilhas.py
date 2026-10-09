"""Compara duas planilhas de resultados aba a aba (linha de base): formato, textos e números (tolerância relativa/absoluta).

Uso: python -m src.comparar_planilhas planilha_referencia.xlsx planilha_nova.xlsx [--ignorar Config Resumo_Log]
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd


def comparar(ref: str, novo: str, ignorar: tuple[str, ...] = ("Config",), rtol: float = 1e-6, atol: float = 1e-9) -> pd.DataFrame:
    a, b = pd.ExcelFile(ref), pd.ExcelFile(novo)
    rows = []
    for nome in a.sheet_names:
        if nome in ignorar:
            continue
        if nome not in b.sheet_names:
            rows.append({"aba": nome, "status": "AUSENTE na nova", "celulas": 0, "diferentes": None, "max_dif_abs": None})
            continue
        x, y = a.parse(nome, header=None), b.parse(nome, header=None)
        if x.shape != y.shape:
            rows.append({"aba": nome, "status": f"FORMATO {x.shape} vs {y.shape}", "celulas": x.size, "diferentes": None, "max_dif_abs": None})
            continue
        nd, mx, tot = 0, 0.0, 0
        for c in range(x.shape[1]):
            u, v = x.iloc[:, c], y.iloc[:, c]
            un, vn = pd.to_numeric(u, errors="coerce"), pd.to_numeric(v, errors="coerce")
            numeric = un.notna() & vn.notna()
            d = (un[numeric] - vn[numeric]).abs()
            ok_num = d <= (atol + rtol * vn[numeric].abs())
            nd += int((~ok_num).sum())
            if len(d):
                mx = max(mx, float(d.max()))
            rest = ~numeric
            same = (u[rest].astype(str) == v[rest].astype(str)) | (u[rest].isna() & v[rest].isna())
            nd += int((~same).sum())
            tot += len(u)
        rows.append({"aba": nome, "status": "IGUAL" if nd == 0 else "DIFERE", "celulas": tot, "diferentes": nd, "max_dif_abs": mx})
    extra = [s for s in b.sheet_names if s not in a.sheet_names]
    for s in extra:
        rows.append({"aba": s, "status": "NOVA (só na nova)", "celulas": None, "diferentes": None, "max_dif_abs": None})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ref")
    ap.add_argument("novo")
    ap.add_argument("--ignorar", nargs="*", default=["Config"])
    a = ap.parse_args()
    r = comparar(a.ref, a.novo, tuple(a.ignorar))
    pd.set_option("display.width", 200, "display.max_rows", 200)
    print(r.to_string(index=False))
