"""Etapa 4 — Mapeamento tópico -> aspecto (sugestão por embeddings; decisão final humana).

O código calcula cos(centroide do tópico, vetor do aspecto = média dos embeddings dos
termos-semente) e sugere o aspecto de maior similaridade. Ele grava um CSV editável
(MAPPING_CSV); preencha a coluna `aspecto_confirmado` (um aspecto da taxonomia ou "geral")
e rode de novo as Etapas 5+. Linhas em branco usam a sugestão e o Excel sinaliza que o
mapeamento NÃO está totalmente confirmado.
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from config import GENERAL_BUCKET
from .embeddings import get_embedder
from .utils import Store, stage

log = logging.getLogger("pipeline")


def run(cfg, store: Store) -> None:
    with stage("Etapa 4 — Mapa tópico × aspecto"):
        topics = store.load("topics_bertopic")
        ids = sorted(topics["topic"])  # mesma ordem dos centroides salvos na Etapa 3
        cent = np.load(store.root / "topic_centroids.npy")
        model = get_embedder(cfg)
        aspects = list(cfg.ASPECT_SEEDS)
        A = []
        for a in aspects:
            v = model.encode(cfg.ASPECT_SEEDS[a], normalize_embeddings=True).mean(0)
            A.append(v / np.linalg.norm(v))
        sim = cent @ np.vstack(A).T
        M = pd.DataFrame(sim, columns=aspects)
        M.insert(0, "topic", ids)
        best = sim.argmax(1)
        M["sim_max"] = sim.max(1)
        M["sugestao"] = [aspects[b] if s >= cfg.MAPPING_MIN_SIM else GENERAL_BUCKET for b, s in zip(best, M["sim_max"])]
        M = M.merge(topics[["topic", "n_fit", "top_words", "exemplos"]], on="topic")
        store.save("mapa_topico_aspecto", M)

        path = Path(cfg.MAPPING_CSV)
        if not path.exists() and not path.with_suffix(".xlsx").exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            tpl = M[["topic", "n_fit", "top_words", "exemplos", "sugestao", "sim_max"]].copy()
            tpl["aspecto_confirmado"] = ""
            tpl.to_csv(path, index=False, encoding="utf-8-sig")
            log.warning("Modelo de mapeamento criado em %s — REVISE e preencha 'aspecto_confirmado'.", path)
        store.metric("etapa4", topicos_por_aspecto_sugerido=M["sugestao"].value_counts().to_dict())


def resolve_mapping(cfg, store: Store) -> tuple[dict[int, str], bool]:
    """Lê o CSV humano; completa lacunas com a sugestão. Retorna (topic->aspecto, totalmente_confirmado)."""
    M = store.load("mapa_topico_aspecto")
    sug = dict(zip(M["topic"], M["sugestao"]))
    mapping, confirmed = dict(sug), False
    path = Path(cfg.MAPPING_CSV)
    xlsx = path.with_suffix(".xlsx")  # o .xlsx (editado à mão) tem prioridade sobre o .csv gerado
    if xlsx.exists() or path.exists():
        path = xlsx if xlsx.exists() else path
        log.info("Lendo mapeamento humano de %s", path)
        H = pd.read_excel(path) if path.suffix == ".xlsx" else pd.read_csv(path, encoding="utf-8-sig")
        conf = H["aspecto_confirmado"].fillna("").astype(str).str.strip()
        valid = set(cfg.ASPECT_SEEDS) | {GENERAL_BUCKET}
        bad = set(conf[conf != ""]) - valid
        if bad:
            raise ValueError(f"Aspectos inválidos em {path}: {bad}. Válidos: {sorted(valid)}")
        for t, a in zip(H["topic"], conf):
            if a:
                mapping[int(t)] = a
        confirmed = bool((conf != "").all()) and set(H["topic"]) >= set(M["topic"])
    if not confirmed:
        log.warning("MAPEAMENTO NÃO CONFIRMADO integralmente: usando sugestão automática nas lacunas.")
    return mapping, confirmed
