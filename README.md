# airbnb-reviews-topic-modelling-code

Pipeline em Python (mestrado profissional) de análise de sentimento por aspecto sobre avaliações do Airbnb no Rio de Janeiro,
confrontado com as notas e subnotas oficiais. Ver `redacao/00_enquadramento.md` (perguntas de pesquisa) e
`historico/HISTORICO_DECISOES.md` (decisões, correções e resultados; a estratégia anterior termina na tag `estrategia-v1-tese-final`).
Texto de resultados vigente: `redacao/01_resultados_unificado.md` (gerado por `python redacao/montar_documento.py outputs/resultados_final_<carimbo>.xlsx` e conferido com `python redacao/verificar_numeros.py redacao/01_resultados_unificado.md outputs/resultados_final_<carimbo>.xlsx`). Rascunhos anteriores em `historico/rascunhos_v2/`.

## Como rodar
1. Python 3.11 em um venv de caminho curto (ex.: `C:\vairbnb`); `pip install torch --index-url https://download.pytorch.org/whl/cpu` e depois `pip install -r requirements.txt`.
2. Colocar `listings.csv` e `reviews.csv` na raiz (não são versionados).
3. `python run_pipeline.py --stages 1 2 3 4` (horas em CPU; retomável), revisar `data/mapa_aspecto_confirmado.xlsx`, depois `--stages 5 6 7 8 9 ...`.
4. Resultados em `outputs/` (log e Excel com uma aba por resultado). Parâmetros apenas em `config.py`.

## Diagnóstico por anúncio
`python diagnostico.py --id 12345` gera um relatório HTML (perfil por aspecto, comparação com anúncios do mesmo bairro e tipo, queixas e elogios recorrentes).
Para exemplos publicáveis: `--anonimizar`. Exemplos anonimizados em `redacao/exemplos_diagnostico/`. Requer o pipeline já executado (etapas 1 a 17).
