# Graph Report - /home/fabiano/Documents/Yfinance  (2026-05-20)

## Corpus Check
- 69 files · ~161,381 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1131 nodes · 1236 edges · 180 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Structure Signals
- Entity graph basis: 1,064 non-file, non-concept node(s)
- Weakly connected components: 95
- Singleton components: 24
- Isolated nodes: 24
- Largest component: 88 node(s) (8% of the entity graph basis)
- Low-cohesion communities: 13
- Largest low-cohesion community: 18 node(s) (cohesion 0.11)

## Workspace Bridges
1. `Brain YFinance — Índice` - connects `Brain Brain Architecture`, `Brain Brain Yfinance — 11`, `Brain Brain Yfinance — 12`, `Brain Brain Yfinance — Alertas`, `Brain Brain Yfinance — De`, `Brain Brain Yfinance — De \(2\)`, `Brain Brain Yfinance — De \(3\)`, `Brain Brain Yfinance — De \(4\)`, `Brain Brain Yfinance — Diagrama`, `Brain Brain Yfinance — Limiares`, `Brain Brain Yfinance — Py`, `Brain Brain Yfinance — Que`; home: `Brain Brain Yfinance — Brain`; degree 13; score 26135.42
  source files: `/home/fabiano/Documents/Yfinance/src/brain/brain\_yfinance.md`
2. `5. Descrição das Classes e Arquivos Principais` - connects `Backend Buffett Fetcher`, `Backend Decision Service`, `Backend History Fetcher`, `Backend Market Service`, `Backend Portfolio Service`, `Backend Price Service`, `Backend Rules`, `Backend Stock Validator`, `Brain Brain Architecture`; home: `Brain Brain Architecture — Py`; degree 13; score 26921.95
  source files: `/home/fabiano/Documents/Yfinance/src/brain/brain\_architecture.md`
3. `5. Descrição das Classes e Arquivos Principais` - connects `Backend Buffett Fetcher`, `Backend Decision Service`, `Backend History Fetcher`, `Backend Portfolio Service`, `Backend Price Service`, `Backend Rules`, `Backend Stock Validator`, `Brain Brain Yfinance — Brain`; home: `Brain Brain Yfinance — Py`; degree 12; score 30009.1
  source files: `/home/fabiano/Documents/Yfinance/src/brain/brain\_yfinance.md`
4. `calculate\(\)` - connects `Backend Valuation Calculator — Ano`, `Backend Valuation Calculator — Base`, `Backend Valuation Calculator — Buffett`, `Backend Valuation Calculator — Pelo`, `Backend Valuation Calculator — Pre`, `Backend Valuation Calculator — Score`, `Backend Valuation Calculator — Ticker`; home: `Backend Valuation Calculator — De`; degree 9; score 566
  source files: `/home/fabiano/Documents/Yfinance/src/backend/services/valuation\_calculator.py`
5. `PriceService` - connects `Backend Price Service — De`, `Backend Price Service — Foi`, `Backend Price Service — JSON`, `Backend Price Service — Pre \(2\)`, `Backend Price Service — Retorna`, `Backend Price Service — Yfinance`; home: `Backend Price Service — Pre`; degree 10; score 6912
  source files: `/home/fabiano/Documents/Yfinance/src/backend/services/price\_service.py`
6. `\_build\_entry\(\)` - connects `Backend Decision Service — Atual`, `Backend Decision Service — Barsi`, `Backend Decision Service — Best`, `Backend Decision Service — De`, `Backend Decision Service — De \(2\)`, `Backend Decision Service — Pelo`; home: `Backend Decision Service — Build`; degree 8; score 542
  source files: `/home/fabiano/Documents/Yfinance/src/backend/services/decision\_service.py`

## God Nodes
1. `\_load\(\)` - 21 edges
2. `🧠 Berkshire Hathaway Annual Meeting — 1994` - 19 edges
3. `🧠 Berkshire Hathaway Annual Meeting — 1995` - 19 edges
4. `🧠 Berkshire Hathaway Annual Meeting — 1996` - 19 edges
5. `🧠 Berkshire Hathaway Annual Meeting — 1997` - 19 edges
6. `🧠 Berkshire Hathaway Annual Meeting — 1998` - 19 edges
7. `🧠 Berkshire Hathaway Annual Meeting — 1999` - 19 edges
8. `🧠 Berkshire Hathaway Annual Meeting — 2000` - 19 edges
9. `🧠 Berkshire Hathaway Annual Meeting — 2001` - 19 edges
10. `🧠 Berkshire Hathaway Annual Meeting — 2002` - 19 edges

## Surprising Connections
- None detected - all connections are within the same source files.

## Semantic Anomalies
- **[HIGH] Bridge node** - Brain YFinance — Índice bridges Brain Brain Yfinance — Brain and Brain Brain Architecture, Brain Brain Yfinance — Que, Brain Brain Yfinance — De \(3\), Brain Brain Yfinance — De \(4\), Brain Brain Yfinance — Py, Brain Brain Yfinance — Diagrama, Brain Brain Yfinance — De, Brain Brain Yfinance — De \(2\), Brain Brain Yfinance — Alertas, Brain Brain Yfinance — Limiares, Brain Brain Yfinance — 11, Brain Brain Yfinance — 12.
  _High betweenness centrality \(26002.419\) across 13 communities makes this node a likely dependency chokepoint._
- **[HIGH] Bridge node** - 5. Descrição das Classes e Arquivos Principais bridges Brain Brain Yfinance — Py and Brain Brain Yfinance — Brain, Backend Rules, Backend Stock Validator, Backend Price Service, Backend History Fetcher, Backend Buffett Fetcher, Backend Decision Service, Backend Portfolio Service.
  _High betweenness centrality \(29917.096\) across 9 communities makes this node a likely dependency chokepoint._
- **[HIGH] Bridge node** - 5. Descrição das Classes e Arquivos Principais bridges Brain Brain Architecture — Py and Brain Brain Architecture, Backend Rules, Backend Stock Validator, Backend Price Service, Backend History Fetcher, Backend Buffett Fetcher, Backend Decision Service, Backend Portfolio Service, Backend Market Service.
  _High betweenness centrality \(26818.947\) across 10 communities makes this node a likely dependency chokepoint._
- **[HIGH] Low-cohesion community** - Knowledge Base 1994 Brk Annual Meeting Analysis is weakly connected for its size.
  _Cohesion score 0.11 across 18 nodes suggests this community may mix unrelated responsibilities._
- **[HIGH] Low-cohesion community** - Knowledge Base 1995 Brk Annual Meeting Analysis is weakly connected for its size.
  _Cohesion score 0.11 across 18 nodes suggests this community may mix unrelated responsibilities._

## Communities

### Community 0 - "Backend Stock Repository"
Cohesion (entity basis within full-graph community): 0.05
Nodes (51): get\_all\_financials\(\), Retorna o mapa completo ticker -> entry de demonstrativos históricos., get\_all\_history\(\), get\_all\_indicators\(\), Retorna todos os registros de indicadores fundamentalistas., get\_all\_prices\(\), Retorna o mapa completo ticker -> entry de preços., get\_all\_valuations\(\) (+43 more)

### Community 1 - "Backend Financials Fetcher"
Cohesion (entity basis within full-graph community): 0.08
Nodes (28): \_fetch\_balanco\(\), Busca Balanço Patrimonial do StatusInvest. Retorna dict com campos snake\_case + '\_source', ou {} em caso de falha., \_fetch\_capex\_yf\(\), Busca apenas CAPEX via yfinance \(4-5 anos\). O StatusInvest não tem linha dedicada de CAPEX no getfluxocaixa. Retorna dict { "ano\_str": valor\_negativo } ou {} em caso de falha. CAPEX é negativo no yfinance \(saída de caixa\)., \_fetch\_cashflow\_yf\_fallback\(\), Fallback completo para yfinance quando StatusInvest falhar. Retorna fco, capex, da, fcf \(4-5 anos\)., \_fetch\_dre\(\), Busca DRE histórica do StatusInvest. Retorna dict com campos snake\_case + '\_source', ou {} em caso de falha. (+20 more)

### Community 2 - "Knowledge Base 1994 Brk Annual Meeting Analysis"
Cohesion (entity basis within full-graph community): 0.11
Nodes (18): 🧠 Berkshire Hathaway Annual Meeting — 1994, 🔥 Citações de Alto Valor, 🧩 Clusters Temáticos, 👔 Como Avaliar a Qualidade da Gestão, 🏗️ Como Julgar um Bom Negócio, 🌪️ Comportamento em Crises e Mercados Adversos, 📊 Densidade de Conhecimento, 🔬 Divergências entre Buffett e Munger (+10 more)

### Community 3 - "Knowledge Base 1995 Brk Annual Meeting Analysis"
Cohesion (entity basis within full-graph community): 0.11
Nodes (18): 🧠 Berkshire Hathaway Annual Meeting — 1995, 🔥 Citações de Alto Valor, 🧩 Clusters Temáticos, 👔 Como Avaliar a Qualidade da Gestão, 🏗️ Como Julgar um Bom Negócio, 🌪️ Comportamento em Crises e Mercados Adversos, 📊 Densidade de Conhecimento, 🔬 Divergências entre Buffett e Munger (+10 more)

### Community 4 - "Knowledge Base 1996 Brk Annual Meeting Analysis"
Cohesion (entity basis within full-graph community): 0.11
Nodes (18): 🧠 Berkshire Hathaway Annual Meeting — 1996, 🔥 Citações de Alto Valor, 🧩 Clusters Temáticos, 👔 Como Avaliar a Qualidade da Gestão, 🏗️ Como Julgar um Bom Negócio, 🌪️ Comportamento em Crises e Mercados Adversos, 📊 Densidade de Conhecimento, 🔬 Divergências entre Buffett e Munger (+10 more)

### Community 5 - "Knowledge Base 1997 Brk Annual Meeting Analysis"
Cohesion (entity basis within full-graph community): 0.11
Nodes (18): 🧠 Berkshire Hathaway Annual Meeting — 1997, 🔥 Citações de Alto Valor, 🧩 Clusters Temáticos, 👔 Como Avaliar a Qualidade da Gestão, 🏗️ Como Julgar um Bom Negócio, 🌪️ Comportamento em Crises e Mercados Adversos, 📊 Densidade de Conhecimento, 🔬 Divergências entre Buffett e Munger (+10 more)

### Community 6 - "Knowledge Base 1998 Brk Annual Meeting Analysis"
Cohesion (entity basis within full-graph community): 0.11
Nodes (18): 🧠 Berkshire Hathaway Annual Meeting — 1998, 🔥 Citações de Alto Valor, 🧩 Clusters Temáticos, 👔 Como Avaliar a Qualidade da Gestão, 🏗️ Como Julgar um Bom Negócio, 🌪️ Comportamento em Crises e Mercados Adversos, 📊 Densidade de Conhecimento, 🔬 Divergências entre Buffett e Munger (+10 more)

### Community 7 - "Knowledge Base 1999 Brk Annual Meeting Analysis"
Cohesion (entity basis within full-graph community): 0.11
Nodes (18): 🧠 Berkshire Hathaway Annual Meeting — 1999, 🔥 Citações de Alto Valor, 🧩 Clusters Temáticos, 👔 Como Avaliar a Qualidade da Gestão, 🏗️ Como Julgar um Bom Negócio, 🌪️ Comportamento em Crises e Mercados Adversos, 📊 Densidade de Conhecimento, 🔬 Divergências entre Buffett e Munger (+10 more)

### Community 8 - "Knowledge Base 2000 Brk Annual Meeting Analysis"
Cohesion (entity basis within full-graph community): 0.11
Nodes (18): 🧠 Berkshire Hathaway Annual Meeting — 2000, 🔥 Citações de Alto Valor, 🧩 Clusters Temáticos, 👔 Como Avaliar a Qualidade da Gestão, 🏗️ Como Julgar um Bom Negócio, 🌪️ Comportamento em Crises e Mercados Adversos, 📊 Densidade de Conhecimento, 🔬 Divergências entre Buffett e Munger (+10 more)

### Community 9 - "Knowledge Base 2001 Brk Annual Meeting Analysis"
Cohesion (entity basis within full-graph community): 0.11
Nodes (18): 🧠 Berkshire Hathaway Annual Meeting — 2001, 🔥 Citações de Alto Valor, 🧩 Clusters Temáticos, 👔 Como Avaliar a Qualidade da Gestão, 🏗️ Como Julgar um Bom Negócio, 🌪️ Comportamento em Crises e Mercados Adversos, 📊 Densidade de Conhecimento, 🔬 Divergências entre Buffett e Munger (+10 more)

### Community 10 - "Knowledge Base 2002 Brk Annual Meeting Analysis"
Cohesion (entity basis within full-graph community): 0.11
Nodes (18): 🧠 Berkshire Hathaway Annual Meeting — 2002, 🔥 Citações de Alto Valor, 🧩 Clusters Temáticos, 👔 Como Avaliar a Qualidade da Gestão, 🏗️ Como Julgar um Bom Negócio, 🌪️ Comportamento em Crises e Mercados Adversos, 📊 Densidade de Conhecimento, 🔬 Divergências entre Buffett e Munger (+10 more)

### Community 11 - "Knowledge Base 2003 Brk Annual Meeting Analysis"
Cohesion (entity basis within full-graph community): 0.11
Nodes (18): 🧠 Berkshire Hathaway Annual Meeting — 2003, 🔥 Citações de Alto Valor, 🧩 Clusters Temáticos, 👔 Como Avaliar a Qualidade da Gestão, 🏗️ Como Julgar um Bom Negócio, 🌪️ Comportamento em Crises e Mercados Adversos, 📊 Densidade de Conhecimento, 🔬 Divergências entre Buffett e Munger (+10 more)

### Community 12 - "Knowledge Base 2004 Brk Annual Meeting Analysis"
Cohesion (entity basis within full-graph community): 0.11
Nodes (18): 🧠 Berkshire Hathaway Annual Meeting — 2004, 🔥 Citações de Alto Valor, 🧩 Clusters Temáticos, 👔 Como Avaliar a Qualidade da Gestão, 🏗️ Como Julgar um Bom Negócio, 🌪️ Comportamento em Crises e Mercados Adversos, 📊 Densidade de Conhecimento, 🔬 Divergências entre Buffett e Munger (+10 more)

### Community 13 - "Knowledge Base Prompt Analise Brk"
Cohesion (entity basis within full-graph community): 0.11
Nodes (18): 🔥 Citações de Alto Valor, 🧩 Clusters Temáticos, 👔 Como Avaliar a Qualidade da Gestão, 🏗️ Como Julgar um Bom Negócio, 🌪️ Comportamento em Crises e Mercados Adversos, 📊 Densidade de Conhecimento, 🔬 Divergências entre Buffett e Munger, ❌ Erros e Lições Aprendidas (+10 more)

### Community 14 - "Knowledge Base 1994 2003 Brk Decade Consolidation"
Cohesion (entity basis within full-graph community): 0.13
Nodes (16): 10. ⚠️ Riscos Sistêmicos Identificados no Período, 11. 🔥 As 10 Melhores Citações da Década, 12. 🧩 Os 3 Clusters Temáticos Dominantes da Década, 13. ❓ As 10 Perguntas Fundamentais da Década, 14. 🎯 O Que Fazer Diferente — As 10 Ações Práticas da Década, 15. 📊 Meta-análise da Década, 16. 🧠 Interpretação Pessoal \(deixe em branco — para preenchimento posterior\), 1. 🔁 Princípios Repetidos com Alta Frequência (+8 more)

### Community 15 - "Knowledge Base Analise Dfp Kepl3 2024"
Cohesion (entity basis within full-graph community): 0.18
Nodes (11): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo (+3 more)

### Community 16 - "Knowledge Base Analise Dfp Shul4 2025"
Cohesion (entity basis within full-graph community): 0.18
Nodes (11): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo do Negócio (+3 more)

### Community 17 - "Knowledge Base Analise Dfp Vulc3 2025"
Cohesion (entity basis within full-graph community): 0.18
Nodes (11): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags, 8. Bloco 7 — Fase e Ciclo do Negócio (+3 more)

### Community 18 - "Knowledge Base Analise Dfp Grnd3 2022"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): Análise DFP — GRND3 | 2021–2022, Bloco 1 — DRE \(Qualidade do Resultado\), Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), Bloco 3 — Balanço e Endividamento, Bloco 4 — Retorno sobre Capital, Bloco 5 — Alocação de Capital, Bloco 6 — Red Flags, Bloco 7 — Fase e Ciclo (+2 more)

### Community 19 - "Knowledge Base Analise Dfp Grnd3 2023"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): Análise DFP — GRND3 | 2022–2023, Bloco 1 — DRE \(Qualidade do Resultado\), Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), Bloco 3 — Balanço e Endividamento, Bloco 4 — Retorno sobre Capital, Bloco 5 — Alocação de Capital, Bloco 6 — Red Flags, Bloco 7 — Fase e Ciclo (+2 more)

### Community 20 - "Knowledge Base Analise Dfp Grnd3 2024"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): Análise DFP — GRND3 | 2023–2024, Bloco 1 — DRE \(Qualidade do Resultado\), Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), Bloco 3 — Balanço e Endividamento, Bloco 4 — Retorno sobre Capital, Bloco 5 — Alocação de Capital, Bloco 6 — Red Flags, Bloco 7 — Fase e Ciclo (+2 more)

### Community 21 - "Knowledge Base Analise Dfp Grnd3 2025"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): Análise DFP — GRND3 | 2024–2025, Bloco 1 — DRE \(Qualidade do Resultado\), Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), Bloco 3 — Balanço e Endividamento, Bloco 4 — Retorno sobre Capital, Bloco 5 — Alocação de Capital, Bloco 6 — Red Flags, Bloco 7 — Fase e Ciclo (+2 more)

### Community 22 - "Knowledge Base Analise Dfp Kepl3 2021"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo (+2 more)

### Community 23 - "Knowledge Base Analise Dfp Kepl3 2022"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo (+2 more)

### Community 24 - "Knowledge Base Analise Dfp Kepl3 2023"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo (+2 more)

### Community 25 - "Knowledge Base Analise Dfp Kepl3 2025"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo do Negócio (+2 more)

### Community 26 - "Knowledge Base Analise Dfp Leve3 2021"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo (+2 more)

### Community 27 - "Knowledge Base Analise Dfp Leve3 2022"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo (+2 more)

### Community 28 - "Knowledge Base Analise Dfp Leve3 2023"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo (+2 more)

### Community 29 - "Knowledge Base Analise Dfp Leve3 2024"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo (+2 more)

### Community 30 - "Knowledge Base Analise Dfp Leve3 2025"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo (+2 more)

### Community 31 - "Knowledge Base Analise Dfp Shul4 2021"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo do Negócio (+2 more)

### Community 32 - "Knowledge Base Analise Dfp Shul4 2022"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo do Negócio (+2 more)

### Community 33 - "Knowledge Base Analise Dfp Shul4 2023"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo do Negócio (+2 more)

### Community 34 - "Knowledge Base Analise Dfp Shul4 2024"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo do Negócio (+2 more)

### Community 35 - "Knowledge Base Analise Itr Dfp Alld3 2021"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo (+2 more)

### Community 36 - "Knowledge Base Analise Itr Dfp Alld3 2022"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo (+2 more)

### Community 37 - "Knowledge Base Analise Itr Dfp Alld3 2023"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo (+2 more)

### Community 38 - "Knowledge Base Analise Itr Dfp Alld3 2024"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo (+2 more)

### Community 39 - "Knowledge Base Analise Itr Dfp Alld3 2025"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): 1. Resumo Executivo, 2. Bloco 1 — DRE: Qualidade do Resultado, 3. Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), 4. Bloco 3 — Balanço: Solidez e Endividamento, 5. Bloco 4 — Retorno sobre Capital, 6. Bloco 5 — Alocação de Capital, 7. Bloco 6 — Red Flags Contábeis, 8. Bloco 7 — Fase e Ciclo do Negócio (+2 more)

### Community 40 - "Brain Brain Architecture"
Cohesion (entity basis within full-graph community): 0.05
Nodes (7): 4. Árvore de Arquivos do Backend, Brain YFinance — Arquitetura, Classes e Diagramas, Brain YFinance — Cálculos, Métricas, Medalhas e Limiares, Brain YFinance — Páginas, Fontes de Dados e Limitações, Brain YFinance — Visão Geral e Filosofias, Arquivos do Brain, Antes de começar qualquer tarefa

### Community 41 - "Brain Brain Calculations"
Cohesion (entity basis within full-graph community): 0.18
Nodes (11): 7.10 DCF — Valor Intrínseco \(VI\), Base do Cálculo — LPA, Fórmula — 2-Stage DCF, Filosofia, Margem de Segurança, Output do campo dcf, Penalidade FCF — Crescimento, Não Base, Por que FCF penalty no crescimento, não na base? (+3 more)

### Community 42 - "Knowledge Base Analise Dfp Grnd3 2021"
Cohesion (entity basis within full-graph community): 0.2
Nodes (10): Análise DFP — GRND3 | 2020–2021, Bloco 1 — DRE \(Qualidade do Resultado\), Bloco 2 — Qualidade do Lucro \(Lucro vs. Caixa\), Bloco 3 — Balanço e Endividamento, Bloco 4 — Retorno sobre Capital, Bloco 5 — Alocação de Capital, Bloco 6 — Red Flags, Bloco 7 — Fase e Ciclo (+2 more)

### Community 43 - "Backend API Server"
Cohesion (entity basis within full-graph community): 0
Nodes (9): decision\(\), dividends\_ytd\(\), index\(\), market\(\), portfolio\(\), API server para o frontend YFINANCE. Serve os dados JSON do backend e dados de gráfico via yfinance. Endpoints: GET / → frontend/index.html GET /api/decision → decision\_stocks.json GET /api/valuation/<t> → valuations.json\[ticker\] GET /api/history/<t> → sto, \_save\_favoritos\(\), sectors\(\) (+1 more)

### Community 44 - "Brain Brain Calculations — Limiares"
Cohesion (entity basis within full-graph community): 0.22
Nodes (9): 10. Tabela de Referência — Todos os Limiares, Bazin/Barsi — Dividendos, BRank — Ranking Unificado, Buffett Moat — Padrões Mais Exigentes, DCF — Valor Intrínseco, Graham — Valuation, Piotroski — Limiares Conservadores, Qualidade — Rentabilidade (+1 more)

### Community 45 - "Brain Brain Calculations — Passo"
Cohesion (entity basis within full-graph community): 0.22
Nodes (9): 7.9 BRank — Ranking Unificado Buffett × Barsi × Bazin, Fórmula Completa, Interpretação e Cores, O problema que o BRank resolve, Onde aparece, Passo 1 — Normalização para \[0, 1\], Passo 2 — Soma Ponderada, Passo 3 — Gates Binários \(penalidades multiplicativas\) (+1 more)

### Community 46 - "Brain Brain Yfinance"
Cohesion (entity basis within full-graph community): 0.22
Nodes (9): 7.9 BRank — Ranking Unificado Buffett × Barsi × Bazin, Fórmula Completa, Interpretação e Cores, O problema que o BRank resolve, Onde aparece, Passo 1 — Normalização para \[0, 1\], Passo 2 — Soma Ponderada \(pesos filosóficos\), Passo 3 — Gates Binários \(penalidades multiplicativas\) (+1 more)

### Community 47 - "Brain Brain Calculations — De"
Cohesion (entity basis within full-graph community): 0.25
Nodes (8): 7.1 Alvo Bazin e Zonas de Preço \(Sinal\), 7.2 Potencial de Valorização \(gainpct\), 7.3 Distância do Mínimo \(Dist. Mín. / pnowpmin\), 7.4 Score Ponderado \(0–100\), 7.5 Piotroski F-Score \(0–9\), 7.7 FCF/Lucro — Qualidade do Lucro, 7.8 Acumulação Silenciosa \(Estratégia Barsi\), 7. Cálculos e Métricas Detalhadas

### Community 48 - "Brain Brain Yfinance — Limiares"
Cohesion (entity basis within full-graph community): 0.25
Nodes (8): 10. Tabela de Referência — Todos os Limiares, Bazin/Barsi — Dividendos, BRank — Ranking Unificado \(seção 7.9\), Buffett Moat — Padrões Mais Exigentes, Graham — Valuation, Piotroski — Limiares Conservadores, Qualidade — Rentabilidade, Técnico/Liquidez

### Community 49 - "Brain Brain Yfinance — De"
Cohesion (entity basis within full-graph community): 0.25
Nodes (8): 7.1 Alvo Bazin e Zonas de Preço \(Sinal\), 7.2 Potencial de Valorização \(gainpct\), 7.3 Distância do Mínimo \(Dist. Mín. / pnowpmin\), 7.4 Score Ponderado \(0–100\), 7.5 Piotroski F-Score \(0–9\), 7.7 FCF/Lucro — Qualidade do Lucro, 7.8 Acumulação Silenciosa \(Estratégia Barsi\), 7. Cálculos e Métricas Detalhadas

### Community 50 - "Knowledge Base Prompt Analise Dfp"
Cohesion (entity basis within full-graph community): 0.25
Nodes (8): 🧮 ANÁLISE POR BLOCO, BLOCO 1 — DRE: Qualidade do Resultado, BLOCO 2 — Qualidade do Lucro \(Lucro vs. Caixa\), BLOCO 3 — Balanço: Solidez e Endividamento, BLOCO 4 — Retorno sobre Capital, BLOCO 5 — Alocação de Capital, BLOCO 6 — Red Flags Contábeis, BLOCO 7 — Tendência e Ciclo do Negócio

### Community 51 - "Knowledge Base Prompt Sintese Tese Investimento"
Cohesion (entity basis within full-graph community): 0.25
Nodes (8): LENTE 1 — Círculo de Competência e Preditividade, LENTE 2 — Qualidade do Moat \(Fosso Competitivo\), LENTE 3 — Qualidade do Negócio: Capital e Caixa, LENTE 4 — Qualidade do Lucro e Contabilidade, LENTE 5 — Gestão: Honestidade e Alocação de Capital, LENTE 6 — Risco: Alavancagem, Liquidez e Concentração, LENTE 7 — Valuation: Aritmética antes de Otimismo, 🔍 LENTES DE ANÁLISE — Filtros da Mentalidade Buffett/Munger

### Community 52 - "Knowledge Base Sintese Tese Grnd3 2021 A 2025"
Cohesion (entity basis within full-graph community): 0.29
Nodes (7): 1. Fotografia do Negócio, 2. Evolução dos Indicadores-Chave, 3. Análise das 7 Lentes, 4. Inversão: O Que Pode Dar Errado, 5. O Que Precisaria Ser Verdade Para Comprar, Dados de Valuation \(entrada\), 🧠 Síntese de Tese — GRND3 | 2021–2025

### Community 53 - "Knowledge Base Sintese Tese Kepl3 2021 A 2025"
Cohesion (entity basis within full-graph community): 0.29
Nodes (7): 1. Fotografia do Negócio, 2. Evolução dos Indicadores-Chave, 3. Análise das 7 Lentes, 4. Inversão: O Que Pode Dar Errado, 5. O Que Precisaria Ser Verdade Para Comprar, 📈 Dados de Valuation, 🧠 Síntese de Tese — KEPL3 | 2021–2025

### Community 54 - "Backend Transcribe Meeting"
Cohesion (entity basis within full-graph community): 0.29
Nodes (7): download\_audio\(\), Baixa o áudio do YouTube e retorna \(caminho\_arquivo, titulo\)., main\(\), save\_transcription\(\), Salva texto completo e versão com timestamps., transcribe\(\), Carrega o modelo Whisper e transcreve o áudio.

### Community 55 - "Brain Brain Frontend"
Cohesion (entity basis within full-graph community): 0.29
Nodes (7): 12.1 CapEx Total vs. Manutenção, 12.2 Moat por Proxies Financeiros, 12.3 Fonte Única de Dados Fundamentalistas, 12.4 Setores Financeiros — Critérios Diferentes, 12.5 Sem Testes sobre Lógica de Negócio, 12.6 Frágil Dependência do Google Finance, 12. Limitações e Considerações Conhecidas

### Community 56 - "Brain Brain Yfinance — 12"
Cohesion (entity basis within full-graph community): 0.29
Nodes (7): 12.1 CapEx Total vs. Manutenção, 12.2 Moat por Proxies Financeiros, 12.3 Fonte Única de Dados Fundamentalistas, 12.4 Setores Financeiros — Critérios Diferentes, 12.5 Sem Testes Automatizados sobre Lógica de Negócio, 12.6 Frágil Dependência do Google Finance, 12. Limitações e Considerações Conhecidas

### Community 57 - "Knowledge Base Prompt Analise Dfp — De"
Cohesion (entity basis within full-graph community): 0.33
Nodes (6): 📤 FORMATO DE SAÍDA, 🎯 OBJETIVO, 📊 PROMPT: Análise de DFP/ITR Anual — Empresas B3, ⚙️ REGRAS DE QUALIDADE, SAIDA ESPERADA, 🏷️ SISTEMA DE TAGS

### Community 58 - "Brain Brain Calculations — De \(2\)"
Cohesion (entity basis within full-graph community): 0.33
Nodes (6): 7.11 Detector de Resultado Não Recorrente, Comportamento quando ativado, Fórmula, Histórico de decisões, Limiares, Problema que resolve

### Community 59 - "Brain Brain Calculations — De \(3\)"
Cohesion (entity basis within full-graph community): 0.33
Nodes (6): 8.1 Medalha de Ouro 🥇 — Ouro Barsi, 8.2 Medalha de Prata 🥈 — Margem Dupla, 8.3 Medalha de Bronze 🥉 — Atrativo por Dividendo, 8.4 Selo Buffett ★ — Excelência de Negócio, 8.5 Filtro BEST — Setores Barsi, 8. Sistema de Medalhas e Selos

### Community 60 - "Brain Brain Yfinance — De \(2\)"
Cohesion (entity basis within full-graph community): 0.33
Nodes (6): 8.1 Medalha de Ouro 🥇 — Ouro Barsi, 8.2 Medalha de Prata 🥈 — Margem Dupla, 8.3 Medalha de Bronze 🥉 — Atrativo por Dividendo, 8.4 Selo Buffett ★ — Excelência de Negócio, 8.5 Filtro BEST — Setores Barsi, 8. Sistema de Medalhas e Selos

### Community 61 - "Knowledge Base Prompt Sintese Tese Investimento — De"
Cohesion (entity basis within full-graph community): 0.4
Nodes (5): 📁 ENTRADA ESPERADA, 📝 EXEMPLO DE VEREDICTO BEM FORMULADO, 🎯 OBJETIVO, 🧠 PROMPT: Síntese de Tese de Investimento — Análise Multi-Ano \(Mentalidade Buffett/Munger\), ⚙️ REGRAS DE QUALIDADE

### Community 62 - "Knowledge Base Prompt Sintese Tese Investimento — Linhas"
Cohesion (entity basis within full-graph community): 0.33
Nodes (6): 1. Fotografia do Negócio \(máx. 8 linhas\), 2. Evolução dos Indicadores-Chave \(tabela consolidada\), 3. Análise das 7 Lentes \(1 parágrafo por lente — máx. 5 linhas cada\), 4. Inversão: O Que Pode Dar Errado \(lista\), 5. O Que Precisaria Ser Verdade Para Comprar, 📊 ESTRUTURA DE SAÍDA OBRIGATÓRIA

### Community 63 - "Brain Brain Architecture — Py"
Cohesion (entity basis within full-graph community): 0.4
Nodes (5): 5.11 apiserver.py — Flask + Scheduler, 5.2 repositories/stockrepository.py — Camada de Dados, 5.7 services/financialsfetcher.py — DRE 10 Anos do StatusInvest, 5.8 services/valuationcalculator.py — Motor Principal, 5. Descrição das Classes e Arquivos Principais

### Community 64 - "Brain Brain Frontend — 11"
Cohesion (entity basis within full-graph community): 0.4
Nodes (5): 11.1 Google Finance — Preços em Tempo Real, 11.2 Yahoo Finance \(yfinance\), 11.3 StatusInvest — API Não Oficial, 11.4 B3 — Arquivo de Custódia, 11. Fontes de Dados Externas

### Community 65 - "Brain Brain Overview"
Cohesion (entity basis within full-graph community): 0.4
Nodes (5): 1. Visão Geral, Filosofia Híbrida, O que é, O que faz, Stack Técnica

### Community 66 - "Brain Brain Overview — De"
Cohesion (entity basis within full-graph community): 0.4
Nodes (5): 2.1 Luiz Barsi Filho — "A Galinha dos Ovos de Ouro", 2.2 Décio Bazin — "Faça Fortuna com Ações" \(1992\), 2.3 Benjamin Graham — "O Investidor Inteligente", 2.4 Warren Buffett — Moat, FCF e Owner Earnings, 2. Filosofias de Investimento Implementadas

### Community 67 - "Brain Brain Yfinance — Que"
Cohesion (entity basis within full-graph community): 0.4
Nodes (5): 1. Visão Geral, Filosofia Híbrida, O que é, O que faz, Stack Técnica

### Community 68 - "Brain Brain Yfinance — 11"
Cohesion (entity basis within full-graph community): 0.4
Nodes (5): 11.1 Google Finance — Preços em Tempo Real, 11.2 Yahoo Finance \(yfinance\), 11.3 StatusInvest — API Não Oficial, 11.4 B3 — Arquivo de Custódia, 11. Fontes de Dados Externas

### Community 69 - "Brain Brain Yfinance — De \(3\)"
Cohesion (entity basis within full-graph community): 0.4
Nodes (5): 2.1 Luiz Barsi Filho — "A Galinha dos Ovos de Ouro", 2.2 Décio Bazin — "Faça Fortuna com Ações" \(1992\), 2.3 Benjamin Graham — "O Investidor Inteligente", 2.4 Warren Buffett — Moat, FCF e Owner Earnings, 2. Filosofias de Investimento Implementadas

### Community 70 - "Brain Brain Yfinance — Py"
Cohesion (entity basis within full-graph community): 0.4
Nodes (5): 5.11 apiserver.py — Flask + Scheduler, 5.2 repositories/stockrepository.py — Camada de Dados, 5.7 services/financialsfetcher.py — DRE 10 Anos do StatusInvest, 5.8 services/valuationcalculator.py — Motor Principal, 5. Descrição das Classes e Arquivos Principais

### Community 71 - "Brain Brain Yfinance — Diagrama"
Cohesion (entity basis within full-graph community): 0.4
Nodes (5): 6. Diagramas de Sequência, Diagrama 1 — Pipeline de Inicialização \(Execução Manual\), Diagrama 2 — Ciclo de Decisão Automático \(a cada 30 min\), Diagrama 3 — Requisição Frontend \(Screening\), Diagrama 4 — Carregamento da Carteira

### Community 72 - "Knowledge Base Prompt Analise Brk — De"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): 🎯 OBJETIVO, 📜 PROMPT: Análise de Reuniões Anuais da Berkshire Hathaway, ⚙️ REGRAS DE QUALIDADE DA ANÁLISE, 🏷️ SISTEMA DE TAGS

### Community 73 - "Knowledge Base 1994 2003 Brk Decade Consolidation — Quando"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): 6. 📅 Quando Comprar e Quando Não Comprar — Regras Consolidadas, ✅ Compre quando: \(apenas com 5+ ocorrências\), ❌ Não compre quando: \(apenas com 5+ ocorrências\), 🔒 Nunca venda quando:

### Community 74 - "Knowledge Base 1994 Brk Annual Meeting Analysis — Quando"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): ✅ Compre quando:, ❌ Não compre quando / Evite:, 🔒 Nunca venda quando:, 📅 Quando Comprar — e Quando Não Comprar

### Community 75 - "Knowledge Base 1995 Brk Annual Meeting Analysis — Quando"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): ✅ Compre quando:, ❌ Não compre quando / Evite:, 🔒 Nunca venda quando:, 📅 Quando Comprar — e Quando Não Comprar

### Community 76 - "Knowledge Base 1996 Brk Annual Meeting Analysis — Quando"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): ✅ Compre quando:, ❌ Não compre quando / Evite:, 🔒 Nunca venda quando:, 📅 Quando Comprar — e Quando Não Comprar

### Community 77 - "Knowledge Base 1997 Brk Annual Meeting Analysis — Quando"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): ✅ Compre quando:, ❌ Não compre quando / Evite:, 🔒 Nunca venda quando:, 📅 Quando Comprar — e Quando Não Comprar

### Community 78 - "Knowledge Base 1998 Brk Annual Meeting Analysis — Quando"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): ✅ Compre quando:, ❌ Não compre quando / Evite:, 🔒 Nunca venda quando:, 📅 Quando Comprar — e Quando Não Comprar

### Community 79 - "Knowledge Base 1999 Brk Annual Meeting Analysis — Quando"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): ✅ Compre quando:, ❌ Não compre quando / Evite:, 🔒 Nunca venda quando:, 📅 Quando Comprar — e Quando Não Comprar

### Community 80 - "Knowledge Base 2000 Brk Annual Meeting Analysis — Quando"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): ✅ Compre quando:, ❌ Não compre quando / Evite:, 🔒 Nunca venda quando:, 📅 Quando Comprar — e Quando Não Comprar

### Community 81 - "Knowledge Base 2001 Brk Annual Meeting Analysis — Quando"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): ✅ Compre quando:, ❌ Não compre quando / Evite:, 🔒 Nunca venda quando:, 📅 Quando Comprar — e Quando Não Comprar

### Community 82 - "Knowledge Base 2002 Brk Annual Meeting Analysis — Quando"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): ✅ Compre quando:, ❌ Não compre quando / Evite:, 🔒 Nunca venda quando:, 📅 Quando Comprar — e Quando Não Comprar

### Community 83 - "Knowledge Base 2003 Brk Annual Meeting Analysis — Quando"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): ✅ Compre quando:, ❌ Não compre quando / Evite:, 🔒 Nunca venda quando:, 📅 Quando Comprar — e Quando Não Comprar

### Community 84 - "Knowledge Base 2004 Brk Annual Meeting Analysis — Quando"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): ✅ Compre quando:, ❌ Não compre quando / Evite:, 🔒 Nunca venda quando:, 📅 Quando Comprar — e Quando Não Comprar

### Community 85 - "Knowledge Base Analise Itr Dfp Alld3 2025 — Milhares"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): Apêndice — Dados-Base Consolidados, Balanço-Chave \(R$ milhares\), DRE Resumida \(R$ milhares\), Fluxo de Caixa \(R$ milhares\)

### Community 86 - "Brain Brain Architecture — De"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): 3. Arquitetura Geral e Fluxo de Dados, Intervalos de Atualização, Padrão de Persistência — Atomic Write, Pipeline Completo

### Community 87 - "Backend Rules"
Cohesion (entity basis within full-graph community): 0
Nodes (3): 5.1 config/rules.py — Todos os Thresholds, 5.1 config/rules.py — Todos os Thresholds, Thresholds e regras de valuation. Baseado em Barsi, Bazin, Graham, Greenblatt e Lynch.

### Community 88 - "Backend Portfolio Service"
Cohesion (entity basis within full-graph community): 0
Nodes (3): 5.10 services/portfolioservice.py, 5.10 services/portfolioservice.py, Portfolio service — lê o arquivo de custódia B3 \(XLS\) e cruza com valuations.json para gerar recomendações por ativo. Apenas ativos presentes em valuations.json são incluídos. FIIs e outros ativos sem cobertura são ignorados silenciosamente.

### Community 89 - "Backend Stock Validator"
Cohesion (entity basis within full-graph community): 0
Nodes (3): 5.3 services/stockvalidator.py, 5.3 services/stockvalidator.py, Serviço de validação de tickers. Verifica periodicamente se cada ticker ainda está ativo e com dados disponíveis. Um ticker é marcado como INVÁLIDO quando ocorre qualquer das condições: - yfinance não retorna histórico de preço nos últimos 6 meses \(sem neg

### Community 90 - "Backend Price Service"
Cohesion (entity basis within full-graph community): 0
Nodes (3): 5.4 services/priceservice.py — Preço em Tempo Real, 5.4 services/priceservice.py — Preço em Tempo Real, PriceService — classe responsável por: 1. Buscar o preço atual de um ticker no Google Finance \(scraping\) 2. Ler o último preço salvo do JSON \(stock\_prices.json\) 3. Fazer update: buscar + persistir no JSON

### Community 91 - "Backend History Fetcher"
Cohesion (entity basis within full-graph community): 0
Nodes (3): 5.5 services/historyfetcher.py, 5.5 services/historyfetcher.py, Serviço de coleta de histórico via yfinance + StatusInvest. Persiste em data/stock\_history.json via stock\_repository. Para cada ticker válido \(conforme stock\_validity.json\) busca: - Preço mínimo e máximo dos últimos 6 meses \(yfinance\) - Dividendos pagos po

### Community 92 - "Backend Buffett Fetcher"
Cohesion (entity basis within full-graph community): 0
Nodes (3): 5.6 services/buffettfetcher.py — Fases 2 e 3 do Moat, 5.6 services/buffettfetcher.py — Fases 2 e 3 do Moat, Busca de dados de Fluxo de Caixa para análise Buffett \(Fases 2 e 3\). Fase 2 — fetch\_cashflow\(\): CapEx, D&A, FCO, FCF, Owner Earnings \(ano mais recente\). Fase 3 — fetch\_trends\(\): tendências históricas de 4 anos para 6 métricas chave. Chamado por history\_fet

### Community 93 - "Backend Decision Service"
Cohesion (entity basis within full-graph community): 0
Nodes (3): 5.9 services/decisionservice.py, 5.9 services/decisionservice.py, Serviço de decisão de compra. Lê os ativos qualificados de monitoring\_stocks.json, atualiza o preço via Google Finance, correlaciona com o histórico de 6 meses e calcula métricas de entrada. Persiste em data/decision\_stocks.json. Campos no JSON de saída \(o

### Community 94 - "Brain Brain Architecture — De \(2\)"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): 6. Diagramas de Sequência, Diagrama 1 — Pipeline de Inicialização \(Execução Manual\), Diagrama 2 — Ciclo de Decisão Automático \(a cada 30 min\), Diagrama 3 — Carregamento da Carteira

### Community 95 - "Brain Brain Calculations — Fase"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): 7.6 Buffett Moat Score \(0–10\), Fase 1 — Critérios Base \(0–10 pontos\), Fase 2 — Validação de Caixa \(informacional, não afeta score\), Fase 3 — Modificadores de Tendência \(±0.5 por critério\)

### Community 96 - "Brain Brain Frontend — De"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): 9.0 Header — Barra de Navegação Global, 9.3 Favoritos — Lista Personalizada, 9.4 Radar — Alertas de Preço, 9. Páginas da Aplicação

### Community 97 - "Brain Brain Frontend — De \(2\)"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): 9.1 Screening — Tela Principal, Modal de Detalhe — Cards de Preço \(#priceCards\), Modal de Detalhe — Gráfico Preço & Volume, Modal de Detalhe — Ranking no Setor \(#sectorRankBox\)

### Community 98 - "Brain Brain Frontend — Aba"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): 9.2 Carteira — Gestão de Posições, Cards de Resumo da Carteira \(#portfolioSummary\), Sub-aba Ações, Sub-aba FIIs

### Community 99 - "Brain Brain Yfinance — De \(4\)"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): 3. Arquitetura Geral e Fluxo de Dados, Intervalos de Atualização, Padrão de Persistência — Atomic Write, Pipeline Completo

### Community 100 - "Brain Brain Yfinance — Fase"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): 7.6 Buffett Moat Score \(0–10\), Fase 1 — Critérios Base \(0–10 pontos\), Fase 2 — Validação de Caixa \(Informacional, não afeta score\), Fase 3 — Modificadores de Tendência \(±0.5 por critério\)

### Community 101 - "Brain Brain Yfinance — Alertas"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): 9.1 Screening — Tela Principal, 9.3 Favoritos — Lista Personalizada, 9.4 Radar — Alertas de Preço, 9. Páginas da Aplicação

### Community 102 - "Claude"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): CLAUDE.md — YFINANCEREFACTOR, Estrutura do projeto, Padrões do projeto

### Community 103 - "Backend Price Service — Pre"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): PriceService, .\_default\_http\_client\(\), .\_\_init\_\_\(\), Serviço de preços de ações. Responsabilidades: - fetch\_from\_google\(ticker\) → busca preço ao vivo no Google Finance - get\_from\_json\(ticker\) → lê o último preço salvo localmente - update\(ticker, force\) → busca ao vivo e persiste no JSON - update\_all\(tickers,

### Community 104 - "Knowledge Base Prompt Analise Brk — Quando"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): ✅ Compre quando:, ❌ Não compre quando / Evite:, 🔒 Nunca venda quando:, 📅 Quando Comprar — e Quando Não Comprar

### Community 105 - "Knowledge Base Prompt Sintese Tese Investimento — Compra"
Cohesion (entity basis within full-graph community): 0.5
Nodes (4): 🔴 DESCARTAR A TESE, 🟡 MONITORAR, 🟢 OPORTUNIDADE DE COMPRA, 🏁 VEREDICTO FINAL

### Community 106 - "Knowledge Base Sintese Tese Grnd3 2021 A 2025 — Grnd3"
Cohesion (entity basis within full-graph community): 1
Nodes (2): 🟡 MONITORAR — GRND3, 🏁 VEREDICTO FINAL

### Community 107 - "Backend API Server — Radar"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): get\_radar\(\), get\_radar\_alerts\(\), \_load\_radar\(\)

### Community 108 - "Backend Market Service"
Cohesion (entity basis within full-graph community): 0
Nodes (2): 5.12 services/marketservice.py — Índices de Mercado, Market service — busca índices de mercado via yfinance e salva em market\_data.json. Índices: IBOV → ^BVSP \(Ibovespa — pontos\) USD → BRL=X \(Dólar / Real\) SP500 → ^GSPC \(S&P 500\) OURO → GC=F \(Ouro — USD/oz\)

### Community 109 - "Brain Brain Frontend — De \(3\)"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): 11.5 Alertas Visuais no Modal de Tendências Históricas, Badge de Dados Desatualizados \(⚠ vermelho\), Badge de Resultado Não Recorrente \(⚠ amarelo\)

### Community 110 - "Brain Brain Yfinance — Brain"
Cohesion (entity basis within full-graph community): 1
Nodes (2): 4. Árvore de Arquivos do Backend, Brain YFinance — Índice

### Community 111 - "Brain Brain Yfinance — Aba"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): 9.2 Carteira — Gestão de Posições, Sub-aba Ações, Sub-aba FIIs

### Community 112 - "Knowledge Base Consolidate Decade"
Cohesion (entity basis within full-graph community): 1
Nodes (2): 🧠 Berkshire Hathaway — Consolidado \[ANOINICIO\]–\[ANOFIM\], Como adaptar para outros períodos

### Community 113 - "Knowledge Base Consolidate Decade — Prompt"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): Como usar \(Claude Code\), O Prompt, Prompt: Consolidação de Década — BRK Annual Meetings

### Community 114 - "Backend Decision Service — Build"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): \_build\_entry\(\), Constrói a entrada de decisão para um ticker., \_safe\_float\(\)

### Community 115 - "Backend Decision Service — De"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): run\(\), Processa os tickers qualificados e gera decision\_stocks.json. tickers: lista específica ou None para usar todos de monitoring\_stocks.json force: força novo fetch de preço mesmo que esteja dentro do intervalo Retorna a lista de entradas gerada., \_save\_decision\_stocks\(\)

### Community 116 - "Backend History Fetcher — De"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): \_needs\_update\(\), update\_ticker\(\), Busca e persiste o histórico de um ticker. Retorna o dict de dados ou None se inválido / falhou.

### Community 117 - "Backend Market Service — Fetch"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): fetch\(\), \_fetch\_one\(\), Busca todos os índices e persiste em market\_data.json. Retorna o dict salvo.

### Community 118 - "Backend Portfolio Service — Em"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): load\(\), Lê o arquivo de custódia B3, cruza com valuations e retorna { summary, positions, fiis, fiis\_summary }. - Ativo em valuations.json → dados completos + recomendação - Ativo em stocks\_list mas não em valuations → incluído como "FORA\_CRITERIOS" - FIIs e outro, \_recommend\(\)

### Community 119 - "Backend Price Service — Pre \(2\)"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): .update\(\), .update\_all\(\), Busca o preço ao vivo e persiste no JSON. Se force=False e o preço ainda está dentro do intervalo mínimo, retorna o preço já salvo sem fazer nova requisição. Retorna o preço \(novo ou cacheado\) ou None em caso de falha.

### Community 120 - "Knowledge Base Prompt Analise Brk — Completamente"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): ❌ IGNORE completamente:, ✅ INCLUA obrigatoriamente:, 📌 REGRAS DE FILTRAGEM

### Community 121 - "Knowledge Base Prompt Analise Dfp — Completamente"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): ✅ EXTRAIA obrigatoriamente:, ❌ IGNORE completamente:, 📌 REGRAS DE FILTRAGEM

### Community 122 - "Backend Valuation Calculator"
Cohesion (entity basis within full-graph community): 0
Nodes (2): \_load\_sectors\(\), Serviço de cálculo de valuation por ticker. Combina dados de: - all\_indicators.json \(indicadores fundamentalistas\) - stock\_history.json \(min/max 6m + dividendos 4a\) - stock\_prices.json \(preço atual\) Calcula e persiste em data/valuations.json via stock\_repo

### Community 123 - "Backend Valuation Calculator — De"
Cohesion (entity basis within full-graph community): 0.67
Nodes (3): calculate\(\), Calcula o valuation completo de um ticker. Retorna o dict de valuation ou None se dados insuficientes. force=True: ignora os filtros de pré-qualificação \(usado para ativos da carteira que não passaram no screening, mas precisam de análise\). O resultado ter, \_safe\_float\(\)

### Community 124 - "Backend API Server — Chart"
Cohesion (entity basis within full-graph community): 1
Nodes (2): chart\(\), history\(\)

### Community 125 - "Backend API Server — Radar \(2\)"
Cohesion (entity basis within full-graph community): 1
Nodes (2): dismiss\_radar\_alert\(\), \_save\_radar\(\)

### Community 126 - "Backend API Server — Favoritos"
Cohesion (entity basis within full-graph community): 1
Nodes (2): get\_favoritos\(\), \_load\_favoritos\(\)

### Community 127 - "Backend API Server — Decision"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_run\_decision\(\), Executa o decision\_service e market\_service e registra o horário.

### Community 128 - "Backend API Server — Loop"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_scheduler\_loop\(\), Loop de background: executa imediatamente e depois a cada REFRESH\_INTERVAL\_HOURS.

### Community 129 - "Backend Buffett Fetcher — Estavel"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_calc\_tendencia\(\), Avalia a direção de uma série temporal \(mais recente primeiro\) via regressão linear. threshold\_rel: variação mínima por ano relativa à média para classificar tendência. Default 5% — abaixo disso classifica como ESTAVEL. Retorna: CRESCENDO, ESTAVEL ou CAIND

### Community 130 - "Backend Buffett Fetcher — Ano"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_extrair\_anos\(\), Extrai rótulos de ano das colunas do DataFrame \(mais recente primeiro\).

### Community 131 - "Backend Buffett Fetcher — Cashflow"
Cohesion (entity basis within full-graph community): 1
Nodes (2): fetch\_cashflow\(\), Busca dados de Fluxo de Caixa e DRE histórica via yfinance. Retorna dict com cashflow\_available=True e as métricas calculadas, ou {"cashflow\_available": False} em caso de qualquer falha. Campos retornados \(quando disponível\): cashflow\_available : bool cape

### Community 132 - "Backend Buffett Fetcher — Ano \(2\)"
Cohesion (entity basis within full-graph community): 1
Nodes (2): fetch\_trends\(\), Busca tendências históricas \(até 4 anos\) para análise Buffett Fase 3. Métricas calculadas ano a ano: margem\_bruta Gross Profit / Total Revenue \(%\) margem\_liquida Net Income / Total Revenue \(%\) roe Net Income / Stockholders Equity \(%\) fcf Operating Cash Flo

### Community 133 - "Backend Buffett Fetcher — Linha"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_safe\_row\(\), Extrai o valor mais recente \(.iloc\[0\]\) de uma linha do DataFrame. Retorna None se a linha não existe, o valor é NaN ou não é numérico.

### Community 134 - "Backend Buffett Fetcher — Do"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_safe\_series\(\), Extrai lista com até \`n\` valores históricos de uma linha do DataFrame. Colunas do yfinance são ordenadas do mais recente ao mais antigo. Retorna lista de floats ou None por posição; lista vazia se linha ausente.

### Community 135 - "Backend Decision Service — De \(2\)"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_calc\_accumulation\_30d\(\), Busca ~21 pregões via yfinance \(period='1mo'\) e conta quantos dias tiveram preço de fechamento E volume ambos abaixo da média dos 6 meses. Mesmo critério Barsi, janela de ~30 dias corridos.

### Community 136 - "Backend Decision Service — Barsi"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_calc\_unified\_rank\(\), Ranking unificado Buffett × Barsi × Bazin \(0-100\). Pesos: 30% weighted\_score — amplitude \(21 critérios Graham/Barsi/Bazin\) 20% buffett\_moat — qualidade/vantagem competitiva 20% piotroski — saúde financeira independente 15% dy\_real — renda contínua \(Barsi/B

### Community 137 - "Backend Decision Service — Atual"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_calc\_zone\(\), Recalcula a zona com o preço atual — desacoplado do valuation\_calculator.

### Community 138 - "Backend Decision Service — Best"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_is\_best\(\), Barsi BEST: Bancos · Elétricas · Seguradoras · Transmissão de Energia. Classificação via subsetor/segmento de all\_sectors.json.

### Community 139 - "Backend Decision Service — Sectors"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_load\_sectors\(\), Carrega all\_sectors.json — mapeamento ticker → {setor, subsetor, segmento}.

### Community 140 - "Backend Decision Service — Pelo"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_lookup\_sector\(\), Busca setor pelo ticker exato; fallback pelo radical de 4 letras. Ex: SAPR4 não encontrado → tenta qualquer chave que comece com 'SAPR'. Cobre todas as classes \(ON/PN/UNT\) da mesma empresa.

### Community 141 - "Backend Financials Fetcher — Dados"
Cohesion (entity basis within full-graph community): 1
Nodes (2): get\_stale\_tickers\(\), Detecta tickers com dados defasados no financials\_history.json. Um ticker é considerado defasado quando: ano\_atual - ultimo\_ano\_dre >= min\_gap Exemplo em 2026: dados até 2024 → gap=2 → defasado. dados até 2025 → gap=1 → OK. Retorna lista de \(ticker, ultimo

### Community 142 - "Backend Financials Fetcher — Dre"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_latest\_dre\_year\(\), Retorna o ano mais recente disponível na DRE do ticker \(excluindo TTM\).

### Community 143 - "Backend History Fetcher — Ltimos"
Cohesion (entity basis within full-graph community): 1
Nodes (2): fetch\_history\(\), Busca histórico completo de um ticker: - min/max de preço nos últimos 6 meses \(yfinance\) - dividendos por ano nos últimos 5 anos \(yfinance\) - lucro líquido por ano nos últimos 5 anos \(yfinance\) - payout ratio mais recente \(StatusInvest\) Retorna dict com os

### Community 144 - "Backend History Fetcher — Do"
Cohesion (entity basis within full-graph community): 1
Nodes (2): fetch\_payout\(\), Busca o payout ratio mais recente do StatusInvest. Equivalente ao get\_payout\(\) do sistema antigo, mas usando httpx ao invés de curl. O endpoint retorna uma lista de objetos; o campo 'actual' do primeiro item é o payout do período mais recente. Retorna o pa

### Community 145 - "Backend History Fetcher — Update"
Cohesion (entity basis within full-graph community): 1
Nodes (2): update\_all\(\), Atualiza histórico dos tickers válidos \(ou lista fornecida\). O intervalo HISTORY\_UPDATE\_INTERVAL\_DAYS controla o que realmente é refetchado. Retorna dict {ticker: entry\_or\_None}.

### Community 146 - "Knowledge Base Itr Dfp 4 T22"
Cohesion (entity basis within full-graph community): 1
Nodes (1): 📁 ENTRADA ESPERADA

### Community 147 - "Backend Market Service — Carrega"
Cohesion (entity basis within full-graph community): 1
Nodes (2): load\(\), Carrega market\_data.json do disco. Retorna None se não existir.

### Community 148 - "Backend Portfolio Service — B3"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_find\_b3\_file\(\), Retorna o primeiro arquivo .xls/.xlsx encontrado na pasta B3.

### Community 149 - "Backend Price Fetcher"
Cohesion (entity basis within full-graph community): 1
Nodes (1): Serviço de coleta de preços atual via Google Finance \(scraping\). Lê os preços e persiste em data/stock\_prices.json via stock\_repository. Uso direto: python price\_fetcher.py # atualiza todos os tickers válidos python price\_fetcher.py BBAS3 PETR4 # atualiza

### Community 150 - "Backend Price Fetcher — De"
Cohesion (entity basis within full-graph community): 1
Nodes (2): fetch\_price\(\), Busca o preço atual de um ticker no Google Finance. Retorna o preço como float ou None em caso de falha.

### Community 151 - "Backend Price Fetcher — Atualizado"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_needs\_update\(\), Retorna True se o preço precisa ser atualizado \(respeita intervalo mínimo\).

### Community 152 - "Backend Price Fetcher — De \(2\)"
Cohesion (entity basis within full-graph community): 1
Nodes (2): update\_all\(\), Atualiza preços de uma lista de tickers \(ou todos os válidos se None\). delay: pausa em segundos entre requisições para não sobrecarregar o Google. Retorna dict com resultados: {ticker: price\_or\_None}.

### Community 153 - "Backend Price Fetcher — Pre"
Cohesion (entity basis within full-graph community): 1
Nodes (2): update\_ticker\(\), Busca e persiste o preço de um ticker. Retorna o preço atualizado ou None se inválido / falhou.

### Community 154 - "Backend Price Service — De"
Cohesion (entity basis within full-graph community): 1
Nodes (2): .fetch\_from\_google\(\), Busca o preço atual de um ticker diretamente no Google Finance. Em caso de falha, tenta novamente até \`retries\` vezes com pausa de \`retry\_delay\` segundos. Retorna o preço como float ou None se todas as tentativas falharem.

### Community 155 - "Backend Price Service — Yfinance"
Cohesion (entity basis within full-graph community): 1
Nodes (2): .fetch\_from\_yfinance\(\), Busca o preço atual via yfinance \(TICKER.SA\) como fallback do Google Finance. Usa o último fechamento disponível no histórico de 5 dias.

### Community 156 - "Backend Price Service — JSON"
Cohesion (entity basis within full-graph community): 1
Nodes (2): .get\_entry\_from\_json\(\), Retorna a entrada completa \(ticker, price\_now, last\_updated, source\) do stock\_prices.json para o ticker. Útil para inspecionar metadados.

### Community 157 - "Backend Price Service — Retorna"
Cohesion (entity basis within full-graph community): 1
Nodes (2): .get\_from\_json\(\), Retorna o último preço válido salvo localmente para o ticker. Retorna None se nunca foi salvo.

### Community 158 - "Backend Price Service — Foi"
Cohesion (entity basis within full-graph community): 1
Nodes (2): .needs\_update\(\), Retorna True se o preço precisa ser atualizado: - nunca foi salvo, ou - a última atualização foi há mais de PRICE\_UPDATE\_INTERVAL\_HOURS horas

### Community 159 - "Knowledge Base Prompt Sintese Tese Investimento — De \(2\)"
Cohesion (entity basis within full-graph community): 1
Nodes (2): 📈 Dados de Valuation \(forneça antes de iniciar a análise\), SAIDA ESPERADA

### Community 160 - "Knowledge Base Sintese Tese Kepl3 2021 A 2025 — Compra"
Cohesion (entity basis within full-graph community): 1
Nodes (2): 🟢 OPORTUNIDADE DE COMPRA — KEPL3, 🏁 VEREDICTO FINAL

### Community 161 - "Backend Stock Validator — Ticker"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_check\_ticker\_yfinance\(\), Verifica via yfinance se o ticker tem dados válidos. Retorna \(is\_valid, reason\_if\_invalid\).

### Community 162 - "Backend Stock Validator — Check"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_needs\_check\(\), Retorna True se o ticker precisa ser re-validado.

### Community 163 - "Backend Stock Validator — Lidos"
Cohesion (entity basis within full-graph community): 1
Nodes (2): print\_report\(\), Exibe relatório dos tickers inválidos e válidos.

### Community 164 - "Backend Stock Validator — All"
Cohesion (entity basis within full-graph community): 1
Nodes (2): validate\_all\(\), Valida todos os tickers \(ou lista fornecida\). Retorna dict {ticker: entry}.

### Community 165 - "Backend Stock Validator — Ticker \(2\)"
Cohesion (entity basis within full-graph community): 1
Nodes (2): validate\_ticker\(\), Valida um ticker e persiste o resultado em stock\_validity.json. Retorna o dict de validade atualizado.

### Community 166 - "Backend Valuation Calculator — Anos"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_align\_hist\_to\_anos\(\), Alinha valores de uma métrica DRE à lista de anos dada \(None se ausente\).

### Community 167 - "Backend Valuation Calculator — Buffett"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_calc\_buffett\_moat\_score\(\), Buffett Moat Score \(0-10\) — Fase 1 do plano Warren Buffett. Usa apenas dados já disponíveis em all\_indicators.json e stock\_history.json. Critérios e pesos: Margem Bruta >= 40% : peso 2 \(pricing power — critério principal\) Margem Líquida >= 20% : peso 1 \(Bu

### Community 168 - "Backend Valuation Calculator — Base"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_calc\_dcf\(\), DCF 2-stage Buffett. Taxa de desconto: 10% \(mínimo Buffett, independe da Selic\). Base: LPA = preço / P·L. FCF quality penaliza o crescimento \(não escala a base — evita distorção em FCF baixo\).

### Community 169 - "Backend Valuation Calculator — Ano"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_calc\_piotroski\(\), Piotroski F-Score adaptado \(9 pontos\) com os dados disponíveis. Profitabilidade \(3 sinais\): P1 — Lucro Líquido positivo no ano mais recente P2 — Margem EBIT > 0 \(proxy de CF Operacional positivo\) P3 — Lucro crescendo \(ano mais recente > ano anterior\) Alava

### Community 170 - "Backend Valuation Calculator — Score"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_calc\_weighted\_score\(\), Score ponderado \(0-100\) baseado nos 21 critérios com pesos diferenciados. Grupos e pesos \(ver rules.WEIGHTED\_SCORE\_WEIGHTS\): Qualidade/Rentabilidade : peso 3 \(ROE, ROIC, margens\) Crescimento : peso 2 \(CAGR receita/lucro, dividendo crescente\) Dívida/Seguran

### Community 171 - "Backend Valuation Calculator — Pre"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_calc\_zone\(\), Determina a zona de preço do ativo: COMPRA\_FORTE : preço <= target\_8pct \(yield real >= 8%\) COMPRA : preço <= target\_6pct \(yield real >= 6%\) MONITORAR : preço <= target\_5pct \(yield real >= 5%\) CARO : preço > target\_5pct

### Community 172 - "Backend Valuation Calculator — Dre"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_extract\_dre\_hist\(\), Extrai série histórica de DRE \(mais recente primeiro\). Retorna \(anos, valores\).

### Community 173 - "Backend Valuation Calculator — Pelo"
Cohesion (entity basis within full-graph community): 1
Nodes (2): \_lookup\_sector\(\), Busca pelo ticker exato; fallback pelo radical de 4 letras.

### Community 174 - "Backend Valuation Calculator — JSON"
Cohesion (entity basis within full-graph community): 1
Nodes (2): update\_all\(\), Calcula valuation de todos os tickers \(ou lista fornecida\). Requer que stock\_prices.json e stock\_history.json já estejam populados. Retorna dict {ticker: entry\_or\_None}.

### Community 175 - "Backend Valuation Calculator — Ticker"
Cohesion (entity basis within full-graph community): 1
Nodes (2): update\_ticker\(\), Calcula e persiste o valuation de um ticker. Retorna o dict ou None.

### Community 176 - "Num Den 100 Com Prote O Contra Zero E None"
Cohesion (entity basis within full-graph community): 1
Nodes (1): num/den \* 100, com proteção contra zero e None.

### Community 177 - "Init Py"
Cohesion (entity basis within full-graph community): n/a
Nodes (0): 

### Community 178 - "Retorna Dividends Sum 12m Para Um Fii Via Yfinance"
Cohesion (entity basis within full-graph community): 1
Nodes (1): Retorna dividends\_sum\_12m para um FII via yfinance.

### Community 179 - "Readme Markdown"
Cohesion (entity basis within full-graph community): n/a
Nodes (0): 

## Knowledge Gaps
- **859 weakly connected node(s):** `index\(\)`, `sectors\(\)`, `decision\(\)`, `market\(\)`, `valuation\(\)` (+854 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Backend API Server — Chart`** (2 nodes): `chart\(\)`, `history\(\)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend API Server — Radar \(2\)`** (2 nodes): `dismiss\_radar\_alert\(\)`, `\_save\_radar\(\)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend API Server — Favoritos`** (2 nodes): `get\_favoritos\(\)`, `\_load\_favoritos\(\)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend API Server — Decision`** (2 nodes): `\_run\_decision\(\)`, `Executa o decision\_service e market\_service e registra o horário.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend API Server — Loop`** (2 nodes): `\_scheduler\_loop\(\)`, `Loop de background: executa imediatamente e depois a cada REFRESH\_INTERVAL\_HOURS.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Buffett Fetcher — Estavel`** (2 nodes): `\_calc\_tendencia\(\)`, `Avalia a direção de uma série temporal \(mais recente primeiro\) via regressão linear. threshold\_rel: variação mínima por ano relativa à média para classificar tendência. Default 5% — abaixo disso classifica como ESTAVEL. Retorna: CRESCENDO, ESTAVEL ou CAIND`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Buffett Fetcher — Ano`** (2 nodes): `\_extrair\_anos\(\)`, `Extrai rótulos de ano das colunas do DataFrame \(mais recente primeiro\).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Buffett Fetcher — Cashflow`** (2 nodes): `fetch\_cashflow\(\)`, `Busca dados de Fluxo de Caixa e DRE histórica via yfinance. Retorna dict com cashflow\_available=True e as métricas calculadas, ou {"cashflow\_available": False} em caso de qualquer falha. Campos retornados \(quando disponível\): cashflow\_available : bool cape`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Buffett Fetcher — Ano \(2\)`** (2 nodes): `fetch\_trends\(\)`, `Busca tendências históricas \(até 4 anos\) para análise Buffett Fase 3. Métricas calculadas ano a ano: margem\_bruta Gross Profit / Total Revenue \(%\) margem\_liquida Net Income / Total Revenue \(%\) roe Net Income / Stockholders Equity \(%\) fcf Operating Cash Flo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Buffett Fetcher — Linha`** (2 nodes): `\_safe\_row\(\)`, `Extrai o valor mais recente \(.iloc\[0\]\) de uma linha do DataFrame. Retorna None se a linha não existe, o valor é NaN ou não é numérico.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Buffett Fetcher — Do`** (2 nodes): `\_safe\_series\(\)`, `Extrai lista com até \`n\` valores históricos de uma linha do DataFrame. Colunas do yfinance são ordenadas do mais recente ao mais antigo. Retorna lista de floats ou None por posição; lista vazia se linha ausente.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Decision Service — De \(2\)`** (2 nodes): `\_calc\_accumulation\_30d\(\)`, `Busca ~21 pregões via yfinance \(period='1mo'\) e conta quantos dias tiveram preço de fechamento E volume ambos abaixo da média dos 6 meses. Mesmo critério Barsi, janela de ~30 dias corridos.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Decision Service — Barsi`** (2 nodes): `\_calc\_unified\_rank\(\)`, `Ranking unificado Buffett × Barsi × Bazin \(0-100\). Pesos: 30% weighted\_score — amplitude \(21 critérios Graham/Barsi/Bazin\) 20% buffett\_moat — qualidade/vantagem competitiva 20% piotroski — saúde financeira independente 15% dy\_real — renda contínua \(Barsi/B`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Decision Service — Atual`** (2 nodes): `\_calc\_zone\(\)`, `Recalcula a zona com o preço atual — desacoplado do valuation\_calculator.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Decision Service — Best`** (2 nodes): `\_is\_best\(\)`, `Barsi BEST: Bancos · Elétricas · Seguradoras · Transmissão de Energia. Classificação via subsetor/segmento de all\_sectors.json.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Decision Service — Sectors`** (2 nodes): `\_load\_sectors\(\)`, `Carrega all\_sectors.json — mapeamento ticker → {setor, subsetor, segmento}.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Decision Service — Pelo`** (2 nodes): `\_lookup\_sector\(\)`, `Busca setor pelo ticker exato; fallback pelo radical de 4 letras. Ex: SAPR4 não encontrado → tenta qualquer chave que comece com 'SAPR'. Cobre todas as classes \(ON/PN/UNT\) da mesma empresa.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Financials Fetcher — Dados`** (2 nodes): `get\_stale\_tickers\(\)`, `Detecta tickers com dados defasados no financials\_history.json. Um ticker é considerado defasado quando: ano\_atual - ultimo\_ano\_dre >= min\_gap Exemplo em 2026: dados até 2024 → gap=2 → defasado. dados até 2025 → gap=1 → OK. Retorna lista de \(ticker, ultimo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Financials Fetcher — Dre`** (2 nodes): `\_latest\_dre\_year\(\)`, `Retorna o ano mais recente disponível na DRE do ticker \(excluindo TTM\).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend History Fetcher — Ltimos`** (2 nodes): `fetch\_history\(\)`, `Busca histórico completo de um ticker: - min/max de preço nos últimos 6 meses \(yfinance\) - dividendos por ano nos últimos 5 anos \(yfinance\) - lucro líquido por ano nos últimos 5 anos \(yfinance\) - payout ratio mais recente \(StatusInvest\) Retorna dict com os`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend History Fetcher — Do`** (2 nodes): `fetch\_payout\(\)`, `Busca o payout ratio mais recente do StatusInvest. Equivalente ao get\_payout\(\) do sistema antigo, mas usando httpx ao invés de curl. O endpoint retorna uma lista de objetos; o campo 'actual' do primeiro item é o payout do período mais recente. Retorna o pa`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend History Fetcher — Update`** (2 nodes): `update\_all\(\)`, `Atualiza histórico dos tickers válidos \(ou lista fornecida\). O intervalo HISTORY\_UPDATE\_INTERVAL\_DAYS controla o que realmente é refetchado. Retorna dict {ticker: entry\_or\_None}.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Knowledge Base Itr Dfp 4 T22`** (2 nodes): `ITR\_DFP\_4T22.PDF`, `📁 ENTRADA ESPERADA`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Market Service — Carrega`** (2 nodes): `load\(\)`, `Carrega market\_data.json do disco. Retorna None se não existir.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Portfolio Service — B3`** (2 nodes): `\_find\_b3\_file\(\)`, `Retorna o primeiro arquivo .xls/.xlsx encontrado na pasta B3.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Price Fetcher`** (2 nodes): `price\_fetcher.py`, `Serviço de coleta de preços atual via Google Finance \(scraping\). Lê os preços e persiste em data/stock\_prices.json via stock\_repository. Uso direto: python price\_fetcher.py # atualiza todos os tickers válidos python price\_fetcher.py BBAS3 PETR4 # atualiza`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Price Fetcher — De`** (2 nodes): `fetch\_price\(\)`, `Busca o preço atual de um ticker no Google Finance. Retorna o preço como float ou None em caso de falha.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Price Fetcher — Atualizado`** (2 nodes): `\_needs\_update\(\)`, `Retorna True se o preço precisa ser atualizado \(respeita intervalo mínimo\).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Price Fetcher — De \(2\)`** (2 nodes): `update\_all\(\)`, `Atualiza preços de uma lista de tickers \(ou todos os válidos se None\). delay: pausa em segundos entre requisições para não sobrecarregar o Google. Retorna dict com resultados: {ticker: price\_or\_None}.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Price Fetcher — Pre`** (2 nodes): `update\_ticker\(\)`, `Busca e persiste o preço de um ticker. Retorna o preço atualizado ou None se inválido / falhou.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Price Service — De`** (2 nodes): `.fetch\_from\_google\(\)`, `Busca o preço atual de um ticker diretamente no Google Finance. Em caso de falha, tenta novamente até \`retries\` vezes com pausa de \`retry\_delay\` segundos. Retorna o preço como float ou None se todas as tentativas falharem.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Price Service — Yfinance`** (2 nodes): `.fetch\_from\_yfinance\(\)`, `Busca o preço atual via yfinance \(TICKER.SA\) como fallback do Google Finance. Usa o último fechamento disponível no histórico de 5 dias.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Price Service — JSON`** (2 nodes): `.get\_entry\_from\_json\(\)`, `Retorna a entrada completa \(ticker, price\_now, last\_updated, source\) do stock\_prices.json para o ticker. Útil para inspecionar metadados.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Price Service — Retorna`** (2 nodes): `.get\_from\_json\(\)`, `Retorna o último preço válido salvo localmente para o ticker. Retorna None se nunca foi salvo.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Price Service — Foi`** (2 nodes): `.needs\_update\(\)`, `Retorna True se o preço precisa ser atualizado: - nunca foi salvo, ou - a última atualização foi há mais de PRICE\_UPDATE\_INTERVAL\_HOURS horas`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Knowledge Base Prompt Sintese Tese Investimento — De \(2\)`** (2 nodes): `📈 Dados de Valuation \(forneça antes de iniciar a análise\)`, `SAIDA ESPERADA`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Knowledge Base Sintese Tese Kepl3 2021 A 2025 — Compra`** (2 nodes): `🟢 OPORTUNIDADE DE COMPRA — KEPL3`, `🏁 VEREDICTO FINAL`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Stock Validator — Ticker`** (2 nodes): `\_check\_ticker\_yfinance\(\)`, `Verifica via yfinance se o ticker tem dados válidos. Retorna \(is\_valid, reason\_if\_invalid\).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Stock Validator — Check`** (2 nodes): `\_needs\_check\(\)`, `Retorna True se o ticker precisa ser re-validado.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Stock Validator — Lidos`** (2 nodes): `print\_report\(\)`, `Exibe relatório dos tickers inválidos e válidos.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Stock Validator — All`** (2 nodes): `validate\_all\(\)`, `Valida todos os tickers \(ou lista fornecida\). Retorna dict {ticker: entry}.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Stock Validator — Ticker \(2\)`** (2 nodes): `validate\_ticker\(\)`, `Valida um ticker e persiste o resultado em stock\_validity.json. Retorna o dict de validade atualizado.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Valuation Calculator — Anos`** (2 nodes): `\_align\_hist\_to\_anos\(\)`, `Alinha valores de uma métrica DRE à lista de anos dada \(None se ausente\).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Valuation Calculator — Buffett`** (2 nodes): `\_calc\_buffett\_moat\_score\(\)`, `Buffett Moat Score \(0-10\) — Fase 1 do plano Warren Buffett. Usa apenas dados já disponíveis em all\_indicators.json e stock\_history.json. Critérios e pesos: Margem Bruta >= 40% : peso 2 \(pricing power — critério principal\) Margem Líquida >= 20% : peso 1 \(Bu`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Valuation Calculator — Base`** (2 nodes): `\_calc\_dcf\(\)`, `DCF 2-stage Buffett. Taxa de desconto: 10% \(mínimo Buffett, independe da Selic\). Base: LPA = preço / P·L. FCF quality penaliza o crescimento \(não escala a base — evita distorção em FCF baixo\).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Valuation Calculator — Ano`** (2 nodes): `\_calc\_piotroski\(\)`, `Piotroski F-Score adaptado \(9 pontos\) com os dados disponíveis. Profitabilidade \(3 sinais\): P1 — Lucro Líquido positivo no ano mais recente P2 — Margem EBIT > 0 \(proxy de CF Operacional positivo\) P3 — Lucro crescendo \(ano mais recente > ano anterior\) Alava`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Valuation Calculator — Score`** (2 nodes): `\_calc\_weighted\_score\(\)`, `Score ponderado \(0-100\) baseado nos 21 critérios com pesos diferenciados. Grupos e pesos \(ver rules.WEIGHTED\_SCORE\_WEIGHTS\): Qualidade/Rentabilidade : peso 3 \(ROE, ROIC, margens\) Crescimento : peso 2 \(CAGR receita/lucro, dividendo crescente\) Dívida/Seguran`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Valuation Calculator — Pre`** (2 nodes): `\_calc\_zone\(\)`, `Determina a zona de preço do ativo: COMPRA\_FORTE : preço <= target\_8pct \(yield real >= 8%\) COMPRA : preço <= target\_6pct \(yield real >= 6%\) MONITORAR : preço <= target\_5pct \(yield real >= 5%\) CARO : preço > target\_5pct`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Valuation Calculator — Dre`** (2 nodes): `\_extract\_dre\_hist\(\)`, `Extrai série histórica de DRE \(mais recente primeiro\). Retorna \(anos, valores\).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Valuation Calculator — Pelo`** (2 nodes): `\_lookup\_sector\(\)`, `Busca pelo ticker exato; fallback pelo radical de 4 letras.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Valuation Calculator — JSON`** (2 nodes): `update\_all\(\)`, `Calcula valuation de todos os tickers \(ou lista fornecida\). Requer que stock\_prices.json e stock\_history.json já estejam populados. Retorna dict {ticker: entry\_or\_None}.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backend Valuation Calculator — Ticker`** (2 nodes): `update\_ticker\(\)`, `Calcula e persiste o valuation de um ticker. Retorna o dict ou None.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Num Den 100 Com Prote O Contra Zero E None`** (1 nodes): `num/den \* 100, com proteção contra zero e None.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Init Py`** (1 nodes): `\_\_init\_\_.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Retorna Dividends Sum 12m Para Um Fii Via Yfinance`** (1 nodes): `Retorna dividends\_sum\_12m para um FII via yfinance.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Readme Markdown`** (1 nodes): `README.md`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does \`5. Descrição das Classes e Arquivos Principais\` connect \`Brain Brain Yfinance — Py\` to \`Brain Brain Yfinance — Brain\`, \`Backend Rules\`, \`Backend Stock Validator\`, \`Backend Price Service\`, \`Backend History Fetcher\`, \`Backend Buffett Fetcher\`, \`Backend Decision Service\`, \`Backend Portfolio Service\`?**
  _High betweenness centrality \(29917.096\) - this node is a cross-community bridge._
- **Why does \`5. Descrição das Classes e Arquivos Principais\` connect \`Brain Brain Architecture — Py\` to \`Brain Brain Architecture\`, \`Backend Rules\`, \`Backend Stock Validator\`, \`Backend Price Service\`, \`Backend History Fetcher\`, \`Backend Buffett Fetcher\`, \`Backend Decision Service\`, \`Backend Portfolio Service\`, \`Backend Market Service\`?**
  _High betweenness centrality \(26818.947\) - this node is a cross-community bridge._
- **Why does \`Brain YFinance — Índice\` connect \`Brain Brain Yfinance — Brain\` to \`Brain Brain Architecture\`, \`Brain Brain Yfinance — Que\`, \`Brain Brain Yfinance — De \(3\)\`, \`Brain Brain Yfinance — De \(4\)\`, \`Brain Brain Yfinance — Py\`, \`Brain Brain Yfinance — Diagrama\`, \`Brain Brain Yfinance — De\`, \`Brain Brain Yfinance — De \(2\)\`, \`Brain Brain Yfinance — Alertas\`, \`Brain Brain Yfinance — Limiares\`, \`Brain Brain Yfinance — 11\`, \`Brain Brain Yfinance — 12\`?**
  _High betweenness centrality \(26002.419\) - this node is a cross-community bridge._
- **What connects \`index\(\)\`, \`sectors\(\)\`, \`decision\(\)\` to the rest of the system?**
  _859 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should \`Knowledge Base 1994 Brk Annual Meeting Analysis\` be split into smaller, more focused modules?**
  _Cohesion score 0.11 across 18 entity nodes - this community may mix unrelated responsibilities._
- **Should \`Knowledge Base 1995 Brk Annual Meeting Analysis\` be split into smaller, more focused modules?**
  _Cohesion score 0.11 across 18 entity nodes - this community may mix unrelated responsibilities._
- **Should \`Knowledge Base 1996 Brk Annual Meeting Analysis\` be split into smaller, more focused modules?**
  _Cohesion score 0.11 across 18 entity nodes - this community may mix unrelated responsibilities._
