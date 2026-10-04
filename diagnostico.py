"""Gera o diagnóstico (HTML) de UM anúncio, a pedido, com comparação a anúncios do mesmo bairro e tipo.

Uso (Python do venv):
  python diagnostico.py --id 12345                     # relatório completo em outputs/diagnosticos/
  python diagnostico.py --id 12345 --anonimizar        # sem id, sem bairro, sem frases (para exemplos na dissertação)
  python diagnostico.py --id 12345 --sem-frases        # mantém id e bairro, omite as frases de exemplo
  python diagnostico.py --sortear 3 --anonimizar       # 3 anúncios de perfis diferentes (nota alta, baixa, poucas avaliações)
Requer que o pipeline já tenha rodado (cache em outputs/cache/...). Dados públicos do Airbnb; ainda assim, anonimize exemplos publicados.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from config import CONFIG
from src.diagnostico import gerar, tabela_base
from src.utils import Store


def sortear(cfg, store: Store, k: int) -> list[int]:
    F = tabela_base(cfg, store)
    F = F[F["n_asp"] >= 3]
    rng = np.random.default_rng(cfg.SEED)
    grupos = [F[(F["review_scores_rating"] >= 4.95) & (F["number_of_reviews"] >= 30)],
              F[(F["review_scores_rating"] <= 4.5) & (F["number_of_reviews"] >= 20)],
              F[(F["number_of_reviews"].between(3, 6))]]
    return [int(g.sample(1, random_state=int(rng.integers(1e9)))["id"].iloc[0]) for g in grupos[:k]]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", type=int, nargs="*", default=[])
    ap.add_argument("--sortear", type=int, default=0)
    ap.add_argument("--anonimizar", action="store_true")
    ap.add_argument("--sem-frases", action="store_true")
    ap.add_argument("--saida", default=str(Path(CONFIG.OUTPUT_DIR) / "diagnosticos"))
    a = ap.parse_args()
    store = Store(CONFIG)
    ids = list(a.id) + (sortear(CONFIG, store, a.sortear) if a.sortear else [])
    if not ids:
        ap.error("informe --id ou --sortear")
    for i in ids:
        print(gerar(CONFIG, store, i, Path(a.saida), a.anonimizar, a.sem_frases))


if __name__ == "__main__":
    main()
