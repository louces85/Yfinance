---
type: community
cohesion: 0.07
members: 52
---

# Backend Stock Repository

**Cohesion:** 0.07
**Members:** 52 nodes

## Members
- [[_load()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[_now()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[_save()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Escrita atômica grava em arquivo temporário e substitui com os.replace. Garante que leitores concorrentes nunca vejam JS]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_all_financials()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_all_history()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_all_indicators()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_all_prices()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_all_valuations()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_financials()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_history()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_indicators_by_ticker()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_invalid_tickers()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_monitoring_stocks()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_price()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_ranked_valuations()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_tickers_list()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_valid_tickers()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_validity()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[get_valuation()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Grava múltiplos preços de uma vez — uma única leitura+escrita no JSON.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Gravaatualiza a entrada de histórico de um ticker. entry deve conter os campos definidos no schema de stock_history.json]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Gravaatualiza o preço atual de um ticker.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Gravaatualiza o status de validade de um ticker.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Gravaatualiza o valuation de um ticker.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Gravaatualiza os demonstrativos históricos de um ticker. entry deve conter as seções 'dre', 'balanco', 'fluxo_caixa'.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Gravasubstitui o monitoring_stocks.json com os tickers que passaram nos filtros de pré-qualificação do valuation_calcula]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[is_ticker_valid()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Repositório central de acesso aos dados JSON. Todos os serviços leem e escrevem exclusivamente por aqui.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna a entrada de histórico (minmax 6m + dividendos) de um ticker.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna a lista de stocks monitoradas.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna a lista de todos os tickers cadastrados.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna apenas os tickers marcados como válidos.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna o bloco de demonstrativos históricos de um ticker, ou None.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna o dicionário de indicadores de um ticker específico.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna o mapa completo ticker - entry de demonstrativos históricos.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna o mapa completo ticker - entry de preços.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna o status de validade de um ticker.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna o último preço válido do ticker, ou None se não existir.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna o valuation calculado de um ticker.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna os tickers marcados como inválidos.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna todos os registros de indicadores fundamentalistas.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna todos os valuations com rank = min_rank, ordenados por rank DESC e p_now_p_min ASC.]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[Retorna True se o ticker está marcado como válido em stock_validity.json. Tickers sem entrada no JSON são tratados como ]] - rationale - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[save_financials()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[save_history()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[save_monitoring_stocks()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[save_price()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[save_prices_batch()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[save_validity()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[save_valuation()]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py
- [[stock_repository.py]] - code - /home/fabiano/Documents/Yfinance/src/backend/repositories/stock\_repository.py

## Connections to other communities
- 1 edge to [[_COMMUNITY_Brain Brain Architecture — Py]]
- 1 edge to [[_COMMUNITY_Brain Brain Yfinance — Py]]
- 1 edge to [[_COMMUNITY_Claude]]

## Top bridge nodes
- [[stock_repository.py]] - degree 31, connects to 3 communities
