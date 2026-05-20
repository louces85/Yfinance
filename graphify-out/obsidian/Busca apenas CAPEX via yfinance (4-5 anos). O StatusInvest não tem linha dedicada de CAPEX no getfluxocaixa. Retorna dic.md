---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py"
type: "rationale"
community: "Backend Financials Fetcher"
location: "L289"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_financials_fetcher
---

# Busca apenas CAPEX via yfinance \(4-5 anos\). O StatusInvest não tem linha dedicada de CAPEX no getfluxocaixa. Retorna dict { "ano\_str": valor\_negativo } ou {} em caso de falha. CAPEX é negativo no yfinance \(saída de caixa\).

## Connections
- [[_fetch_capex_yf()]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_financials_fetcher
