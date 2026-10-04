"""Configuração única do pipeline. Nenhum parâmetro ajustável vive fora deste arquivo.

Decisões de projeto (acordadas no "grill"):
  * Limite de N avaliações mais recentes por imóvel (custo computacional em CPU).
  * R_syn_raw (contínuo) é a variável das Análises A/B e do teste do teto; o quantile
    mapping só gera R_syn_cal, usado para comunicação em estrelas (importar o teto de
    R_off para R_syn anularia o teste do teto).
  * Perfil ABSA -> R_syn por média igual dos aspectos disponíveis (sem pesos aprendidos
    contra R_off, que seriam circulares).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Aspectos com subnota oficial correspondente (validação de construto, Etapa 6).
ASPECT_TO_SUBSCORE = {
    "limpeza": "review_scores_cleanliness",
    "localizacao": "review_scores_location",
    "checkin": "review_scores_checkin",
    "comunicacao": "review_scores_communication",
    "custo_beneficio": "review_scores_value",
    "precisao": "review_scores_accuracy",
    # satisfação geral não tem subnota própria; a nota global é o análogo (checagem de construto, não circular:
    # R_syn não é ajustado contra R_off).
    "satisfacao_geral": "review_scores_rating",
}

# Taxonomia a priori + termos-semente multilíngues (pt, en, es, fr).
# "ruido_conforto", "seguranca" e "comodidades" não têm subnota oficial -> não validáveis.
ASPECT_SEEDS = {
    "limpeza": ["limpeza", "limpo", "sujo", "higiene", "cheiro", "mofo", "baratas",
                "cleanliness", "clean", "dirty", "spotless", "smell",
                "limpieza", "limpio", "sucio", "propreté", "propre", "sale"],
    "localizacao": ["localização", "bem localizado", "perto da praia", "perto do metrô", "bairro", "região",
                    "location", "well located", "close to the beach", "walking distance", "neighborhood",
                    "ubicación", "bien ubicado", "cerca de la playa", "emplacement", "bien situé", "quartier"],
    "checkin": ["check-in", "chegada", "entrada", "chaves", "self check-in", "portaria", "acesso",
                "arrival", "keys", "key box", "lockbox", "llegada", "llaves", "arrivée", "clés"],
    "comunicacao": ["anfitrião", "anfitriã", "comunicação", "atencioso", "prestativo", "respondeu rápido", "simpático",
                    "host", "communication", "responsive", "friendly host", "helpful",
                    "anfitrión", "comunicación", "amable", "atento", "hôte", "communication rapide", "accueillant"],
    "custo_beneficio": ["custo-benefício", "preço", "vale a pena", "barato", "caro", "valor",
                        "value for money", "price", "worth it", "cheap", "expensive", "affordable",
                        "relación calidad-precio", "precio", "rapport qualité-prix", "prix", "cher"],
    "ruido_conforto": ["barulho", "silencioso", "ruído", "confortável", "cama confortável", "ar-condicionado", "colchão",
                       "noise", "quiet", "loud", "comfortable", "comfortable bed", "air conditioning",
                       "ruido", "tranquilo", "cómodo", "colchón", "bruit", "calme", "confortable"],
    "seguranca": ["segurança", "seguro", "inseguro", "assalto", "perigoso", "portaria 24h",
                  "safety", "safe", "unsafe", "dangerous", "robbery", "secure",
                  "seguridad", "peligroso", "sécurité", "sûr", "dangereux"],
    "precisao": ["igual às fotos", "conforme anunciado", "descrição do anúncio", "fotos correspondem", "diferente do anúncio",
                 "as described", "matches the photos", "accurate listing", "misleading photos",
                 "como en las fotos", "tal como se describe", "conforme aux photos", "comme décrit"],
    "comodidades": ["cozinha equipada", "wifi", "piscina", "varanda", "vista", "utensílios", "máquina de lavar",
                    "equipped kitchen", "pool", "balcony", "view", "amenities", "washing machine",
                    "cocina equipada", "balcón", "équipements", "cuisine équipée", "piscine"],
    # elogio/queixa genérico (recomendo, voltarei, adorei, experiência incrível). Decisão v2: aspecto próprio,
    # em vez de diluir custo_beneficio/localizacao com sentimento que não é sobre esses aspectos.
    "satisfacao_geral": ["recomendo", "adorei", "amei", "voltarei", "estadia incrível", "experiência maravilhosa", "superou as expectativas",
                         "highly recommend", "loved it", "would come back", "wonderful stay", "great experience", "exceeded expectations",
                         "recomiendo", "me encantó", "volveré", "estadía maravillosa", "excelente experiencia",
                         "je recommande", "nous avons adoré", "séjour merveilleux", "reviendrons"],
}
GENERAL_BUCKET = "geral"  # tópicos genéricos/sem aspecto: fora do perfil ABSA e de R_syn


@dataclass
class Config:
    # --- caminhos ---
    LISTINGS_CSV: str = str(ROOT / "listings.csv")
    REVIEWS_CSV: str = str(ROOT / "reviews.csv")
    OUTPUT_DIR: str = str(ROOT / "outputs")
    MAPPING_CSV: str = str(ROOT / "data" / "mapa_aspecto_confirmado.csv")  # mapeamento humano

    # --- reprodutibilidade ---
    SEED: int = 42

    # --- escala / amostragem ---
    DEV_SAMPLE_FRAC: float = 1.0          # <1 sorteia imóveis (rodada de teste); 1 = todos
    MAX_REVIEWS_PER_LISTING: int = 30     # N avaliações mais recentes por imóvel (0 = todas)
    MIN_REVIEWS: int = 2                  # imóveis com number_of_reviews < MIN_REVIEWS são excluídos
    MIN_SENT_TOKENS: int = 3              # sentenças menores são fundidas à vizinha
    LANG_SET: tuple = ("pt", "en", "es", "fr", "de", "it")

    # --- modelos ---
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
    SENTIMENT_QUANTIZE: bool = False      # int8 dinâmico DESTRÓI este modelo (saída ~uniforme; testado) — manter False
    SENTIMENT_BATCH: int = 64
    SENTIMENT_MAX_LEN: int = 96
    SENTIMENT_CHUNK: int = 20_000
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_BATCH: int = 128
    EMBEDDING_CHUNK: int = 50_000
    TORCH_THREADS: int = 8

    # --- BERTopic ---
    TOPIC_MIN_TOKENS: int = 4             # só sentenças com >= este nº de tokens entram no ajuste
    BERTOPIC_FIT_SAMPLE: int = 200_000
    UMAP_N_NEIGHBORS: int = 15
    UMAP_N_COMPONENTS: int = 5
    HDBSCAN_MIN_CLUSTER_SIZE: int = 150
    HDBSCAN_MIN_SAMPLES: int = 10
    VECTORIZER_MIN_DF: int = 10
    TOPIC_TRANSFORM_CHUNK: int = 100_000
    OUTLIER_MIN_SIM: float = 0.45         # outlier (-1) só é reatribuído ao tópico mais próximo se cos >= isto
    TOPIC_TOP_WORDS: int = 10

    # --- LDA (linha de base) ---
    LDA_SAMPLE: int = 100_000
    LDA_MIN_TOKENS: int = 5
    LDA_K_GRID: tuple = (5, 10, 15, 20, 25, 30, 40)  # K escolhido por C_v máximo
    LDA_PASSES: int = 5
    COHERENCE_SAMPLE: int = 30_000        # textos usados para estimar C_v (custo)

    # --- aspectos ---
    ASPECT_SEEDS: dict = field(default_factory=lambda: ASPECT_SEEDS)
    ASPECT_TO_SUBSCORE: dict = field(default_factory=lambda: ASPECT_TO_SUBSCORE)
    MAPPING_MIN_SIM: float = 0.25         # abaixo disto a sugestão automática é "geral"
    MIN_SENT_PER_ASPECT: int = 2          # sentenças mínimas para o aspecto existir no imóvel
    MIN_ASPECTS: int = 3                  # aspectos ESPECÍFICOS mínimos para calcular R_syn
    GENERIC_ASPECTS: tuple = ("satisfacao_geral",)  # não contam para MIN_ASPECTS (estão em quase todo imóvel)
    RSYN_EXCLUDE_ASPECTS: tuple = ()      # aspectos fora da média de R_syn (sensibilidade: ("satisfacao_geral",))

    # --- rating sintético ---
    SHRINKAGE_M: float | None = None      # None -> mediana de number_of_reviews dos imóveis com R_syn
    # Especificação principal (decidida após ver a sensibilidade; ambas são reportadas): SEM shrinkage. Com m = mediana
    # de v, o shrinkage correlaciona R_syn com o volume (ρ = +0,50 dentro de R_off = 5,0, onde v mediano é 9), o que
    # contamina justamente o teste do teto. R_syn_shrink (com shrinkage, como na spec) fica sempre na tabela.
    RSYN_SHRINK: bool = False

    # --- Análises A e B ---
    PRIMARY_OUTCOME: str = "estimated_occupancy_l365d"
    SECONDARY_OUTCOME: str = "estimated_revenue_l365d"
    LOG_OUTCOMES: tuple = ("estimated_revenue_l365d", "number_of_reviews_ltm")   # desfechos modelados em log1p
    EXTRA_OUTCOMES: tuple = ("number_of_reviews_ltm",)  # desfecho sem construção algébrica (volume recente de avaliações)
    # Controle de avaliações dos últimos 12 meses. A ocupação estimada é EXATAMENTE
    # min(255, ltm * 2 * max(3, minimum_nights)) (verificado em 100% dos anúncios; ver historico/HISTORICO_DECISOES.md,
    # seção 13). Com este controle ligado o desfecho fica quase determinístico e o teste perde sentido; a spec original
    # pedia apenas o volume total de avaliações. False (principal) = sem ltm; True = análise anterior, só para referência.
    INCLUDE_LTM_CONTROL: bool = False  # ESPECIFICAÇÃO PRINCIPAL (aprovada em 2026-10-04); True = análise original
    CEIL_THRESHOLD: float = 4.8
    CEIL_THRESHOLDS: tuple = (4.8, 4.9, 5.0)   # grade de sensibilidade do teste no teto
    K_FOLDS: int = 5
    CV_REPEATS: int = 5
    RARE_NEIGHBOURHOOD_MIN: int = 20      # bairros menores são agrupados em "OUTROS"
    R_OFF_BANDS: tuple = (0.0, 4.5, 4.8, 4.9, 5.0, 5.0001)  # faixas de R_off (último bin = 5,0 exato)
    RANK_SHIFT_PCT: float = 10.0          # "mudança relevante" = >= 10 pontos percentuais de posto

    def cache_key(self) -> str:
        """Hash dos parâmetros que invalidam artefatos intermediários."""
        keys = ["DEV_SAMPLE_FRAC", "MAX_REVIEWS_PER_LISTING", "MIN_REVIEWS", "MIN_SENT_TOKENS", "SEED",
                "SENTIMENT_MODEL", "SENTIMENT_QUANTIZE", "EMBEDDING_MODEL", "LANG_SET"]
        d = {k: getattr(self, k) for k in keys}
        return hashlib.md5(json.dumps(d, default=str, sort_keys=True).encode()).hexdigest()[:8]

    def as_dict(self) -> dict:
        return asdict(self)


CONFIG = Config()
