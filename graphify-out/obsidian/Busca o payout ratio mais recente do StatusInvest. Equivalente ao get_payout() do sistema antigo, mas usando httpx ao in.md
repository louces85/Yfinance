---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/history_fetcher.py"
type: "rationale"
community: "Backend History Fetcher — Do"
location: "L60"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_history_fetcher_do
---

# Busca o payout ratio mais recente do StatusInvest. Equivalente ao get\_payout\(\) do sistema antigo, mas usando httpx ao invés de curl. O endpoint retorna uma lista de objetos; o campo 'actual' do primeiro item é o payout do período mais recente. Retorna o pa

## Connections
- [[fetch_payout()]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_history_fetcher_do
