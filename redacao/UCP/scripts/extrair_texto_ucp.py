#!/usr/bin/env python3
"""Extrai o texto do DOCX da versao UCP (paragrafos e tabelas, na ordem) para conferencia."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
UCP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UCP.parent / "abnt" / ".libs"))
from docx import Document  # noqa: E402
from docx.table import Table  # noqa: E402
from docx.text.paragraph import Paragraph  # noqa: E402

arq = next((UCP / "saida").glob("*-UCP.docx"))
d = Document(str(arq))
out = []
for el in d.element.body.iterchildren():
    tag = el.tag.split("}")[1]
    if tag == "p":
        out.append(Paragraph(el, d).text)
    elif tag == "tbl":
        for row in Table(el, d).rows:
            out.append(" | ".join(c.text.strip() for c in row.cells))
(UCP / "saida" / "texto_extraido.txt").write_text("\n".join(out), encoding="utf-8")
print(arq.name, len(out), "linhas")
