# O que foi aplicado a partir de awesome-ai-for-economists

Branch `awesome-ai-for-economists`, criado a partir de `ajustes-orientador-14out26`. Nenhuma ferramenta de terceiros foi instalada ou executada: li o conteúdo de alguns skills (World Bank Reproducibility Skill, Econ Paper Review Skill) e de `bibverify` só como referência de checklist e implementei versões próprias, mínimas.

| Ideia da lista | O que foi feito | Arquivos |
|---|---|---|
| Verificação de BibTeX (`bibverify`) | Script próprio que compara as 65 entradas do `.bib` com o Crossref (ano, volume, número, páginas, título). 53 entradas com DOI conferiram; 5 divergências, todas explicadas (abaixo); 12 sem DOI | `redacao/verificar_referencias.py` |
| Auditoria de reprodutibilidade (World Bank Reproducibility Skill) | Registro das versões exatas dos pacotes, dados de origem com somas de verificação (SHA-256) e declaração do que o repositório publica; seção de reprodução e verificação no README; dependências das figuras separadas | `requirements-lock.txt`, `requirements-figuras.txt`, `DADOS.md`, `README.md` |
| Revisão simulada (Econ Paper Review Skill) | Conferência automática das remissões do documento final: todas as 42 seções numeradas, 17 tabelas e 11 figuras citadas existem; nenhum "Seção/Tabela/Figura N" aponta para algo inexistente. A conferência revelou uma frase imprecisa, corrigida (abaixo) | Seção 2.2 da dissertação (`cap3_dados_metodo.tex`) |

## Divergências do Crossref (nenhuma alterada no `.bib`)
- `reimers2019`: o Crossref dá as páginas 3980–3990; o `.bib` usa 3982–3992, conferidas na primeira página do PDF do artigo (registrado em 12/10).
- `landis1977`: o Crossref traz só a primeira página (159); o `.bib` usa 159–174.
- `zervas2021`: o Crossref data de 2020 (publicação online); a edição é de 2021 (*Marketing Letters* 32).
- `souza2020`: só a formatação do título difere.
- `bridges2018`: o Crossref dá 2016 (publicação online) e as páginas 2065–2083; o `.bib` usa 2018 e 2057–2075. **Não consegui resolver pelo PDF** (não consegui extrair o texto do arquivo). Vale conferir a primeira página do PDF do artigo.

## Correção feita no texto
A Seção 2.2 dizia que "as bases brutas não são publicadas" e que "os exemplos publicados" não têm trechos de avaliações, mas o repositório publica as 297 sentenças rotuladas e as 100 do segundo anotador (`data/validacao_*.xlsx`). O texto agora diz isso (sentenças com o primeiro nome do anfitrião mascarado, avaliações públicas sob CC BY 4.0) e restringe a frase sobre ausência de trechos aos relatórios de diagnóstico. O `.docx` e o PDF foram regenerados.

## O que não apliquei, e por quê
- Skills de redação (Econ Writing Skill) e de apresentações: são feitos para artigos de economia em inglês e conflitam com as convenções de estilo da dissertação.
- Servidores MCP de dados econômicos, Stata e ferramentas de macroeconomia: sem relação com este trabalho.
- Ferramentas de busca de literatura: a busca já foi feita e descrita (Seção 1.8 e Apêndice C).
- Revisor automático de rigor ou de argumentação: a leitura crítica fica com o orientador.
