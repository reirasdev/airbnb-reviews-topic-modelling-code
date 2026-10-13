"""Converte um arquivo Markdown de redacao/ em PDF (HTML formatado + Edge/Chrome em modo oculto).
Uso: python redacao/gerar_pdf.py redacao/01_resultados.md
"""
from __future__ import annotations

import subprocess
import tempfile
import sys
from pathlib import Path

import markdown

CSS = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; line-height: 1.45; color: #1b1b1b; }
h1 { font-size: 19pt; margin: 0 0 8pt 0; border-bottom: 2px solid #333; padding-bottom: 4pt; }
h2 { font-size: 14pt; margin-top: 20pt; border-bottom: 1px solid #bbb; padding-bottom: 2pt; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin-top: 14pt; page-break-after: avoid; }
p, li { text-align: justify; }
blockquote { margin: 8pt 0; padding: 6pt 10pt; background: #f4f4f4; border-left: 3px solid #999; color: #333; font-size: 9.5pt; }
table { border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 8.8pt; page-break-inside: avoid; }
th, td { border: 1px solid #c8c8c8; padding: 3pt 5pt; vertical-align: top; }
th { background: #eeeeee; text-align: left; }
td:not(:first-child) { text-align: right; }
td:first-child, th:first-child { text-align: left; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f1f1f1; padding: 0 2pt; }
"""


def main(md_path: str) -> Path:
    src = Path(md_path)
    html = markdown.markdown(src.read_text(encoding="utf-8"), extensions=["tables", "sane_lists"])
    out_html = src.with_suffix(".html")
    out_html.write_text(f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{src.stem}</title><style>{CSS}</style></head><body>{html}</body></html>',
                        encoding="utf-8")
    pdf = src.with_suffix(".pdf")
    for exe in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
        if Path(exe).exists():
            subprocess.run([exe, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={tempfile.mkdtemp()}", f"--print-to-pdf={pdf.resolve()}", out_html.resolve().as_uri()],
                           check=True, timeout=120, capture_output=True)
            out_html.unlink()
            return pdf
    raise SystemExit("Edge/Chrome não encontrado")


if __name__ == "__main__":
    print(main(sys.argv[1]))
