---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py"
type: "rationale"
community: "Backend Financials Fetcher"
location: "L451"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_financials_fetcher
---

# Orquestra os três fetches para um ticker com rate limiting entre chamadas SI. Fluxo: \_fetch\_dre\(\) → sleep\(1.5s\) \_fetch\_balanco\(\) → sleep\(1.5s\) \_fetch\_fluxo\_caixa\(\) → sleep\(1.5s\) ← StatusInvest \(10+ anos\) + yfinance CAPEX Política de falha parcial: salva qu

## Connections
- [[fetch_financials()]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_financials_fetcher
