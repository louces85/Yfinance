---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py"
type: "rationale"
community: "Backend Financials Fetcher"
location: "L358"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_financials_fetcher
---

# Fluxo de Caixa combinado: - Fonte primária: StatusInvest getfluxocaixa \(10+ anos\) → fco, da, fcf\_livre, investing, financing, etc. - Complemento: yfinance para 'capex' \(linha dedicada, 4-5 anos\) + 'fcf' calculado como FCO - |capex| Fallback para yfinance c

## Connections
- [[_fetch_fluxo_caixa()]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_financials_fetcher
