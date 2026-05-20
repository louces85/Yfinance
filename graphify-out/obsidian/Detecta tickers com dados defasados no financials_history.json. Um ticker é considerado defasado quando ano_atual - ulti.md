---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py"
type: "rationale"
community: "Backend Financials Fetcher — Dados"
location: "L425"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_financials_fetcher_dados
---

# Detecta tickers com dados defasados no financials\_history.json. Um ticker é considerado defasado quando: ano\_atual - ultimo\_ano\_dre >= min\_gap Exemplo em 2026: dados até 2024 → gap=2 → defasado. dados até 2025 → gap=1 → OK. Retorna lista de \(ticker, ultimo

## Connections
- [[get_stale_tickers()]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_financials_fetcher_dados
