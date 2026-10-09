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


# ---------------------------------------------------------------------------------------------------------------
# Modelo B: nlptown/bert-base-multilingual-uncased-sentiment (5 classes, 1 a 5 estrelas), treinado em avaliações de produtos
# e serviços. Mesma lógica de chunks com retomada; o texto único (text_id) é a chave de cache; modelo "uncased".
# ---------------------------------------------------------------------------------------------------------------
def _load_model_b(cfg):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    torch.set_num_threads(cfg.TORCH_THREADS)
    tok = AutoTokenizer.from_pretrained(cfg.SENTIMENT_MODEL_B)
    model = AutoModelForSequenceClassification.from_pretrained(cfg.SENTIMENT_MODEL_B).eval()
    labels = [str(model.config.id2label[i]) for i in range(model.config.num_labels)]
    log.info("Modelo B: %s | rótulos %s", cfg.SENTIMENT_MODEL_B, labels)
    assert model.config.num_labels == 5 and labels[0].startswith("1") and labels[4].startswith("5"), "ordem de rótulos inesperada"
    return tok, model


def _predict_b(texts: list[str], tok, model, cfg) -> np.ndarray:
    import torch

    out = []
    with torch.inference_mode():
        for i in range(0, len(texts), cfg.SENTIMENT_BATCH):
            enc = tok(texts[i:i + cfg.SENTIMENT_BATCH], truncation=True, max_length=cfg.SENTIMENT_MAX_LEN, padding=True, return_tensors="pt")
            out.append(torch.softmax(model(**enc).logits, dim=-1).numpy())
    return np.vstack(out).astype("float32")


def run_b(cfg, store: Store) -> None:
    with stage("Etapa 2 (modelo B) — Análise de sentimento com 5 classes"):
        T = store.load("texts").sort_values(["n_tok", "text_id"], kind="mergesort").reset_index(drop=True)
        tok, model = _load_model_b(cfg)
        for t, p in zip(_SANITY, _predict_b(_SANITY, tok, model, cfg)):
            log.info("  sanity: %-55s P(1..5)=%s", t, np.round(p, 2))
        cdir = store.subdir("sent_chunks_B")
        n_chunks = int(np.ceil(len(T) / cfg.SENTIMENT_CHUNK))
        t0, done = time.time(), 0
        for c in range(n_chunks):
            f = cdir / f"c{c:05d}.parquet"
            if f.exists():
                continue
            part = T.iloc[c * cfg.SENTIMENT_CHUNK:(c + 1) * cfg.SENTIMENT_CHUNK]
            p = _predict_b(part["text"].tolist(), tok, model, cfg)
            df = pd.DataFrame(p, columns=[f"p{k}" for k in range(1, 6)])
            df.insert(0, "text_id", part["text_id"].to_numpy())
            df.to_parquet(f, index=False)
            done += len(part)
            rate = done / (time.time() - t0)
            log.info("  [B] chunk %d/%d | %.0f textos/s | ETA %.0f min", c + 1, n_chunks, rate, (len(T) - (c + 1) * cfg.SENTIMENT_CHUNK) / max(rate, 1e-9) / 60)

        M = pd.concat([pd.read_parquet(cdir / f"c{c:05d}.parquet") for c in range(n_chunks)], ignore_index=True)
        P = M[[f"p{k}" for k in range(1, 6)]].to_numpy()
        M["stars"] = (P @ np.arange(1, 6)).astype("float32")                       # estrelas esperadas = soma de k·P(k)
        M["p_neg"], M["p_neu"], M["p_pos"] = M["p1"] + M["p2"], M["p3"], M["p4"] + M["p5"]  # descritivas (a polaridade usa cls)
        M["cls"] = np.array([0, 0, 1, 2, 2])[P.argmax(1)]                           # classe mais provável de 5: 1-2 neg, 3 neu, 4-5 pos
        store.save("sentiment", M)
        S = store.load("sentences")[["text_id", "lang"]].merge(M[["text_id", "stars", "cls"]], on="text_id")
        store.metric("etapa2", textos_unicos=len(M), stars_media=round(float(M["stars"].mean()), 3), stars_mediana=round(float(M["stars"].median()), 3),
                     prop_sentencas_stars_ge_4=round(float((S["stars"] >= 4).mean()), 3), prop_sentencas_stars_le_2=round(float((S["stars"] <= 2).mean()), 3),
                     prop_polaridade_neg_neu_pos=[round(float((S["cls"] == k).mean()), 3) for k in range(3)])
        log.info("Sentimento médio por idioma (B):\n%s", S.groupby("lang")["stars"].agg(["count", "mean"]).round(3).to_string())


_run_a = run


def run(cfg, store: Store) -> None:
    (run_b if cfg.SENTIMENT_SOURCE == "B" else _run_a)(cfg, store)
