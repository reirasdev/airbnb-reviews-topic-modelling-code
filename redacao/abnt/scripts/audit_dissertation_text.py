#!/usr/bin/env python3
"""Triagem textual para dissertações.

Uso:
  python3 audit_dissertation_text.py texto.txt --json resultado.json

O script não declara conformidade ABNT. Ele localiza sinais que merecem revisão
manual em um PDF ou arquivo textual extraído, incluindo uma conciliação
heurística entre chamadas de citação no texto e entradas da lista de
referências. Autores institucionais citados por sigla (ex.: ABNT, IBGE),
"apud" e falhas de OCR geram falsos positivos: confirmar sempre no documento.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

YEAR = r"(?:1[6-9]|20)\d{2}[a-z]?"

SECTION_PATTERNS = {
    "resumo": r"(?im)^\s*resumo\s*$",
    "abstract": r"(?im)^\s*(abstract|summary)\s*$",
    "palavras-chave": r"(?im)^\s*(palavras[- ]chave|palavras-chave)\s*[:：]?",
    "keywords": r"(?im)^\s*keywords\s*[:：]?",
    "sumário": r"(?im)^\s*sum[áa]rio\s*$",
    "introdução": r"(?im)^\s*1[ .-]+introdu[çc][ãa]o\s*$|^\s*introdu[çc][ãa]o\s*$",
    "conclusão": r"(?im)^\s*(\d+[ .-]+)?(conclus[ãa]o|conclus[õo]es|considera[çc][õo]es\s+finais)\s*$",
    "referências": r"(?im)^\s*refer[êe]ncias(\s+bibliogr[áa]ficas)?\s*$",
}

PLACEHOLDER_PATTERNS = {
    "marcador TODO": r"(?i)\bTODO\b|\[\s*preencher\s*\]|\{\s*inserir\s*\}",
    "texto de exemplo": r"(?i)lorem ipsum|texto provis[óo]rio|a definir|nome do autor",
}

SUSPICIOUS_PATTERNS = {
    "ponto e vírgula entre autor e ano": r"\([A-ZÀ-Ý][^()\n]{0,80};\s*\d{4}[a-z]?",
    "et al. sem vírgula antes do ano": r"\bet al\.\s+\d{4}[a-z]?",
    "et al. com vírgula antes dele": r",\s*et al\.",
    "citação múltipla possivelmente separada por vírgula": r"\([^()\n]{2,100},\s+[A-ZÀ-Ý][^()\n]{2,60},\s*\d{4}",
}

# Palavras capitalizadas que antecedem parênteses com ano mas não são autores.
NARRATIVE_STOPWORDS = {
    "FIGURA", "TABELA", "QUADRO", "GRAFICO", "EQUACAO", "FONTE", "SECAO",
    "CAPITULO", "APENDICE", "ANEXO", "LEI", "DECRETO", "PORTARIA", "ART",
    "NBR", "NO", "NA", "EM", "DE", "DO", "DA", "O", "A", "E",
}


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def occurrences(text: str, pattern: str, limit: int = 20) -> list[dict]:
    hits = []
    for match in re.finditer(pattern, text):
        if len(hits) >= limit:
            break
        start = max(0, match.start() - 80)
        end = min(len(text), match.end() + 100)
        snippet = re.sub(r"\s+", " ", text[start:end]).strip()
        hits.append({"line": line_number(text, match.start()), "snippet": snippet})
    return hits


def strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def normalize_author(value: str) -> str:
    value = re.sub(r"(?i)\bet\s+al\.?", "", value)
    value = strip_accents(value).upper()
    value = re.sub(r"[^A-Z'\- ]", " ", value)
    value = re.sub(r"\s+", " ", value).strip(" -'")
    return value


def extract_citation_calls(text: str) -> list[dict]:
    """Extrai pares (autor, ano) de chamadas parentéticas e narrativas."""
    calls: list[dict] = []
    seen: set[tuple[str, str, int]] = set()

    def add(author: str, year: str, position: int) -> None:
        author = normalize_author(author)
        if not author or author in NARRATIVE_STOPWORDS:
            return
        key = (author, year, line_number(text, position))
        if key in seen:
            return
        seen.add(key)
        calls.append({"author": author, "year": year,
                      "line": line_number(text, position)})

    # Chamadas parentéticas: (SILVA, 2023), (SILVA; SOUZA, 2023, p. 10),
    # (SILVA et al., 2023), (BRASIL, 2020). Em "apud", considerar a obra
    # efetivamente consultada (a que vem depois do apud).
    for match in re.finditer(r"\(([^()\n]{2,200})\)", text):
        content = match.group(1)
        if not re.search(r"\b" + YEAR + r"\b", content):
            continue
        segment = content
        apud = re.search(r"(?i)\bapud\b", content)
        if apud:
            segment = content[apud.end():]
        head = re.split(r"[,;]", segment.strip(), maxsplit=1)[0]
        author_match = re.search(
            r"([A-ZÀ-Ý][\wÀ-ÿ'’\-]*(?:\s+(?:e|da|de|do|das|dos)\s+[\wÀ-ÿ'’\-]+|\s+[A-ZÀ-Ý][\wÀ-ÿ'’\-]*)*)\s*$",
            head.strip(),
        )
        year_match = re.search(r"\b" + YEAR + r"\b", segment) or re.search(
            r"\b" + YEAR + r"\b", content
        )
        if author_match and year_match:
            add(author_match.group(1), year_match.group(0), match.start())

    # Chamadas narrativas: Silva (2023), Silva et al. (2023, p. 5).
    for match in re.finditer(
        r"\b([A-ZÀ-Ý][\wÀ-ÿ'’\-]+(?:\s+et\s+al\.?)?)\s*\(\s*(" + YEAR + r")\b",
        text,
    ):
        add(match.group(1), match.group(2), match.start())

    return calls


def extract_reference_entries(text: str) -> tuple[list[dict], bool]:
    """Extrai (autor/entidade, ano) das entradas da lista de referências."""
    heading = re.search(SECTION_PATTERNS["referências"], text)
    if not heading:
        return [], False
    tail = text[heading.end():]
    stop = re.search(
        r"(?im)^\s*(gloss[áa]rio|ap[êe]ndices?\b|anexos?\b|[íi]ndice)\b", tail
    )
    block = tail[: stop.start()] if stop else tail

    entries: list[dict] = []
    current: list[str] = []
    current_line = 0
    offset = heading.end()

    def flush() -> None:
        if not current:
            return
        entry_text = " ".join(current)
        head = re.split(r"[,.]", entry_text, maxsplit=1)[0]
        year_match = re.search(r"\b" + YEAR + r"\b", entry_text)
        author = normalize_author(head)
        if author and year_match:
            entries.append({"author": author, "year": year_match.group(0),
                            "line": current_line})

    position = offset
    for raw_line in block.splitlines(keepends=True):
        line = raw_line.strip()
        if re.match(r"^[A-ZÀ-Ý][A-ZÀ-Ý'’\- ]{1,80}[,.]", line):
            flush()
            current = [line]
            current_line = line_number(text, position)
        elif line and current:
            current.append(line)
        position += len(raw_line)
    flush()
    return entries, True


def reconcile(calls: list[dict], entries: list[dict]) -> dict:
    def keys(items: list[dict]) -> set[tuple[str, str]]:
        result = set()
        for item in items:
            result.add((item["author"], item["year"]))
            result.add((item["author"], item["year"][:4]))
        return result

    entry_keys = keys(entries)
    call_keys = keys(calls)

    def unmatched(items: list[dict], other: set[tuple[str, str]]) -> list[dict]:
        missing, reported = [], set()
        for item in items:
            exact = (item["author"], item["year"])
            loose = (item["author"], item["year"][:4])
            if exact in other or loose in other:
                continue
            label = f"{item['author']} ({item['year']})"
            if label in reported:
                continue
            reported.add(label)
            missing.append({"call": label, "line": item["line"]})
        return missing

    return {
        "citações_sem_referência": unmatched(calls, entry_keys),
        "referências_sem_citação": unmatched(entries, call_keys),
    }


def audit(text: str) -> dict:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    findings = []

    sections = {}
    for name, pattern in SECTION_PATTERNS.items():
        hits = occurrences(text, pattern, limit=1)
        sections[name] = {"present": bool(hits), "locations": hits}
        if not hits:
            findings.append({
                "severity": "attention",
                "category": "estrutura",
                "issue": f"Seção não localizada: {name}",
                "recommendation": "Conferir se a seção existe com outro título ou se está ausente; validar contra o manual institucional.",
            })

    for issue, pattern in PLACEHOLDER_PATTERNS.items():
        hits = occurrences(text, pattern)
        if hits:
            findings.append({
                "severity": "high",
                "category": "revisão editorial",
                "issue": issue,
                "locations": hits,
                "recommendation": "Substituir ou remover o marcador antes de gerar a versão final.",
            })

    for issue, pattern in SUSPICIOUS_PATTERNS.items():
        hits = occurrences(text, pattern)
        if hits:
            findings.append({
                "severity": "attention",
                "category": "citações",
                "issue": issue,
                "locations": hits,
                "recommendation": "Inspecionar o trecho no PDF ou no arquivo editável e comparar com a NBR 10520:2023 e o manual do programa.",
            })

    available = len(re.findall(r"(?i)dispon[íi]vel\s+em\s*:", text))
    access = len(re.findall(r"(?i)acesso\s+em\s*:", text))
    if available > access:
        findings.append({
            "severity": "attention",
            "category": "referências",
            "issue": "Há mais ocorrências de 'Disponível em:' do que de 'Acesso em:'",
            "evidence": {"disponivel_em": available, "acesso_em": access},
            "recommendation": "Revisar as referências on-line segundo a NBR 6023:2025; não inserir datas sem confirmar a consulta real.",
        })

    calls = extract_citation_calls(text)
    entries, has_reference_list = extract_reference_entries(text)
    reconciliation = {"citações_sem_referência": [], "referências_sem_citação": []}
    if has_reference_list:
        reconciliation = reconcile(calls, entries)
        note = ("Conciliação heurística: confirmar manualmente conforme o passo 7 do SKILL.md. "
                "Falsos positivos comuns: entidade citada por sigla (ex.: ABNT, IBGE), "
                "'apud', sobrenomes compostos e falhas de OCR.")
        if reconciliation["citações_sem_referência"]:
            findings.append({
                "severity": "attention",
                "category": "referências",
                "issue": "Chamadas de citação sem entrada correspondente na lista de referências",
                "locations": reconciliation["citações_sem_referência"][:15],
                "recommendation": note,
            })
        if reconciliation["referências_sem_citação"]:
            findings.append({
                "severity": "attention",
                "category": "referências",
                "issue": "Entradas da lista de referências sem chamada localizada no texto",
                "locations": reconciliation["referências_sem_citação"][:15],
                "recommendation": note,
            })
    else:
        findings.append({
            "severity": "attention",
            "category": "referências",
            "issue": "Lista de referências não localizada; conciliação chamada ↔ referência não executada",
            "recommendation": "Conferir se a seção existe com outro título e repetir a triagem.",
        })

    distinct_years = sorted(set(re.findall(r"\b(?:1[6-9]|20)\d{2}\b", text)))
    return {
        "tool": "audit_dissertation_text",
        "warning": "Triagem automática; os achados precisam de confirmação visual e normativa.",
        "metrics": {
            "characters": len(text),
            "lines": text.count("\n") + 1,
            "distinct_year_tokens": len(distinct_years),
            "citation_calls_detected": len(calls),
            "reference_entries_detected": len(entries),
            "citacoes_sem_referencia": len(reconciliation["citações_sem_referência"]),
            "referencias_sem_citacao": len(reconciliation["referências_sem_citação"]),
            "disponivel_em": available,
            "acesso_em": access,
        },
        "sections": sections,
        "findings": findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Faz triagem textual de uma dissertação extraída.")
    parser.add_argument("input", type=Path, help="Arquivo .txt extraído do PDF ou do editor")
    parser.add_argument("--json", type=Path, help="Caminho do JSON de saída; se omitido, imprime no terminal")
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8", errors="replace")
    result = audit(text)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json:
        args.json.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
