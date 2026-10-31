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

## Reprodução e verificação
- Versões exatas dos pacotes: `requirements-lock.txt`. Dados de origem, somas de verificação e o que o repositório publica: `DADOS.md`.
- Análises de sensibilidade pedidas na revisão (Wilson, queixas com duas menções, subaspectos de comodidades, indicadores de ausência, Tabela 12 completa, dados das figuras): `python ajustes_v2.py` (grava `outputs/ajustes_v2/*.parquet` e uma cópia da planilha final com as abas `_v2`; aceita o nome de uma etapa, por exemplo `python ajustes_v2.py queixas_min2`).
- Figuras: `python redacao/figuras/gerar_figuras.py` e, para os relatórios anonimizados, `--relatorios` (dependências extras em `requirements-figuras.txt`).
- Conferências: `python redacao/verificar_numeros_v2.py` (números novos contra as abas e o cache) e `python redacao/verificar_referencias.py` (entradas do `.bib` com DOI contra o Crossref).
- Dissertação no formato do Guia da UCP: `python redacao/UCP/scripts/gerar_dissertacao_ucp.py`; os campos do Word são atualizados por `redacao/UCP/scripts/atualizar_campos.ps1`.

## Diagnóstico por anúncio
`python diagnostico.py --id 12345` gera um relatório HTML (perfil por aspecto, comparação com anúncios do mesmo bairro e tipo, queixas e elogios recorrentes).
Para exemplos publicáveis: `--anonimizar`. Exemplos anonimizados em `redacao/exemplos_diagnostico/`. Requer o pipeline já executado (etapas 1 a 17).

## Citação

Se este código ou modelo foi útil para a sua pesquisa, por favor cite a dissertação de mestrado correspondente:

```bibtex
@mastersthesis{eiras2026airbnb,
  author       = {Eiras, Raphael},
  title        = {{O QUE AS AVALIAÇÕES REVELAM SOBRE A NOTA}: decomposição por aspecto do sentimento em avaliações de hóspedes do {Airbnb} no {Rio de Janeiro}},
  school       = {Universidade Católica de Petrópolis},
  year         = {2026},
  type         = {Dissertação (Mestrado)},
  address      = {Petrópolis / RJ, Brasil},
  url          = {https://github.com/reirasdev/airbnb-reviews-topic-modelling-code}
}
```

## Licença

Este projeto está licenciado sob a **GNU General Public License v3.0 (GPLv3)**.

Isso significa que o código é livre para uso acadêmico, pessoal e modificações. Se você distribuir este código ou uma versão modificada dele, deve disponibilizar o código-fonte correspondente sob a mesma licença GPLv3. Veja o arquivo `LICENSE` para mais detalhes.
