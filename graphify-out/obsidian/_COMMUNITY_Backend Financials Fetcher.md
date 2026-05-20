---
type: community
cohesion: 0.12
members: 29
---

# Backend Financials Fetcher

**Cohesion:** 0.12
**Members:** 29 nodes

## Members
- [[_fetch_balanco()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[_fetch_capex_yf()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[_fetch_cashflow_yf_fallback()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[_fetch_dre()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[_fetch_fluxo_caixa_si()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[_fetch_fluxo_caixa()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[_fetch_statusinvest()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[_has_data()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[_map_fields()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[_needs_update()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[Aplica field_map ao dict raw, retornando apenas os campos mapeados.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[Atualiza demonstrativos de todos os tickers válidos (ou lista fornecida). Progresso impresso por ticker  1234 BBAS3 DRE=]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[Busca apenas CAPEX via yfinance (4-5 anos). O StatusInvest não tem linha dedicada de CAPEX no getfluxocaixa. Retorna dic]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[Busca Balanço Patrimonial do StatusInvest. Retorna dict com campos snake_case + '_source', ou {} em caso de falha.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[Busca dados históricos do StatusInvest para um endpoint ('getdre' ou 'getativos'). Retorna dict { nome_indicador_raw { a]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[Busca DRE histórica do StatusInvest. Retorna dict com campos snake_case + '_source', ou {} em caso de falha.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[Busca e persiste demonstrativos de um ticker. Retorna o dict de dados, ou None se o ticker for inválido ou os fetches fa]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[Busca e persiste demonstrativos financeiros históricos (até 10 anos) - DRE via StatusInvest getdre - Balanço Patrimonial]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[Busca Fluxo de Caixa do StatusInvest (getfluxocaixa) — até 10+ anos históricos. Campos principais fco — Caixa Líquido At]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[Converte string do StatusInvest para float. Exemplos 3.938,54 M - 3938540000.0 -9,80 - -9.8 - - None]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[Fallback completo para yfinance quando StatusInvest falhar. Retorna fco, capex, da, fcf (4-5 anos).]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[fetch_financials()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[financials_fetcher.py]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[Fluxo de Caixa combinado - Fonte primária StatusInvest getfluxocaixa (10+ anos) → fco, da, fcf_livre, investing, financi]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[Orquestra os três fetches para um ticker com rate limiting entre chamadas SI. Fluxo _fetch_dre() → sleep(1.5s) _fetch_ba]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[parse_statusinvest_value()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[True se o dict tem pelo menos uma chave sem prefixo '_'.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[update_all()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py
- [[update_ticker()]] - code - /home/fabiano/Documents/Yfinance/src/backend/services/financials\_fetcher.py

## Connections to other communities
- 1 edge to [[_COMMUNITY_Brain Brain Architecture — Py]]
- 1 edge to [[_COMMUNITY_Brain Brain Yfinance — Py]]
- 1 edge to [[_COMMUNITY_Brain Brain Frontend — De (3)]]
- 1 edge to [[_COMMUNITY_Backend Financials Fetcher — Dados]]
- 1 edge to [[_COMMUNITY_Backend Financials Fetcher — Dre]]

## Top bridge nodes
- [[financials_fetcher.py]] - degree 20, connects to 5 communities
