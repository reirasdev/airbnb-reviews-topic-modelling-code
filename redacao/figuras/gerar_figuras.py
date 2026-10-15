#!/usr/bin/env python3
"""Figuras da dissertacao (ajustes do orientador, F1). Le somente as abas/tabelas *_v2 geradas por `ajustes_v2.py`
(outputs/ajustes_v2/*.parquet, iguais as abas Fig*_v2 da planilha) e os relatorios anonimizados de outputs/diagnosticos.
Saida: redacao/figuras/saida/figura_N.pdf (vetorial) e figura_N.png (300 dpi). Sem titulo dentro da imagem (a legenda fica no texto).

Uso (Python do sistema, com matplotlib e pyarrow), a partir de qualquer pasta:
    python redacao/figuras/gerar_figuras.py            # figuras 1 a 4
    python redacao/figuras/gerar_figuras.py --relatorios  # figura 5 e apendice: renderiza os HTML anonimizados (usa o Edge em modo headless)
"""
from __future__ import annotations

import argparse
import subprocess
import time
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

EDGE = next((Path(x) for x in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe") if Path(x).exists()), Path("msedge"))
AQUI = Path(__file__).resolve().parent
REPO = AQUI.parents[1]
DADOS = REPO / "outputs" / "ajustes_v2"
SAIDA = AQUI / "saida"
SAIDA.mkdir(exist_ok=True)

AZUL, CINZA, LARANJA, CLARO, TEXTO = "#1F4E79", "#9A9A9A", "#C55A11", "#DCE6F1", "#222222"
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"], "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#555555", "axes.linewidth": 0.6,
                     "mathtext.fontset": "stix", "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"})
NOME = {"limpeza": "Limpeza", "localizacao": "Localização", "checkin": "Check-in", "comunicacao": "Comunicação", "custo_beneficio": "Custo-benefício",
        "ruido_conforto": "Ruído e conforto", "seguranca": "Segurança", "precisao": "Precisão do anúncio", "comodidades": "Comodidades", "satisfacao_geral": "Satisfação geral"}


def pt(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def salvar(fig, n):
    fig.savefig(SAIDA / f"figura_{n}.pdf", bbox_inches="tight")
    fig.savefig(SAIDA / f"figura_{n}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("figura", n)


def lido(nome):
    return pd.read_parquet(DADOS / f"{nome}.parquet")


# ------------------------------------------------------------------------------------------------ 1. pipeline
def fig1():
    n = lido("Fig1_numeros_v2").set_index("metrica")["valor"]
    f = lambda k: f"{int(n[k]):,}".replace(",", ".")
    fig, ax = plt.subplots(figsize=(6.3, 4.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def caixa(x, y, w, h, linhas, cor=CLARO, bold=True):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=cor, ec=AZUL, lw=0.8))
        ys = np.linspace(y + h - h / (len(linhas) + 1), y + h / (len(linhas) + 1), len(linhas))
        for i, (t, yy) in enumerate(zip(linhas, ys)):
            ax.text(x + w / 2, yy, t, ha="center", va="center", fontsize=8.2, fontweight="bold" if (bold and i == 0) else "normal", color=TEXTO)

    def seta(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=9, color=AZUL, lw=0.9, shrinkA=0, shrinkB=0))

    caixa(2, 84, 46, 13, ["Base (Inside Airbnb)", f"{f('imoveis_total')} anúncios", f"{f('avaliacoes_total')} avaliações"])
    caixa(52, 84, 46, 13, ["Recorte", f"{f('imoveis_elegiveis(nota>0, v>=MIN_REVIEWS)')} anúncios elegíveis", f"30 avaliações mais recentes: {f('avaliacoes_usadas')}"])
    seta(48.8, 90.5, 51.2, 90.5)
    caixa(27, 64, 46, 13, ["Sentenças", f"{f('sentencas')} sentenças", f"{f('textos_unicos')} textos únicos"])
    seta(75, 83, 60, 77.8)
    caixa(2, 40, 44, 15, ["Sentimento por sentença", "modelo A (principal)", "modelo B (robustez)", "regra de escolha fixada antes de B"])
    caixa(54, 40, 44, 15, ["Tópicos e aspectos", "BERTopic: 185 tópicos", "mapa para 10 aspectos", "(revisão do pesquisador)"])
    seta(40, 63.4, 27, 55.8)
    seta(60, 63.4, 73, 55.8)
    caixa(22, 20, 56, 12, ["Perfil por anúncio e aspecto", "sentimento médio, ao menos 2 sentenças", "28.889 anúncios com perfil"])
    seta(27, 39.4, 40, 32.8)
    seta(73, 39.4, 60, 32.8)
    caixa(2, 1, 44, 12, ["Validação da medição", "297 sentenças rotuladas, 2º anotador", "subnotas oficiais, LDA"], cor="#F2F2F2")
    caixa(54, 1, 44, 12, ["Análises e produto", "LMG, queixas e elogios, índice sintético", "diagnóstico por anúncio"], cor="#F2F2F2")
    seta(40, 19.4, 28, 13.8)
    seta(60, 19.4, 72, 13.8)
    salvar(fig, 1)


# ------------------------------------------------------------------------------------------------ 2. compressao da nota
def fig2():
    h = lido("Fig2_histograma_v2")
    r = lido("Fig2_resumo_v2").set_index("medida")
    fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.9), sharey=True)
    larg = 0.095
    ymax = max(h["n_nota_oficial"].max(), h["n_indice_sintetico"].max()) * 1.12
    for ax, col, cor, xl, k in ((axs[0], "n_nota_oficial", AZUL, "Nota oficial (estrelas)", "nota_oficial"), (axs[1], "n_indice_sintetico", LARANJA, "Índice sintético (estrelas)", "indice_sintetico")):
        ax.bar(h["faixa_inicio"] + larg / 2, h[col], width=larg, color=cor, edgecolor="white", linewidth=0.3)
        ax.set_xlim(1, 5.1)
        ax.set_ylim(0, ymax)
        ax.set_xlabel(xl)
        ax.axvline(r.loc["mediana", k], color="#333333", lw=0.8, ls="--")
        ax.text(r.loc["mediana", k] - 0.05, ymax * 0.93, f"mediana {pt(r.loc['mediana', k], 2)}", ha="right", va="top", fontsize=8)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}".replace(",", ".")))
    axs[0].set_ylabel("Número de anúncios")
    axs[0].text(4.62, ymax * 0.62, f"{pt(r.loc['% = 5,0', 'nota_oficial'])}% dos anúncios\ntêm nota 5,0", ha="right", fontsize=8, color=AZUL)
    fig.tight_layout(w_pad=1.2)
    salvar(fig, 5)


# ------------------------------------------------------------------------------------------------ 3. LMG
def fig3():
    d = lido("Fig3_LMG_v2").sort_values("parcela_A", ascending=True).reset_index(drop=True)
    fig, axs = plt.subplots(1, 2, figsize=(6.3, 3.6), sharey=True)
    for ax, col, m in ((axs[0], "parcela_A", "A"), (axs[1], "parcela_B", "B")):
        cores = [AZUL if c == "confiável" else CINZA for c in d["classificacao"]]
        ax.barh(range(len(d)), 100 * d[col], color=cores, height=0.68)
        for i, v in enumerate(100 * d[col]):
            ax.text(v + 0.8, i, f"{pt(v)}%", va="center", fontsize=8)
        ax.set_xlim(0, 60)
        ax.set_xlabel(f"Parcela do $R^2$ da nota global (%), modelo {m}")
        ax.set_yticks(range(len(d)))
    axs[0].set_yticklabels([NOME[a] for a in d["aspecto"]])
    axs[0].set_ylabel("")
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=AZUL, label="aspecto confiável"), Patch(color=CINZA, label="aspecto que pede cautela")], loc="lower center", ncol=2, frameon=False, fontsize=8.5,
               bbox_to_anchor=(0.5, -0.05))
    fig.tight_layout(w_pad=1.0)
    salvar(fig, 2)


# ------------------------------------------------------------------------------------------------ 4. diferencas com intervalos
ROT = {18: "banheiro, chuveiro", 10: "ar-condicionado, calor", 67: "sujeira, limpeza", 51: "decepção, problemas", 39: "cozinha, utensílios", 92: "resposta do anfitrião",
       19: "barulho", 104: "cheiro, mofo", 69: "cama, colchão", 71: "luz, cortinas (dormir)", 136: "reparos, manutenção", 130: "wi-fi, sinal",
       0: "anfitrião", 2: "estar no Rio", 7: "sentir-se em casa", 8: "voltar", 27: "agradecimento, atenção", 11: "limpo, organizado"}
TABELA_QUEIXAS = [18, 10, 67, 51, 39, 92, 19, 104, 69, 71, 136, 130]
TABELA_ELOGIOS = [0, 2, 7, 8, 27, 11]
CONFIAVEIS = {"limpeza", "localizacao", "custo_beneficio"}


def fig4():
    d = lido("Fig4_diferencas_v2")
    fig, axs = plt.subplots(2, 1, figsize=(6.3, 5.6), gridspec_kw={"height_ratios": [len(TABELA_QUEIXAS), len(TABELA_ELOGIOS)]})
    for ax, tipo, tops, xl in ((axs[0], "queixa", TABELA_QUEIXAS, ""), (axs[1], "elogio", TABELA_ELOGIOS, "Diferença associada no percentil da nota (pontos de percentil)")):
        s = d[(d["tipo"] == tipo) & (d["topic"].isin(tops))].set_index("topic").loc[tops].iloc[::-1]
        y = np.arange(len(s))
        for yy, (_, r) in zip(y, s.iterrows()):
            cor = AZUL if r["aspecto"] in CONFIAVEIS else CINZA
            ax.plot([r["ic_inf"], r["ic_sup"]], [yy, yy], color=cor, lw=1.4, solid_capstyle="butt")
            ax.plot(r["efeito_pontos_percentil_nota"], yy, "o", color=cor, ms=4.2)
            ax.text(r["ic_sup"] + 0.6 if tipo == "queixa" else r["ic_sup"] + 0.35, yy, f"{pt(r['efeito_pontos_percentil_nota'])}".replace("-", "−"), va="center", fontsize=7.5, color="#333333")
        ax.axvline(0, color="#333333", lw=0.7)
        ax.set_yticks(y)
        ax.set_yticklabels([f"{ROT[t]} ({NOME[a].lower()})" for t, a in zip(s.index, s["aspecto"])], fontsize=8)
        ax.set_ylim(-0.7, len(s) - 0.3)
        ax.set_xlabel(xl)
        ax.xaxis.grid(True, color="#E5E5E5", lw=0.5)
        ax.set_axisbelow(True)
    axs[0].set_xlim(-32, 5)
    axs[1].set_xlim(0, 14)
    axs[0].text(0.0, 1.03, "Queixas", transform=axs[0].transAxes, fontsize=8.5, fontweight="bold")
    axs[1].text(0.0, 1.06, "Elogios", transform=axs[1].transAxes, fontsize=8.5, fontweight="bold")
    from matplotlib.lines import Line2D
    fig.legend(handles=[Line2D([0], [0], marker="o", color=AZUL, lw=1.4, label="aspecto confiável"), Line2D([0], [0], marker="o", color=CINZA, lw=1.4, label="aspecto que pede cautela")],
               loc="lower center", ncol=2, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(h_pad=1.8)
    salvar(fig, 3)


# ------------------------------------------------------------------------------------------------ 5. relatorios anonimizados
def render_html(html: Path, png: Path, largura=1000, altura=2600):
    edge = EDGE
    tmp = tempfile.mkdtemp()
    subprocess.run([str(edge), "--headless", "--disable-gpu", f"--user-data-dir={tmp}", f"--window-size={largura},{altura}", "--hide-scrollbars",
                    "--force-device-scale-factor=2", f"--screenshot={png}", html.resolve().as_uri()], check=True, timeout=120, capture_output=True)
    for _ in range(40):  # o Edge pode devolver o controle antes de gravar o arquivo
        if png.exists() and png.stat().st_size > 0:
            break
        time.sleep(0.5)


def recorta(png: Path):
    from PIL import Image

    im = Image.open(png).convert("RGB")
    a = np.array(im)
    nao_branco = np.where((a < 245).any(axis=2).any(axis=1))[0]
    im.crop((0, 0, im.width, min(im.height, int(nao_branco.max()) + 30))).save(png)


def divide(png: Path):
    """Divide a pagina do relatorio em duas partes (parte superior e inferior), cortando numa faixa em branco perto do meio, para caber na pagina com letra legivel."""
    from PIL import Image

    im = Image.open(png).convert("RGB")
    a = np.array(im)
    branco = (a >= 250).all(axis=2).all(axis=1)
    lo, hi = int(0.50 * im.height), int(0.68 * im.height)
    melhor, atual, ini = (0, lo), 0, lo
    for y in range(lo, hi):
        if branco[y]:
            if atual == 0:
                ini = y
            atual += 1
            if atual > melhor[0]:
                melhor = (atual, ini + atual // 2)
        else:
            atual = 0
    corte = melhor[1]
    im.crop((0, 0, im.width, corte)).save(png.with_name(png.stem + "_a.png"))
    im.crop((0, corte, im.width, im.height)).save(png.with_name(png.stem + "_b.png"))


def relatorios():
    htmls = sorted((REPO / "outputs" / "diagnosticos").glob("diagnostico_*.html"))
    for i, h in enumerate(htmls, 1):
        png = SAIDA / f"relatorio_{i}.png"
        render_html(h, png)
        recorta(png)
        divide(png)
        pdf = SAIDA / f"relatorio_{i}.pdf"
        subprocess.run([str(EDGE), "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={tempfile.mkdtemp()}", f"--print-to-pdf={pdf}", h.resolve().as_uri()],
                       check=True, timeout=120, capture_output=True)
        for _ in range(40):
            if pdf.exists() and pdf.stat().st_size > 0:
                break
            time.sleep(0.5)
        print("relatorio", i, h.name)
    # Figura 4 do texto: parte superior do relatorio do anuncio de nota baixa (3o HTML em ordem alfabetica)
    import shutil

    shutil.copy(SAIDA / "relatorio_3_a.png", SAIDA / "figura_4.png")
    shutil.copy(SAIDA / "relatorio_3.pdf", SAIDA / "figura_4.pdf")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--relatorios", action="store_true")
    a = ap.parse_args()
    if a.relatorios:
        relatorios()
    else:
        for f in (fig1, fig2, fig3, fig4):
            f()
