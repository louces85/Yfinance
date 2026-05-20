---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/buffett_fetcher.py"
type: "rationale"
community: "Backend Buffett Fetcher — Cashflow"
location: "L46"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_buffett_fetcher_cashflow
---

# Busca dados de Fluxo de Caixa e DRE histórica via yfinance. Retorna dict com cashflow\_available=True e as métricas calculadas, ou {"cashflow\_available": False} em caso de qualquer falha. Campos retornados \(quando disponível\): cashflow\_available : bool cape

## Connections
- [[fetch_cashflow()]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_buffett_fetcher_cashflow
