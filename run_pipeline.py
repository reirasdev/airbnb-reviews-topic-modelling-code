"""Orquestrador do pipeline.

Uso (venv em C:\\vairbnb):
  python run_pipeline.py --dev                # rodada de teste (2% dos imóveis), valida o pipeline
  python run_pipeline.py --stages 1 2 3 4     # até o mapa tópico×aspecto; revisar data/mapa_aspecto_confirmado.csv
  python run_pipeline.py --stages 5 6 7 8 9   # depois da revisão manual
  python run_pipeline.py                      # tudo; etapas já concluídas são reaproveitadas do cache
  --force 2 3   refaz as etapas indicadas
"""
from __future__ import annotations

import argparse
import dataclasses
import shutil
from datetime import datetime
from pathlib import Path

from config import CONFIG
from src import excel_writer, s1_ingestao, s2_sentimento, s3_topicos, s4_mapa_aspecto, s5_s7_rating, s8_s9_analises, s10_sensibilidade, s11_complementar, s12_investigacao_coef, s13_sem_ltm, s14_validade_construto, s15_importancia, s16_sazonalidade, s17_benchmarks, s18_calibracao_sentimento, s22_lda_checagem, s19_comparacao_modelos, s20_avaliacao_manual_ab
from src.utils import Store, log, set_seed, setup_logging

# artefato principal de cada etapa (para pular o que já foi feito)
DONE = {1: "sentences", 2: "sentiment", 3: "topics_lda", 4: "mapa_topico_aspecto", 5: "perfil_absa",
        6: "validacao_construto", 7: "rating_sintetico", 8: "analise_a_modelos", 9: "analise_b_faixas", 10: "sensibilidade", 11: "descritivo_teto", 12: "investigacao_coef", 13: "sem_ltm_modelos", 14: "val_volume", 15: "imp_lmg", 16: "sazon_volume", 17: "benchmark_bairro_tipo", 18: "calib_correlacoes", 19: "cmp_descritivas", 20: "cmp_manual_modelos", 22: "lda_shared_atribuicao", 23: "lda_validade"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stages", type=int, nargs="*", default=list(range(1, 10)))
    ap.add_argument("--force", type=int, nargs="*", default=[])
    ap.add_argument("--dev", action="store_true", help="2%% dos imóveis, amostras e tópicos reduzidos (não é resultado final)")
    ap.add_argument("--max-reviews", type=int, default=None)
    ap.add_argument("--sentimento", choices=["A", "B"], default=None, help="fonte do sentimento (padrão: SENTIMENT_SOURCE do config)")
    ap.add_argument("--sem-excel", action="store_true", help="não gera a planilha ao final (a planilha final é gerada por --excel-final)")
    a = ap.parse_args()

    cfg = CONFIG
    if a.dev:
        cfg = dataclasses.replace(cfg, DEV_SAMPLE_FRAC=0.02, BERTOPIC_FIT_SAMPLE=30_000, HDBSCAN_MIN_CLUSTER_SIZE=30,
                                  HDBSCAN_MIN_SAMPLES=5, VECTORIZER_MIN_DF=3, LDA_SAMPLE=20_000, COHERENCE_SAMPLE=5_000,
                                  LDA_K_GRID=(5, 10), MAPPING_CSV=str(Path(cfg.OUTPUT_DIR) / "mapa_aspecto_dev.csv"))
    if a.sentimento:
        cfg = dataclasses.replace(cfg, SENTIMENT_SOURCE=a.sentimento)
    if a.max_reviews is not None:
        cfg = dataclasses.replace(cfg, MAX_REVIEWS_PER_LISTING=a.max_reviews)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = Path(cfg.OUTPUT_DIR)
    setup_logging(out / f"run_{ts}.log")
    set_seed(cfg.SEED)
    store = Store(cfg)
    log.info("Execução %s | cache %s | etapas %s | dev=%s", ts, store.root, a.stages, a.dev)

    steps = {1: s1_ingestao.run, 2: s2_sentimento.run, 3: s3_topicos.run, 4: s4_mapa_aspecto.run,
             5: s5_s7_rating.run_absa, 6: s5_s7_rating.run_validation, 7: s5_s7_rating.run_rating,
             8: s8_s9_analises.run_analise_a, 9: s8_s9_analises.run_analise_b, 10: s10_sensibilidade.run, 11: s11_complementar.run, 12: s12_investigacao_coef.run, 13: s13_sem_ltm.run, 14: s14_validade_construto.run, 15: s15_importancia.run, 16: s16_sazonalidade.run, 17: s17_benchmarks.run, 18: s18_calibracao_sentimento.run, 19: s19_comparacao_modelos.run, 20: s20_avaliacao_manual_ab.run, 22: s22_lda_checagem.run_prep, 23: s22_lda_checagem.run_comparacao}
    for n in a.stages:
        if n in a.force:
            for sub in {1: ["sent_chunks"], 2: ["sent_chunks"], 3: ["topic_chunks"]}.get(n, []):
                shutil.rmtree(store.root / sub, ignore_errors=True)
        elif store.exists(DONE[n]) and n not in (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23):
            log.info("Etapa %d já concluída (cache) — pulando", n)
            continue
        steps[n](cfg, store)
    if not a.sem_excel and cfg.SENTIMENT_SOURCE == "A":
        excel_writer.write_excel(cfg, store, out / f"resultados_{ts}.xlsx", ts)


if __name__ == "__main__":
    main()
