---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py"
type: "rationale"
community: "Backend Financials Fetcher"
location: "L144"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_financials_fetcher
---

# Busca dados históricos do StatusInvest para um endpoint \('getdre' ou 'getativos'\). Retorna dict: { nome\_indicador\_raw: { "ano\_str": valor\_float\_ou\_None, ... } } ou {} em caso de qualquer falha. Estrutura da resposta: data.grid com linhas isHeader/isData e

## Connections
- [[_fetch_statusinvest()]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_financials_fetcher
