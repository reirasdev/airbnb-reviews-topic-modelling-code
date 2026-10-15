#!/usr/bin/env python3
"""Gera a dissertacao no formato do Guia de TCC da UCP (2023/2024) a partir dos capitulos em LaTeX (somente leitura).

Reaproveita as funcoes de leitura/conversao do gerador ABNT (../abnt/scripts/gerar_dissertacao.py, somente leitura, sem gravar bytecode)
e sobrepoe o que o Guia da UCP define de modo proprio: citacao autor-data com inicial maiuscula, referencias com 'In:' e 'et al.' em italico,
Introducao e Conclusao sem numero e centralizadas, secoes numeradas a partir de 1, capa, folha de rosto e folha de aprovacao.
Saida: ../saida/<nome>-UCP.docx
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
UCP = Path(__file__).resolve().parents[1]
REDACAO = UCP.parent
_spec = importlib.util.spec_from_file_location("gabnt", REDACAO / "abnt" / "scripts" / "gerar_dissertacao.py")
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)  # carrega funcoes; nao executa main()

from docx import Document  # noqa: E402  (python-docx vem de redacao/abnt/.libs, adicionado pelo modulo g)
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Cm, Pt, RGBColor  # noqa: E402

BS = chr(92)
SAIDA = UCP / "saida"
SAIDA.mkdir(exist_ok=True)
NOME = "Raphael_Eiras-Decomposicao_por_aspecto_do_sentimento_em_avaliacoes_do_airbnb_rj-ucp_2026-UCP"
BIB = g.BIB


# ----------------------------------------------------------------------------- citacoes (NBR 10520:2023, como no Guia da UCP)
def cite_p(keys: list[str]) -> str:
    itens = []
    for k in keys:
        i = g.info(k)
        f = i["fam"]
        txt = "; ".join(f) if len(f) <= 3 else f[0] + " et al."
        itens.append((g.norm(f[0]), i["year"], f"{txt}, {i['year']}"))
    itens.sort()
    return "(" + "; ".join(x[2] for x in itens) + ")"


g.cite_p = cite_p  # parse_inline procura cite_p no escopo do modulo g

# ----------------------------------------------------------------------------- referencias (NBR 6023, como no Guia da UCP)
CORR = {}  # sem correcoes locais: a base (referencias.bib) ja traz as paginas conferidas nos PDFs
EVENTOS = {
    "barbieri2022": ("CONFERENCE ON LANGUAGE RESOURCES AND EVALUATION, 13., 2022, Marseille", "Marseille: European Language Resources Association"),
    "devlin2019": ("CONFERENCE OF THE NORTH AMERICAN CHAPTER OF THE ASSOCIATION FOR COMPUTATIONAL LINGUISTICS: HUMAN LANGUAGE TECHNOLOGIES, 2019, Minneapolis", "[S. l.]: Association for Computational Linguistics"),
    "pontiki2014": ("INTERNATIONAL WORKSHOP ON SEMANTIC EVALUATION, 8., 2014, Dublin", "[S. l.]: [s. n.]"),
    "pontiki2016": ("INTERNATIONAL WORKSHOP ON SEMANTIC EVALUATION, 10., 2016, San Diego", "[S. l.]: Association for Computational Linguistics"),
    "reimers2019": ("CONFERENCE ON EMPIRICAL METHODS IN NATURAL LANGUAGE PROCESSING AND INTERNATIONAL JOINT CONFERENCE ON NATURAL LANGUAGE PROCESSING, 9., 2019, Hong Kong", "[S. l.]: Association for Computational Linguistics"),
    "reimers2020": ("CONFERENCE ON EMPIRICAL METHODS IN NATURAL LANGUAGE PROCESSING, 2020, [S. l.]", "[S. l.]: Association for Computational Linguistics"),
    "wolf2020": ("CONFERENCE ON EMPIRICAL METHODS IN NATURAL LANGUAGE PROCESSING: SYSTEM DEMONSTRATIONS, 2020, [S. l.]", "[S. l.]: Association for Computational Linguistics"),
    "roder2015": ("ACM INTERNATIONAL CONFERENCE ON WEB SEARCH AND DATA MINING, 8., 2015, Shanghai", "[S. l.]: [s. n.]"),
    "freitas2013": ("INTERNATIONAL CONFERENCE ON WORLD WIDE WEB, 22., 2013, [S. l.]", "[S. l.]: [s. n.]"),
    "giritli2026": ("IEEE ANNUAL COMPUTERS, SOFTWARE, AND APPLICATIONS CONFERENCE (COMPSAC), 50., 2026, [S. l.]", "[S. l.]: IEEE"),
}
DOCUMENTO = {"devlin2019": "Proceedings", "pontiki2014": "Proceedings", "pontiki2016": "Proceedings", "reimers2019": "Proceedings", "reimers2020": "Proceedings",
             "wolf2020": "Proceedings", "barbieri2022": "Proceedings", "roder2015": "Proceedings", "freitas2013": "Proceedings",
             "giritli2026": "Proceedings"}


def autores(au) -> list[tuple[str, str]]:
    def um(a):
        fam, giv, inst = a
        return fam.upper() if inst else (f"{fam.upper()}, {giv}" if giv else fam.upper())

    if len(au) > 3:
        return [(um(au[0]) + " ", ""), ("et al.", "i")]
    return [("; ".join(um(a) for a in au), ""), (".", "")] if not um(au[-1]).endswith(".") else [("; ".join(um(a) for a in au), "")]


def ref_ucp(key: str) -> list[tuple[str, str]]:
    e = {**BIB[key], **g.OVERRIDES.get(key, {}), **CORR.get(key, {})}
    t = e["_type"]
    au = g.split_authors(e.get("author", ""))
    A = autores(au)
    title = g.TITULOS.get(key, g.tex2uni(e.get("title", "")))
    yr = e["year"]
    doi, url = e.get("doi"), e.get("url")
    web = f" Disponível em: {url}. Acesso em: {g.ACESSO}."
    if t == "article":
        jn = g.tex2uni(e["journal"])
        if jn.lower().startswith("arxiv"):
            return A + [(f" {g.fin(title)} [S. l.]: arXiv, {yr}.{web}", "")]
        tail = ""  # NBR 6023: artigo de periodico nao leva local de publicacao
        if e.get("volume"):
            tail += f", v. {e['volume']}"
        if e.get("number"):
            tail += f", n. {e['number']}"
        if e.get("pages"):
            tail += f", p. {g.pags(e['pages'])}"
        elif e.get("pendente"):
            tail += f", [PENDENTE: {g.tex2uni(e['pendente']).replace('--', '–')}]"
        tail += f", {yr}."
        tail += f" DOI: {doi}." if doi else (web if url else "")
        return A + [(f" {g.fin(title)} ", ""), (jn, "b"), (tail, "")]
    if t == "inproceedings":
        evento, editora = EVENTOS[key]
        tail = f". {DOCUMENTO[key]} [...]. {editora}, {yr}."
        if e.get("pages"):
            tail += f" p. {g.pags(e['pages'])}."
        tail += f" DOI: {doi}." if doi else (web if url else "")
        return A + [(f" {g.fin(title)} ", ""), ("In", "i"), (": ", ""), (evento, "b"), (tail, "")]
    if t == "mastersthesis":
        univ, _, unidade = g.tex2uni(e["school"]).partition(", ")
        return A + [(" ", ""), (title, "b"), (f". {yr}. Dissertação (Mestrado) – {unidade}, {univ}, {g.tex2uni(e.get('address', 'Campinas'))}, {yr}. DOI: {doi}.", "")]
    if t == "book":
        loc = g.tex2uni(e.get("address", "")) or "[S. l.]"
        pub = g.tex2uni(e.get("publisher", "")) or "[s. n.]"
        serie = f" ({g.tex2uni(e['series'])})" if e.get("series") else ""
        tail = f". {loc}: {pub}, {yr}.{serie}" + (f" DOI: {doi}." if doi else "")
        return A + [(" ", ""), (title, "b"), (tail, "")]
    if t == "misc":
        how = g.tex2uni(e.get("howpublished", ""))
        return A + [(" ", ""), (title, "b"), (f". [S. l.], {yr}. Disponível em: {how}. Acesso em: {g.ACESSO}.", "")]
    return A + [(f" {title}. {yr}.", "")]


# ----------------------------------------------------------------------------- numeracao das secoes (Introducao e Conclusao sem numero)
MAPA = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7}


def remap(s: str) -> str:
    s = s.replace("O texto está organizado em nove seções, seguidas de apêndices.", "O texto está organizado em Introdução, sete seções numeradas, Conclusões e apêndices.")
    s = s.replace("e a Seção 9 apresenta as conclusões", "e as Conclusões encerram o trabalho")

    def um(m):
        n = int(m.group(2))
        return f"{m.group(1)} {MAPA[n]}{m.group(3) or ''}"

    s = re.sub(r"(Seção) (\d+)(\.\d+)?", um, s)
    s = re.sub(r"Seções (\d+) a (\d+)", lambda m: f"Seções {MAPA[int(m.group(1))]} a {MAPA[int(m.group(2))]}", s)
    return s


def centraliza(p):
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def runs_texto(par, partes, size=None):
    for texto, fmt in partes:
        r = par.add_run(texto)
        if fmt == "b":
            r.bold = True
        if fmt == "i":
            r.italic = True
        if size:
            r.font.size = Pt(size)


FIGURAS = REDACAO / "figuras" / "saida"

# Lista de abreviaturas e siglas (so as que aparecem no texto)
SIGLAS = [
    ("ABSA", "Aspect-Based Sentiment Analysis (análise de sentimento por aspecto)"),
    ("AUC", "Area Under the Curve (área sob a curva ROC)"),
    ("BERT", "Bidirectional Encoder Representations from Transformers"),
    ("BERTopic", "modelagem de tópicos baseada em representações do BERT"),
    ("BH", "correção de Benjamini e Hochberg para comparações múltiplas"),
    ("CAPES", "Coordenação de Aperfeiçoamento de Pessoal de Nível Superior"),
    ("CC BY", "licença Creative Commons Atribuição"),
    ("CPU", "Central Processing Unit (unidade central de processamento)"),
    ("GBM", "Gradient Boosting Machine (modelo de árvores com gradiente)"),
    ("GPU", "Graphics Processing Unit (unidade de processamento gráfico)"),
    ("HC3", "estimador de variância robusta à heterocedasticidade, tipo 3"),
    ("HDBSCAN", "Hierarchical Density-Based Spatial Clustering of Applications with Noise"),
    ("HTML", "HyperText Markup Language"),
    ("IC", "intervalo de confiança"),
    ("LDA", "Latent Dirichlet Allocation (alocação latente de Dirichlet)"),
    ("LGPD", "Lei Geral de Proteção de Dados Pessoais"),
    ("LLM", "Large Language Model (grande modelo de linguagem)"),
    ("LMG", "decomposição de Lindeman, Merenda e Gold (média de Shapley do R²)"),
    ("PLN", "processamento de linguagem natural"),
    ("PPG", "programa de pós-graduação"),
    ("UCP", "Universidade Católica de Petrópolis"),
    ("UMAP", "Uniform Manifold Approximation and Projection"),
    ("URL", "Uniform Resource Locator (endereço eletrônico)"),
    ("UTC", "Tempo Universal Coordenado"),
]


def build_figure(doc, anchor, fg: dict, num: int):
    """Figura: 'Figura N – titulo' acima, imagem centralizada, 'Fonte: Elaborada pelo autor.' abaixo (Guia da UCP, p. 36)."""
    cp = anchor.insert_paragraph_before("", style="Caption")
    cp.paragraph_format.keep_with_next = True
    cp.paragraph_format.space_before = Pt(6)
    cp.paragraph_format.space_after = Pt(4)
    cp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = cp.add_run("Figura ")
    r.font.size = Pt(10)
    g.field_runs(cp, "SEQ Figura \\* ARABIC", str(num), 10)
    g.add_runs(cp, [(" – ", {})] + g.parse_inline(remap(fg["caption"])), size=10)
    for r in cp.runs:
        r.bold = False
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0, 0, 0)
    ip = anchor.insert_paragraph_before("")
    ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ip.paragraph_format.first_line_indent = Cm(0)
    ip.paragraph_format.line_spacing = 1.0
    ip.paragraph_format.keep_with_next = True
    from PIL import Image

    arq = FIGURAS / (fg["arquivo"] + ".png")
    w_px, h_px = Image.open(arq).size
    larg = 16.0 * fg["largura"]
    alt = larg * h_px / w_px
    if alt > 21.5:  # cabe na pagina com a legenda e a fonte
        larg, alt = larg * 21.5 / alt, 21.5
    ip.add_run().add_picture(str(arq), width=Cm(larg))
    fp = anchor.insert_paragraph_before("")
    fp.paragraph_format.space_before = Pt(3)
    fp.paragraph_format.space_after = Pt(12)
    fp.paragraph_format.line_spacing = 1.0
    fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fp.paragraph_format.first_line_indent = Cm(0)
    fp.add_run("Fonte: Elaborada pelo autor.").font.size = Pt(10)


def destacar_pendentes(doc) -> int:
    """Marca em amarelo cada trecho '[PENDENTE: ...]' (corpo, tabelas e referencias)."""
    import copy

    from docx.enum.text import WD_COLOR_INDEX

    padrao = re.compile(r"(\[PENDENTE:[^\]]*\])")
    n = 0

    def pars(parent):
        yield from parent.paragraphs
        for t in getattr(parent, "tables", []):
            for row in t.rows:
                for cell in row.cells:
                    yield from pars(cell)

    for p in pars(doc):
        for run in list(p.runs):
            if "[PENDENTE" not in run.text:
                continue
            partes = [x for x in padrao.split(run.text) if x]
            ref = run._r
            for parte in partes:
                novo = copy.deepcopy(ref)
                for t in novo.findall(qn("w:t")):
                    novo.remove(t)
                ref.addprevious(novo)
                from docx.text.run import Run

                r2 = Run(novo, p)
                r2.text = parte
                if padrao.fullmatch(parte):
                    r2.font.highlight_color = WD_COLOR_INDEX.YELLOW
                    n += 1
            ref.getparent().remove(ref)
    return n


def main():
    CAPS = g.CAPS
    k = 0
    kf = 0
    for c in CAPS:
        for kind, val in g.table_blocks(c.read_text(encoding="utf-8")):
            if kind == "table":
                k += 1
                g.LABELS[val["label"]] = k
            elif kind == "figure":
                kf += 1
                g.LABELS[val["label"]] = kf
    resumo = g.parse_inline(g.strip_comments((g.LATEX / "capitulos" / "resumo.tex").read_text(encoding="utf-8")).strip().replace("\n", " "))
    autor = "Raphael Rodrigues Eiras"
    orient = "Prof. Dr. Rodolfo Nicolay"
    centro = "Centro de Engenharia e Computação"
    curso = "Mestrado Profissional em Gestão de Sistemas de Engenharia"
    natureza = (f"Dissertação apresentada ao {centro} da Universidade Católica de Petrópolis (UCP), como requisito parcial "
                f"para obtenção do título de Mestre em Gestão de Sistemas de Engenharia.")
    titulo = "O que as avaliações revelam sobre a nota"
    subtitulo = "decomposição por aspecto do sentimento em avaliações de hóspedes do Airbnb no Rio de Janeiro"
    palavras = "análise de sentimento por aspecto; avaliações online; Airbnb; modelagem de tópicos; diagnóstico de anúncios"
    abstract = (
        "Ratings on Airbnb are concentrated at the top of the scale and say little about the reasons for guest satisfaction. "
        "This study uses the text of 995,072 reviews of listings in Rio de Janeiro (Inside Airbnb) to decompose the rating by aspect and by specific complaint. "
        "Sentence-level sentiment is measured by two multilingual models, and the choice of the main model follows a rule fixed before the second model was run. "
        "Aspects come from topics obtained with BERTopic and are checked with a second method (LDA) and with a second annotator. "
        "The measurement is validated with the official subscores and with labeled sentences weighted by the population. "
        "Only cleanliness, location and value meet the adopted confidence criterion. "
        "Amenities and cleanliness concentrate most of the explained variation of the overall rating. "
        "Complaints about facilities, cleanliness and host response are the most associated with lower ratings, with a similar order in both models. "
        "A synthetic index built from the text adds no explanatory power, beyond the official rating, over indices of review volume. "
        "The results are associations, and the proposed application is a listing-level diagnosis compared with the neighborhood and the type of accommodation."
    )
    keywords = "aspect-based sentiment analysis; online reviews; Airbnb; topic modeling; listing diagnosis"

    doc = Document(str(REDACAO / "abnt" / "templates" / "template-dissertacao-abnt.docx"))
    P = list(doc.paragraphs)

    def tit(p, normal_case_author=False):
        p.clear()
        p.add_run(titulo.upper())
        r2 = p.add_run(": " + subtitulo)
        r2.font.bold = False
        r2.font.all_caps = False

    def autor_par(p):
        p.clear()
        r = p.add_run(autor)
        r.font.all_caps = False
        r.font.bold = False

    # capa: instituicao, centro, curso, autor, titulo, local, ano
    g.set_par_text(P[0], "UNIVERSIDADE CATÓLICA DE PETRÓPOLIS")
    g.set_par_text(P[1], centro.upper())
    g.set_par_text(P[2], curso.upper())
    autor_par(P[3])
    tit(P[4])
    g.set_par_text(P[5], "Petrópolis")
    g.set_par_text(P[6], "2026")
    # folha de rosto
    autor_par(P[8])
    tit(P[9])
    P[10].clear()
    P[10].add_run(natureza).font.size = Pt(10)
    P[11].clear()
    P[11].add_run(f"Orientador: {orient}").font.size = Pt(10)
    g.remove(P[12])
    g.set_par_text(P[13], "Petrópolis")
    P[13].paragraph_format.space_before = Pt(200)  # local e ano no pe da folha de rosto
    g.set_par_text(P[14], "2026")
    # folha de aprovacao: autor, titulo, natureza, orientador, nota, data, banca
    autor_par(P[19])
    tit(P[20])
    P[21].clear()
    P[21].add_run(natureza).font.size = Pt(10)
    for idx in range(22, 30):
        g.remove(P[idx])
    ancora = P[30]  # quebra de pagina antes dos agradecimentos
    linha = "_" * 60

    def corpo(txt, bold=False, centro_=True):
        p = ancora.insert_paragraph_before("", style="Corpo do texto")
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(6)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if centro_ else WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run(txt)
        r.bold = bold
        return p

    corpo("")
    corpo(linha)
    corpo(f"({orient} – orientador)")
    corpo("")
    corpo("Nota: [a definir pela banca]", centro_=False)
    corpo("Aprovado em: [dia] de [mês] de [ano].", centro_=False)
    corpo("BANCA EXAMINADORA:", bold=True, centro_=False)
    for _ in range(3):
        corpo("")
        corpo(linha)
        corpo("([Nome completo, titulação e instituição a que pertence])")
    # agradecimentos (opcional): removidos
    for idx in (31, 32, 33):
        g.remove(P[idx])
    # resumo / abstract
    p = P[35]
    p.clear()
    p.paragraph_format.first_line_indent = Cm(0)
    g.add_runs(p, resumo)
    g.set_par_text(P[36], f"Palavras-chave: {palavras}.")
    P[36].paragraph_format.first_line_indent = Cm(0)
    P[39].clear()
    P[39].paragraph_format.first_line_indent = Cm(0)
    P[39].add_run(abstract)
    g.set_par_text(P[40], f"Keywords: {keywords}.")
    P[40].paragraph_format.first_line_indent = Cm(0)
    # lista de figuras (antes da lista de tabelas)
    anchor = P[41]
    tf = anchor.insert_paragraph_before("LISTA DE FIGURAS", style="Título não numerado")
    lf = anchor.insert_paragraph_before("")
    lf.paragraph_format.first_line_indent = Cm(0)
    lf.paragraph_format.line_spacing = 1.0
    titulos_f = []
    for c in CAPS:
        for kind, val in g.table_blocks(c.read_text(encoding="utf-8")):
            if kind == "figure":
                titulos_f.append("".join(t for t, _ in g.parse_inline(remap(val["caption"]))))
    g.field_runs(lf, 'TOC \\h \\z \\c "Figura"', "\n".join(f"Figura {n} – {t}" for n, t in enumerate(titulos_f, 1)), 11)
    g.page_break_par(tf)
    # lista de tabelas
    tt = anchor.insert_paragraph_before("LISTA DE TABELAS", style="Título não numerado")
    lt = anchor.insert_paragraph_before("")
    lt.paragraph_format.first_line_indent = Cm(0)
    lt.paragraph_format.line_spacing = 1.0
    titulos = []
    for c in CAPS:
        for kind, val in g.table_blocks(c.read_text(encoding="utf-8")):
            if kind == "table":
                titulos.append("".join(t for t, _ in g.parse_inline(remap(val["caption"]))))
    g.field_runs(lt, 'TOC \\h \\z \\c "Tabela"', "\n".join(f"Tabela {n} – {t}" for n, t in enumerate(titulos, 1)), 11)
    g.page_break_par(tt)
    # lista de abreviaturas e siglas
    ts = anchor.insert_paragraph_before("LISTA DE ABREVIATURAS E SIGLAS", style="Título não numerado")
    for sigla, significado in SIGLAS:
        ps = anchor.insert_paragraph_before("")
        ps.paragraph_format.first_line_indent = Cm(0)
        ps.paragraph_format.line_spacing = 1.0
        ps.paragraph_format.space_after = Pt(4)
        ps.paragraph_format.left_indent = Cm(3)
        ps.paragraph_format.first_line_indent = Cm(-3)
        ps.add_run(sigla).bold = True
        ps.add_run("\t" + significado)
        ps.paragraph_format.tab_stops.add_tab_stop(Cm(3))
    g.page_break_par(ts)
    # corpo
    ref_titulo = P[56]
    for idx in range(45, 56):
        g.remove(P[idx])
    h1 = h2 = tnum = fnum = 0
    em_apendice = False
    apend = []  # blocos dos apendices: entram depois das referencias
    for c in CAPS:
        for kind, val in g.table_blocks(c.read_text(encoding="utf-8")):
            if kind == "appendix":
                em_apendice = True
                continue
            if em_apendice:
                apend.append((kind, val))
                continue
            if kind == "h1":
                if val.upper() in ("INTRODUÇÃO", "CONCLUSÕES"):
                    centraliza(ref_titulo.insert_paragraph_before(val.upper(), style="Heading 1"))
                    h1_atual = None
                else:
                    h1 += 1
                    h2 = 0
                    ref_titulo.insert_paragraph_before(f"{h1} {val.upper()}", style="Heading 1")
            elif kind == "h2":
                h2 += 1
                ref_titulo.insert_paragraph_before(f"{h1}.{h2} {val.upper()}", style="Heading 2")
            elif kind == "p":
                par = ref_titulo.insert_paragraph_before("", style="Corpo do texto")
                g.add_runs(par, g.parse_inline(remap(val)))
            elif kind == "figure":
                fnum += 1
                build_figure(doc, ref_titulo, val, fnum)
            else:
                tnum += 1
                val = {**val, "caption": remap(val["caption"]), "rows": remap(val["rows"])}
                g.build_table(doc, ref_titulo, val, tnum)
    # referencias (titulo no sumario, centralizado)
    ref_titulo.style = doc.styles["Heading 1"]
    centraliza(ref_titulo)
    chaves = sorted(BIB, key=lambda k: (g.norm(g.info(k)["fam"][0]), g.info(k)["year"], g.norm(BIB[k].get("title", ""))))
    apendice = P[59]
    for k in chaves:
        par = apendice.insert_paragraph_before("", style="Referência")
        runs_texto(par, ref_ucp(k))
    for idx in (57, 58, 59, 60):
        g.remove(P[idx])
    # apendices (depois das referencias); o ultimo, com a tabela larga, em pagina paisagem
    if apend:
        from docx.enum.section import WD_ORIENT, WD_SECTION

        fim = doc.add_paragraph("")
        letra = -1
        for kind, val in apend:
            if kind == "h1":
                letra += 1
                if "TABELA COMPLETA" in val.upper():
                    g.remove(fim)
                    sec = doc.add_section(WD_SECTION.NEW_PAGE)
                    sec.orientation = WD_ORIENT.LANDSCAPE
                    sec.page_width, sec.page_height = sec.page_height, sec.page_width
                    sec.left_margin, sec.top_margin, sec.right_margin, sec.bottom_margin = Cm(3), Cm(3), Cm(2), Cm(2)
                    paisagem = True
                    anchor_ap = doc.add_paragraph("")
                    fim = anchor_ap
                ph = fim.insert_paragraph_before("", style="Heading 1")
                g.add_runs(ph, [(f"APÊNDICE {chr(65 + letra)} – ", {})] + [(t.upper(), st) for t, st in g.parse_inline(val)])
                centraliza(ph)
            elif kind == "p":
                par = fim.insert_paragraph_before("", style="Corpo do texto")
                g.add_runs(par, g.parse_inline(remap(val)))
            elif kind == "figure":
                fnum += 1
                build_figure(doc, fim, val, fnum)
            elif kind == "table":
                tnum += 1
                val = {**val, "caption": remap(val["caption"]), "rows": remap(val["rows"])}
                g.build_table(doc, fim, val, tnum, larg_cm=(24.7 if doc.sections[-1].orientation == WD_ORIENT.LANDSCAPE else 16.0))
        g.remove(fim)
    # paginacao: tamanho 10, a 2 cm da borda superior
    doc.sections[1].header_distance = Cm(2)
    doc.styles["Header"].font.size = Pt(10)
    g.forcar_times(doc)
    npend = destacar_pendentes(doc)
    out = SAIDA / (NOME + ".docx")
    doc.save(str(out))
    print("salvo:", out, "| tabelas:", tnum, "| figuras:", fnum, "| secoes numeradas:", h1, "| referencias:", len(chaves), "| marcadores PENDENTE:", npend)


if __name__ == "__main__":
    main()
