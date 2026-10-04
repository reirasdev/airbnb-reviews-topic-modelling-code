"""Núcleo do diagnóstico por anúncio (pergunta de pesquisa 3): dados do anúncio, comparação com anúncios semelhantes e relatório HTML.

O relatório descreve ASSOCIAÇÕES (o que os hóspedes escrevem e como isso se compara a anúncios do mesmo bairro e tipo). Não prevê
nota nem prescreve causas. Funciona também para anúncios novos (poucas avaliações): marca a evidência como baixa em vez de omitir.
"""
from __future__ import annotations

import hashlib
import html
from pathlib import Path

import numpy as np
import pandas as pd

from config import GENERAL_BUCKET
from .s15_importancia import tabela_anuncio_aspecto
from .utils import Store

ROTULO = {"limpeza": "Limpeza", "localizacao": "Localização", "checkin": "Check-in", "comunicacao": "Comunicação com o anfitrião",
          "custo_beneficio": "Custo-benefício", "ruido_conforto": "Ruído e conforto", "seguranca": "Segurança",
          "precisao": "Fidelidade ao anúncio (fotos/descrição)", "comodidades": "Comodidades e instalações",
          "satisfacao_geral": "Satisfação geral (elogio/queixa genérico)"}
SUBNOTA = {"limpeza": "review_scores_cleanliness", "localizacao": "review_scores_location", "checkin": "review_scores_checkin",
           "comunicacao": "review_scores_communication", "custo_beneficio": "review_scores_value", "precisao": "review_scores_accuracy",
           "satisfacao_geral": "review_scores_rating"}
MIN_PEERS = 30
EVID_BAIXA = 3  # menos de 3 frases no aspecto = evidência baixa


def tabela_base(cfg, store: Store) -> pd.DataFrame:
    """Tabela anúncio × aspecto (reaproveitada da Etapa 15); usa o cache da Etapa 17 quando existe."""
    return store.load("listing_aspect_table") if store.exists("listing_aspect_table") else tabela_anuncio_aspecto(cfg, store)


def pares(F: pd.DataFrame, row: pd.Series) -> tuple[pd.DataFrame, str]:
    """Anúncios comparáveis: mesmo bairro e tipo; se houver menos de MIN_PEERS, mesmo tipo na cidade."""
    p = F[(F["neighbourhood_cleansed"] == row["neighbourhood_cleansed"]) & (F["room_type"] == row["room_type"]) & (F["id"] != row["id"])]
    if len(p) >= MIN_PEERS:
        return p, f"{len(p)} anúncios do mesmo bairro e tipo de acomodação"
    p = F[(F["room_type"] == row["room_type"]) & (F["id"] != row["id"])]
    return p, f"{len(p)} anúncios do mesmo tipo de acomodação na cidade (poucos no bairro)"


def percentil(peers: pd.Series, x: float) -> float | None:
    s = peers.dropna()
    if len(s) < MIN_PEERS or pd.isna(x):
        return None
    return float(100 * ((s < x).mean() + 0.5 * (s == x).mean()))


def dados_anuncio(cfg, store: Store, listing_id: int) -> dict:
    F = tabela_base(cfg, store)
    sel = F[F["id"] == listing_id]
    if sel.empty:
        raise SystemExit(f"Anúncio {listing_id} não está na base analisada (precisa ter nota e >= {cfg.MIN_REVIEWS} avaliações, e texto).")
    row = sel.iloc[0]
    peers, peers_desc = pares(F, row)
    asp = []
    A = pd.read_parquet(store.path("sentencas_aspecto"), filters=[("listing_id", "==", int(listing_id))])
    Sn = store.load("sentiment")[["text_id", "p_neg", "p_neu", "p_pos"]]
    A = A.merge(Sn, on="text_id")
    A["cls"] = np.array(["neg", "neu", "pos"])[A[["p_neg", "p_neu", "p_pos"]].to_numpy().argmax(1)]
    cnt = A[A["aspecto"] != GENERAL_BUCKET].groupby("aspecto").size()
    for a in cfg.ASPECT_SEEDS:
        x = row.get(f"s_{a}")
        n = int(cnt.get(a, 0))
        pc = percentil(peers[f"s_{a}"], x) if pd.notna(x) else None
        asp.append({"aspecto": a, "rotulo": ROTULO[a], "media": None if pd.isna(x) else float(x), "n_frases": n,
                    "mediana_pares": float(peers[f"s_{a}"].median()), "percentil": pc,
                    "nota_oficial": float(row[SUBNOTA[a]]) if a in SUBNOTA and pd.notna(row.get(SUBNOTA[a])) else None,
                    "percentil_nota_oficial": percentil(peers[SUBNOTA[a]], row[SUBNOTA[a]]) if a in SUBNOTA else None})
    # tópicos: queixas e elogios com efeito medido na Etapa 15
    Q, E = store.load("imp_topicos_queixas"), store.load("imp_topicos_elogios")
    Ad = A[A["topic_direto"] & (A["topic"] >= 0)]
    Tx = store.load("texts").set_index("text_id")["text"]
    rng = np.random.default_rng(cfg.SEED)

    def topicos(kind, tab, sinal):
        out = []
        c = Ad[Ad["cls"] == kind].groupby("topic").size()
        for r in tab.itertuples():
            n = int(c.get(r.topic, 0))
            if n == 0:
                continue
            ids = Ad[(Ad["cls"] == kind) & (Ad["topic"] == r.topic)]["text_id"]
            ex = [Tx.loc[i][:220] for i in ids.sample(min(2, len(ids)), random_state=int(rng.integers(1e9)))]
            out.append({"topic": int(r.topic), "palavras": r.top_words, "aspecto": ROTULO.get(r.aspecto, r.aspecto), "n": n,
                        "efeito": float(r.efeito_pontos_percentil_nota), "prevalencia_cidade": float(r.prevalencia),
                        "prioridade": n * abs(float(r.efeito_pontos_percentil_nota)), "exemplos": ex})
        return sorted(out, key=lambda d: -d["prioridade"])[:6]

    # só tópicos com associação significativa (q < 0,05) no sentido esperado: queixa piora, elogio melhora o percentil da nota
    Q = Q[(Q["q_BH"] < 0.05) & (Q["efeito_pontos_percentil_nota"] < 0)]
    E = E[(E["q_BH"] < 0.05) & (E["efeito_pontos_percentil_nota"] > 0)]
    queixas, elogios = topicos("neg", Q, -1), topicos("pos", E, 1)
    # evolução: 10 avaliações mais recentes vs. anteriores (estrelas médias das frases)
    R = A.groupby(["review_id", "date"])["stars"].mean().reset_index()
    R = R.sort_values("date", ascending=False)
    evol = None
    if len(R) >= 20:
        evol = {"recentes": float(R.head(10)["stars"].mean()), "anteriores": float(R.iloc[10:]["stars"].mean()), "n_anteriores": len(R) - 10}
    return {"row": row, "peers_desc": peers_desc, "aspectos": asp, "queixas": queixas, "elogios": elogios, "evolucao": evol,
            "n_reviews_usadas": int(A["review_id"].nunique()), "n_frases": int(len(A)), "geral_peers": float(peers["review_scores_rating"].median()),
            "pct_nota": percentil(peers["review_scores_rating"], row["review_scores_rating"])}


def _n(x, d=2):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}".replace(".", ",")


def _barra(pc):
    if pc is None:
        return '<span class="mut">sem comparação</span>'
    cor = "#c0392b" if pc <= 25 else ("#1e8449" if pc >= 75 else "#7f8c8d")
    return (f'<div class="bar"><div class="fill" style="width:{pc:.0f}%;background:{cor}"></div>'
            f'<div class="mk" style="left:25%"></div><div class="mk" style="left:75%"></div></div><span class="pc">{pc:.0f}º</span>')


def renderizar(cfg, d: dict, anonimizar: bool = False, sem_frases: bool = False) -> str:
    row = d["row"]
    ident = (f"Anúncio {hashlib.md5(str(int(row['id'])).encode()).hexdigest()[:6].upper()}" if anonimizar else f"Anúncio {int(row['id'])}")
    local = "bairro oculto" if anonimizar else row["neighbourhood_cleansed"]
    fortes = [a for a in d["aspectos"] if a["percentil"] is not None and a["percentil"] >= 75 and a["n_frases"] >= EVID_BAIXA]
    atencao = [a for a in d["aspectos"] if a["percentil"] is not None and a["percentil"] <= 25 and a["n_frases"] >= EVID_BAIXA]
    linhas = []
    for a in d["aspectos"]:
        ev = "baixa" if a["n_frases"] < EVID_BAIXA else ("média" if a["n_frases"] < 8 else "boa")
        flag = ""
        if a["percentil"] is not None and a["n_frases"] >= EVID_BAIXA:
            flag = "▲ ponto forte" if a["percentil"] >= 75 else ("▼ ponto de atenção" if a["percentil"] <= 25 else "")
        linhas.append(f"<tr><td>{html.escape(a['rotulo'])}</td><td>{_n(a['media'])}</td><td>{a['n_frases']}</td>"
                      f"<td class='ev-{ev}'>{ev}</td><td>{_n(a['mediana_pares'])}</td><td>{_barra(a['percentil'])}</td>"
                      f"<td>{flag}</td><td>{_n(a['nota_oficial'])}</td></tr>")

    def bloco(titulo, itens, queixa):
        if not itens:
            return f"<h2>{titulo}</h2><p class='mut'>Nenhum tópico com efeito medido foi citado neste anúncio.</p>"
        s = [f"<h2>{titulo}</h2><table><tr><th>Tópico</th><th>Aspecto</th><th>Menções</th><th>Associação média na cidade com o percentil da nota</th>"
             f"<th>Anúncios que citam (cidade)</th></tr>"]
        for t in itens:
            ex = "" if sem_frases or anonimizar else "<br>".join(f"<i>“{html.escape(e)}”</i>" for e in t["exemplos"])
            s.append(f"<tr><td><b>{html.escape(t['palavras'][:70])}</b><div class='ex'>{ex}</div></td><td>{html.escape(t['aspecto'])}</td><td>{t['n']}</td>"
                     f"<td>{_n(t['efeito'], 1)} pontos</td><td>{100 * t['prevalencia_cidade']:.0f}%</td></tr>".replace("−", "-"))
        return "".join(s) + "</table>"

    evol = d["evolucao"]
    ev_txt = ("<p class='mut'>Menos de 20 avaliações usadas: evolução não calculada.</p>" if evol is None else
              f"<p>Estrelas médias das frases nas 10 avaliações mais recentes: <b>{_n(evol['recentes'])}</b>; nas {evol['n_anteriores']} anteriores: "
              f"<b>{_n(evol['anteriores'])}</b> (diferença {_n(evol['recentes'] - evol['anteriores'])}). Indicativo apenas.</p>")
    css = ("body{font-family:system-ui,Segoe UI,Arial;margin:24px auto;max-width:980px;color:#222;padding:0 16px}h1{font-size:22px}h2{font-size:17px;margin-top:28px;"
           "border-bottom:1px solid #ddd;padding-bottom:4px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{border-bottom:1px solid #eee;padding:6px 8px;text-align:left;"
           "vertical-align:top}th{background:#f6f6f6}.cards{display:flex;gap:12px;flex-wrap:wrap}.card{border:1px solid #ddd;border-radius:8px;padding:10px 14px;min-width:150px}"
           ".card b{font-size:20px;display:block}.mut{color:#888}.bar{display:inline-block;position:relative;width:120px;height:10px;background:#eee;border-radius:5px;"
           "vertical-align:middle;margin-right:6px}.fill{height:10px;border-radius:5px}.mk{position:absolute;top:-2px;width:1px;height:14px;background:#999}.pc{font-size:12px}"
           ".ev-baixa{color:#c0392b}.ev-média{color:#b9770e}.ev-boa{color:#1e8449}.ex{font-size:12px;color:#555;margin-top:4px}.nota{font-size:12px;color:#555;background:#fafafa;"
           "border:1px solid #eee;padding:10px;border-radius:6px;margin-top:24px}")
    pc_nota = d["pct_nota"]
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Diagnóstico — {ident}</title><style>{css}</style></head><body>
<h1>Diagnóstico de avaliações — {ident}</h1>
<p class="mut">{html.escape(local)} · {html.escape(row['room_type'])} · comparação com {html.escape(d['peers_desc'])}</p>
<div class="cards"><div class="card">Nota oficial<b>{_n(row['review_scores_rating'])}</b><span class="mut">mediana dos pares {_n(d['geral_peers'])} · {('%.0fº percentil' % pc_nota) if pc_nota is not None else '—'}</span></div>
<div class="card">Avaliações no total<b>{int(row['number_of_reviews'])}</b><span class="mut">usadas na análise: {d['n_reviews_usadas']} ({d['n_frases']} frases)</span></div>
<div class="card">Pontos fortes<b>{len(fortes)}</b><span class="mut">aspectos no 75º percentil ou acima</span></div>
<div class="card">Pontos de atenção<b>{len(atencao)}</b><span class="mut">aspectos no 25º percentil ou abaixo</span></div></div>
<h2>Perfil por aspecto</h2>
<p>Sentimento médio das frases (escala de 1 a 5 estrelas) em cada aspecto, comparado a anúncios semelhantes. A barra mostra a posição entre os pares (marcas em 25º e 75º);
quanto mais à direita, melhor o sentimento relativo. Aspectos com poucas frases têm evidência baixa e não são classificados como força ou atenção.</p>
<table><tr><th>Aspecto</th><th>Sentimento médio</th><th>Frases</th><th>Evidência</th><th>Mediana dos pares</th><th>Posição entre os pares</th><th></th><th>Nota oficial (subnota)</th></tr>{''.join(linhas)}</table>
{bloco('Queixas recorrentes (por prioridade = menções × associação)', d['queixas'], True)}
{bloco('Elogios recorrentes', d['elogios'], False)}
<h2>Evolução recente</h2>{ev_txt}
<div class="nota"><b>Como ler.</b> Medidas de associação construídas a partir do texto das avaliações (até as 30 mais recentes do anúncio), por modelos de linguagem multilíngues. A
atribuição de cada frase a um aspecto acerta cerca de 55% das vezes (de 41% a 74% conforme o aspecto) e o sentimento, cerca de 59% (validação manual com 297 frases): use este
relatório para priorizar investigações, não como medida exata. A "associação com o percentil da nota" é a diferença média, na cidade, entre anúncios que têm e que não têm esse tipo
de menção, controlada por volume de avaliações; não é efeito causal de corrigir o problema. Anúncios com poucas avaliações têm estimativas instáveis.</div>
</body></html>"""


def gerar(cfg, store: Store, listing_id: int, saida: Path, anonimizar: bool = False, sem_frases: bool = False) -> Path:
    d = dados_anuncio(cfg, store, listing_id)
    saida.mkdir(parents=True, exist_ok=True)
    nome = f"diagnostico_{hashlib.md5(str(listing_id).encode()).hexdigest()[:6]}" if anonimizar else f"diagnostico_{listing_id}"
    p = saida / f"{nome}.html"
    p.write_text(renderizar(cfg, d, anonimizar, sem_frases), encoding="utf-8")
    return p
