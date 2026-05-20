---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/price_fetcher.py"
type: "rationale"
community: "Backend Price Fetcher"
location: "L1"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_price_fetcher
---

# Serviço de coleta de preços atual via Google Finance \(scraping\). Lê os preços e persiste em data/stock\_prices.json via stock\_repository. Uso direto: python price\_fetcher.py # atualiza todos os tickers válidos python price\_fetcher.py BBAS3 PETR4 # atualiza

## Connections
- [[price_fetcher.py]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_price_fetcher
