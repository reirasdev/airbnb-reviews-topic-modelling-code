"""Confere cada número de um rascunho (.md) contra as abas da planilha de resultados CITADAS NA PRÓPRIA SEÇÃO.

Uso: python redacao/verificar_numeros.py redacao/01_resultados_unificado.md outputs/resultados_final_<ts>.xlsx

Regras:
- Cada seção (## ou ###) deve ter uma linha "*Abas da planilha:* `Aba1`, `Aba2` ..."; seções sem essa linha herdam a da seção-mãe. Um número só é considerado verificado se existir (arredondado ao mesmo
  número de casas; com ×100 para percentuais; em valor absoluto) em uma célula numérica (ou em um número dentro de uma célula de texto, como o Resumo_Log) de uma das abas citadas,
  de suas variantes de modelo (sufixos _mA/_mB) ou das abas Config/Estat_Corpus. Isso evita coincidências com os milhares de outros valores da planilha.
- Ignora trechos de código (`...`), datas, anos, numeração de seções/itens e inteiros de um dígito.
- Imprime os NÃO localizados com a seção e a linha; devem ser conferidos à mão (derivados, constantes ou erros).
"""
from __future__ import annotations

import re
import sys

import numpy as np
import pandas as pd

NUM = re.compile(r"(?<![\w.])[+\-−–]?\d{1,3}(?:\.\d{3})+(?:,\d+)?%?|(?<![\w.])[+\-−–]?\d+,\d+%?|(?<![\w.,])[+\-−–]?\d+%?(?![\w])")
CELL_NUM = re.compile(r"-?\d+(?:\.\d+)?(?:e-?\d+)?", re.I)
SEMPRE = ("Config", "Estat_Corpus")


def valores_por_aba(path: str) -> dict[str, np.ndarray]:
    out = {}
    for nome, df in pd.read_excel(path, sheet_name=None, header=None).items():
        vals = []
        for x in df.to_numpy().ravel():
            if isinstance(x, (int, float, np.integer, np.floating)) and not (isinstance(x, float) and np.isnan(x)):
                vals.append(float(x))
            elif isinstance(x, str) and len(x) < 6000:
                vals += [float(m) for m in CELL_NUM.findall(x) if len(m) < 18]
        v = np.unique(np.abs(np.array(vals, dtype=float)))
        out[nome] = v[np.isfinite(v)]
    return out


def limpar(ln: str) -> str:
    ln = re.sub(r"^\s*#+\s*[\d.]*\s*", "", ln)
    ln = re.sub(r"`[^`]*`", " ", ln)
    ln = re.sub(r"\[[^\]]*\]\([^)]*\)", " ", ln)
    ln = re.sub(r"\d{4}-\d{2}-\d{2}", " ", ln)
    ln = re.sub(r"(?<!\d)(19|20)\d{2}(?!\d)", " ", ln)
    ln = re.sub(r"(?i)seções?\s+[\d.,e ]+|tabela\s+\d+|item\s+[\d.]+|\b\d\.\d+(\.\d+)?\b(?=\s*[—\-:)]|\s*$)", " ", ln)
    return ln


def parse(tok: str) -> tuple[float, int, bool]:
    t = tok.replace("−", "-").replace("–", "-").lstrip("+").lstrip("-")
    pct = t.endswith("%")
    t = t.rstrip("%")
    d = len(t.split(",")[1]) if "," in t else 0
    return float(t.replace(".", "").replace(",", ".")), d, pct


def achar(v: float, d: int, pct: bool, base: np.ndarray) -> bool:
    tol = 0.5 * 10 ** (-d) * 1.0000001
    cands = [(v / 100, tol / 100), (v, tol)] if pct else [(v, tol)]  # "87%" pode estar gravado como 0,87 ou 87
    for alvo, lim in cands:
        i = np.searchsorted(base, alvo - lim)
        if i < len(base) and base[i] <= alvo + lim:
            return True
    return False


def main(md: str, xlsx: str) -> None:
    abas = valores_por_aba(xlsx)
    nomes = list(abas)
    secao, abas_secao, pilha = "(início)", [], {}
    nao, total = [], 0
    for i, ln in enumerate(open(md, encoding="utf-8").read().split("\n"), 1):
        h = re.match(r"^(#+)\s+(.*)", ln)
        if h:
            nivel = len(h.group(1))
            secao = h.group(2)[:60]
            abas_secao = pilha.get(nivel - 1, pilha.get(max(pilha, default=0), [])) if nivel > 1 else []
            pilha = {k: v for k, v in pilha.items() if k < nivel}
            pilha[nivel] = abas_secao
            continue
        m = re.search(r"\*Abas da planilha:\*(.*)", ln)
        if m:
            cit = re.findall(r"`([^`]+)`", m.group(1))
            abas_secao = [n for n in nomes if any(n == c or n.startswith(c + "_m") for c in cit)]
            pilha[max(pilha, default=1)] = abas_secao
            continue
        uso = set(abas_secao) | {n for n in nomes if n in SEMPRE}
        base = np.unique(np.concatenate([abas[n] for n in uso])) if uso else np.array([])
        for mm in NUM.finditer(limpar(ln)):
            tok = mm.group(0)
            v, d, pct = parse(tok)
            if d == 0 and not pct and v < 10 and "," not in tok and "." not in tok:
                continue
            total += 1
            if not len(base) or not achar(v, d, pct, base):
                nao.append((i, secao, tok, ln.strip()[:150]))
    print(f"{total} números conferidos; {len(nao)} não localizados nas abas citadas.")
    for i, sec, tok, ln in nao:
        print(f"  l.{i:4d} [{sec[:28]:28s}] {tok:>12s} | {ln}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
