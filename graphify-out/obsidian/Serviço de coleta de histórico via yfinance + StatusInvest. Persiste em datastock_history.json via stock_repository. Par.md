---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/history_fetcher.py"
type: "rationale"
community: "Backend History Fetcher"
location: "L1"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_history_fetcher
---

# Serviço de coleta de histórico via yfinance + StatusInvest. Persiste em data/stock\_history.json via stock\_repository. Para cada ticker válido \(conforme stock\_validity.json\) busca: - Preço mínimo e máximo dos últimos 6 meses \(yfinance\) - Dividendos pagos po

## Connections
- [[history_fetcher.py]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_history_fetcher
