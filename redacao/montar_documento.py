"""Monta redacao/01_resultados_unificado.md a partir das tabelas do pipeline (as mesmas que alimentam a planilha final).

A prosa é escrita nos módulos sec_*.py; todo número e toda tabela vêm de funções que leem o cache (Store), de modo que o texto não depende de digitação. Depois de montar,
redacao/verificar_numeros.py confere cada número do texto contra as abas citadas em cada seção da planilha final.

Uso: python redacao/montar_documento.py resultados_final_<ts>.xlsx
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sec_1_3  # noqa: E402
import sec_4  # noqa: E402

SECOES = [sec_1_3.secao1, sec_1_3.secao2, sec_1_3.secao3, sec_4.secao4]

try:  # seções seguintes, adicionadas à medida que ficam prontas
    import sec_5_7  # noqa: E402
    SECOES += [sec_5_7.secao5, sec_5_7.secao6, sec_5_7.secao7]
except ImportError:
    pass
try:
    import sec_8_10  # noqa: E402
    SECOES += [sec_8_10.secao8, sec_8_10.secao9, sec_8_10.secao10]
except ImportError:
    pass

if __name__ == "__main__":
    xlsx = Path(sys.argv[1]).name
    cab = f"""# Resultados unificados (rascunho para a dissertação)

> **Planilha de apoio:** `{xlsx}`. Cada seção abre indicando as abas correspondentes (*Abas da planilha*). Todas as medidas são de associação, sem linguagem causal. O mapa tópico → aspecto do LDA e a segunda anotação foram confirmados pelo pesquisador. A organização por perguntas está em `00_enquadramento.md`.
"""
    texto = cab + "\n" + "\n".join(s() for s in SECOES)
    out = Path(__file__).resolve().parent / "01_resultados_unificado.md"
    out.write_text(texto, encoding="utf-8")
    print(out, len(texto), "caracteres;", len(SECOES), "seções")
