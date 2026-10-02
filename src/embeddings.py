"""Embeddings multilíngues por texto único, em chunks com checkpoint (float16 em disco)."""
from __future__ import annotations

import logging
import time

import numpy as np

from .utils import Store

log = logging.getLogger("pipeline")


def get_embedder(cfg):
    import torch
    from sentence_transformers import SentenceTransformer

    torch.set_num_threads(cfg.TORCH_THREADS)
    return SentenceTransformer(cfg.EMBEDDING_MODEL, device="cpu")


def embed_all(cfg, store: Store) -> np.ndarray:
    """Matriz (n_textos, d) float16 indexada por text_id, normalizada (cosseno = produto interno)."""
    T = store.load("texts")
    cdir = store.subdir("emb_chunks")
    order = T.sort_values(["n_tok", "text_id"], kind="mergesort").reset_index(drop=True)  # uniformiza padding
    n_chunks = int(np.ceil(len(order) / cfg.EMBEDDING_CHUNK))
    model, t0, done = None, time.time(), 0
    for c in range(n_chunks):
        f = cdir / f"c{c:05d}.npz"
        if f.exists():
            continue
        if model is None:
            model = get_embedder(cfg)
            log.info("Embedding: %s | %d textos únicos", cfg.EMBEDDING_MODEL, len(order))
        part = order.iloc[c * cfg.EMBEDDING_CHUNK:(c + 1) * cfg.EMBEDDING_CHUNK]
        e = model.encode(part["text"].tolist(), batch_size=cfg.EMBEDDING_BATCH, normalize_embeddings=True,
                         show_progress_bar=False)
        np.savez(f, ids=part["text_id"].to_numpy(), emb=e.astype("float16"))
        done += len(part)
        rate = done / (time.time() - t0)
        log.info("  embeddings chunk %d/%d | %.0f textos/s | ETA %.0f min", c + 1, n_chunks, rate,
                 (len(order) - (c + 1) * cfg.EMBEDDING_CHUNK) / max(rate, 1e-9) / 60)
    first = np.load(cdir / "c00000.npz")
    E = np.zeros((len(T), first["emb"].shape[1]), dtype="float16")
    for c in range(n_chunks):
        z = np.load(cdir / f"c{c:05d}.npz")
        E[z["ids"]] = z["emb"]
    return E
