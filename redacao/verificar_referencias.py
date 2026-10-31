#!/usr/bin/env python3
"""Confere as entradas do referencias.bib com DOI contra o Crossref (ano, volume, numero, paginas, similaridade do titulo).

Ideia inspirada em verificadores de BibTeX (por exemplo, bibverify); implementacao propria e minima, sem dependencias externas.
Nao altera o .bib: imprime as divergencias para decisao manual. Entradas sem DOI sao listadas ao final.
Uso (da raiz do repositorio):  python redacao/verificar_referencias.py [--contato seu@email]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BIB = Path(__file__).resolve().parent / "latex" / "referencias.bib"


def parse_bib(txt: str) -> dict[str, dict[str, str]]:
    out = {}
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", txt, re.S):
        campos = {"_tipo": m.group(1).lower()}
        for f in re.finditer(r"(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\}|\{(?:[^{}]|\{[^{}]*\})*\})*\}|\"[^\"]*\"|\d+)\s*,?", m.group(3), re.S):
            v = f.group(2).strip()
            campos[f.group(1).lower()] = v[1:-1] if v[0] in "{\"" else v
        out[m.group(2)] = campos
    return out


def limpa(s: str) -> str:
    s = re.sub(r"\\['`^\"~cu]\s*\{?(\w)\}?", r"\1", s)
    s = re.sub(r"[{}\\$]", "", s)
    s = re.sub(r"[^\w\s]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def jaccard(a: str, b: str) -> float:
    A, B = set(limpa(a).split()), set(limpa(b).split())
    return len(A & B) / max(1, len(A | B))


def crossref(doi: str, contato: str) -> dict | None:
    req = urllib.request.Request("https://api.crossref.org/works/" + urllib.parse.quote(doi), headers={"User-Agent": f"verificar_referencias (mailto:{contato})"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["message"]
    except urllib.error.HTTPError as e:
        return {"_erro": f"HTTP {e.code}"}
    except Exception as e:  # rede
        return {"_erro": str(e)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contato", default="contato@example.org")
    a = ap.parse_args()
    bib = parse_bib(BIB.read_text(encoding="utf-8"))
    sem_doi, problemas = [], 0
    for k, e in bib.items():
        doi = e.get("doi")
        if not doi:
            sem_doi.append(k)
            continue
        m = crossref(doi, a.contato)
        time.sleep(0.4)
        if not m or "_erro" in m:
            print(f"ERRO   {k}: {m and m['_erro']}")
            problemas += 1
            continue
        msgs = []
        ano = (m.get("issued", {}).get("date-parts") or [[None]])[0][0] or (m.get("published-print", {}).get("date-parts") or [[None]])[0][0]
        if ano and str(ano) != e.get("year"):
            msgs.append(f"ano bib={e.get('year')} crossref={ano}")
        if m.get("volume") and e.get("volume") and m["volume"] != e["volume"]:
            msgs.append(f"volume bib={e['volume']} crossref={m['volume']}")
        if m.get("issue") and e.get("number") and m["issue"] != e["number"]:
            msgs.append(f"numero bib={e['number']} crossref={m['issue']}")
        pg = (m.get("page") or m.get("article-number") or "").replace("–", "-")
        pb = e.get("pages", "").replace("--", "-")
        if pg and pb and pg != pb:
            msgs.append(f"paginas bib={pb} crossref={pg}")
        t = (m.get("title") or [""])[0] + (": " + m["subtitle"][0] if m.get("subtitle") else "")
        j = jaccard(t, e.get("title", ""))
        if j < 0.6:
            msgs.append(f"titulo (similaridade {j:.2f}) bib='{e.get('title', '')[:60]}' crossref='{t[:60]}'")
        if msgs:
            problemas += 1
            print(f"DIVERGE {k}: " + "; ".join(msgs))
        else:
            print(f"ok     {k}")
    print(f"\n{len(bib)} entradas; {len(sem_doi)} sem DOI ({', '.join(sem_doi)}); {problemas} com divergencia ou erro")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
