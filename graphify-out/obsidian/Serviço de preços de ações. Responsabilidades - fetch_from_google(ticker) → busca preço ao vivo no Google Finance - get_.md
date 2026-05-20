---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/price_service.py"
type: "rationale"
community: "Backend Price Service — Pre"
location: "L50"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_price_service_pre
---

# Serviço de preços de ações. Responsabilidades: - fetch\_from\_google\(ticker\) → busca preço ao vivo no Google Finance - get\_from\_json\(ticker\) → lê o último preço salvo localmente - update\(ticker, force\) → busca ao vivo e persiste no JSON - update\_all\(tickers,

## Connections
- [[PriceService]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_price_service_pre
