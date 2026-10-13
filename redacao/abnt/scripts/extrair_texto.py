#!/usr/bin/env python3
"""Extrai o texto do DOCX gerado (paragrafos e tabelas, na ordem) para triagem com audit_dissertation_text.py."""
import sys
from pathlib import Path

ABNT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ABNT / ".libs"))
from docx import Document  # noqa: E402
from docx.table import Table  # noqa: E402
from docx.text.paragraph import Paragraph  # noqa: E402

d = Document(str(ABNT / "saida" / "Raphael_Eiras-Decomposicao_por_aspecto_do_sentimento_em_avaliacoes_do_airbnb_rj-ucp_2026-ABNT.docx"))
out = []
for el in d.element.body.iterchildren():
    tag = el.tag.split("}")[1]
    if tag == "p":
        out.append(Paragraph(el, d).text)
    elif tag == "tbl":
        for row in Table(el, d).rows:
            out.append(" | ".join(c.text.strip() for c in row.cells))
(ABNT / "saida" / "texto_extraido.txt").write_text("\n".join(out), encoding="utf-8")
print(len(out), "linhas")
