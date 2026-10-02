"""Etapa 2 — Sentimento por sentença com um único modelo multilíngue.

Saída contínua em estrelas esperadas: 1*P(neg) + 3*P(neu) + 5*P(pos), em [1, 5] —
mesma escala das notas oficiais. Calculado por texto único, em chunks com checkpoint
(retomável), ordenado por comprimento para minimizar padding.
"""
from __future__ import annotations

import logging
import time

import numpy as np
import pandas as pd

from .utils import Store, stage

log = logging.getLogger("pipeline")

_SANITY = ["O apartamento estava impecável, super limpo!", "Lugar sujo e barulhento, não recomendo.",
           "The location is great but the bed was uncomfortable.", "Muy buena ubicación.",
           "Très bel appartement, hôte accueillant.", "Fica a duas quadras do metrô."]


def _load_model(cfg):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    torch.set_num_threads(cfg.TORCH_THREADS)
    tok = AutoTokenizer.from_pretrained(cfg.SENTIMENT_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(cfg.SENTIMENT_MODEL).eval()
    if cfg.SENTIMENT_QUANTIZE:
        model = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
    labels = [str(model.config.id2label[i]).lower() for i in range(model.config.num_labels)]
    if set(labels) >= {"negative", "neutral", "positive"}:
        order = [labels.index("negative"), labels.index("neutral"), labels.index("positive")]
    else:  # LABEL_0/1/2: assume neg, neu, pos (ordem documentada do modelo)
        log.warning("id2label inesperado %s; assumindo ordem neg/neu/pos", labels)
        order = [0, 1, 2]
    return tok, model, order


def _predict(texts: list[str], tok, model, order, cfg) -> np.ndarray:
    import torch

    out = []
    with torch.inference_mode():
        for i in range(0, len(texts), cfg.SENTIMENT_BATCH):
            enc = tok(texts[i:i + cfg.SENTIMENT_BATCH], truncation=True, max_length=cfg.SENTIMENT_MAX_LEN,
                      padding=True, return_tensors="pt")
            p = torch.softmax(model(**enc).logits, dim=-1).numpy()[:, order]
            out.append(p)
    return np.vstack(out).astype("float32")


def run(cfg, store: Store) -> None:
    with stage("Etapa 2 — Análise de sentimento"):
        T = store.load("texts").sort_values(["n_tok", "text_id"], kind="mergesort").reset_index(drop=True)
        tok, model, order = _load_model(cfg)
        log.info("Modelo: %s (quantizado=%s) | %d textos únicos", cfg.SENTIMENT_MODEL, cfg.SENTIMENT_QUANTIZE, len(T))
        for t, p in zip(_SANITY, _predict(_SANITY, tok, model, order, cfg)):
            log.info("  sanity: %-55s neg=%.2f neu=%.2f pos=%.2f", t, *p)

        cdir = store.subdir("sent_chunks")
        n_chunks = int(np.ceil(len(T) / cfg.SENTIMENT_CHUNK))
        t0 = time.time()
        done_texts = 0
        for c in range(n_chunks):
            f = cdir / f"c{c:05d}.parquet"
            if f.exists():
                continue
            part = T.iloc[c * cfg.SENTIMENT_CHUNK:(c + 1) * cfg.SENTIMENT_CHUNK]
            p = _predict(part["text"].tolist(), tok, model, order, cfg)
            pd.DataFrame({"text_id": part["text_id"].to_numpy(), "p_neg": p[:, 0], "p_neu": p[:, 1], "p_pos": p[:, 2]}
                         ).to_parquet(f, index=False)
            done_texts += len(part)
            rate = done_texts / (time.time() - t0)
            log.info("  chunk %d/%d | %.0f textos/s | ETA %.0f min", c + 1, n_chunks, rate,
                     (len(T) - (c + 1) * cfg.SENTIMENT_CHUNK) / max(rate, 1e-9) / 60)

        M = pd.concat([pd.read_parquet(cdir / f"c{c:05d}.parquet") for c in range(n_chunks)], ignore_index=True)
        M["stars"] = (1 * M["p_neg"] + 3 * M["p_neu"] + 5 * M["p_pos"]).astype("float32")
        store.save("sentiment", M)
        S = store.load("sentences")[["text_id", "lang"]].merge(M[["text_id", "stars"]], on="text_id")
        store.metric("etapa2", textos_unicos=len(M), stars_media=round(float(M["stars"].mean()), 3),
                     stars_mediana=round(float(M["stars"].median()), 3),
                     prop_sentencas_stars_ge_4=round(float((S["stars"] >= 4).mean()), 3),
                     prop_sentencas_stars_le_2=round(float((S["stars"] <= 2).mean()), 3))
        by_lang = S.groupby("lang")["stars"].agg(["count", "mean"]).round(3)
        log.info("Sentimento médio por idioma:\n%s", by_lang.to_string())
