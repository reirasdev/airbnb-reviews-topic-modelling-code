"""Utilitários: seed global, logging para arquivo+console, armazenamento de artefatos."""
from __future__ import annotations

import json
import logging
import os
import random
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger("pipeline")


def set_seed(seed: int) -> None:
    """Fixa a seed de tudo que é estocástico. UMAP/HDBSCAN/k-fold recebem a seed explicitamente."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch
        torch.manual_seed(seed)
    except ImportError:
        pass


def setup_logging(log_path: Path) -> None:
    """Log em arquivo (rastro de auditoria) e eco no console."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%H:%M:%S")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # console do Windows é cp1252
    except Exception:
        pass
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    root.addHandler(fh)
    root.addHandler(ch)
    for noisy in ("httpx", "urllib3", "filelock", "huggingface_hub", "numba", "gensim", "matplotlib"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


@contextmanager
def stage(name: str):
    log.info("=" * 70)
    log.info("INÍCIO  %s", name)
    t0 = time.time()
    yield
    log.info("FIM     %s (%.1f min)", name, (time.time() - t0) / 60)


class Store:
    """Artefatos intermediários em outputs/cache/<hash>/ (parquet) + métricas por etapa.

    O hash da configuração garante que mudar amostra/modelo não reutilize cache velho.
    """

    def __init__(self, cfg):
        self.root = Path(cfg.OUTPUT_DIR) / "cache" / cfg.cache_key()
        self.tables = self.root / "tables"
        self.tables.mkdir(parents=True, exist_ok=True)
        self.metrics_path = self.root / "metrics.json"
        self.metrics = json.loads(self.metrics_path.read_text(encoding="utf-8")) if self.metrics_path.exists() else {}

    def path(self, name: str) -> Path:
        return self.tables / f"{name}.parquet"

    def exists(self, name: str) -> bool:
        return self.path(name).exists()

    def save(self, name: str, df: pd.DataFrame) -> None:
        df.to_parquet(self.path(name), index=False)

    def load(self, name: str) -> pd.DataFrame:
        return pd.read_parquet(self.path(name))

    def subdir(self, name: str) -> Path:
        p = self.root / name
        p.mkdir(parents=True, exist_ok=True)
        return p

    def metric(self, stage_name: str, **kv) -> None:
        """Registra métricas-chave (vão para a aba Resumo_Log) e as loga."""
        self.metrics.setdefault(stage_name, {}).update(kv)
        self.metrics_path.write_text(json.dumps(self.metrics, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        for k, v in kv.items():
            log.info("  [%s] %s = %s", stage_name, k, v)
