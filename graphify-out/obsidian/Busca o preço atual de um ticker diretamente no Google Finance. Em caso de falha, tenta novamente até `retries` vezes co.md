---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/price_service.py"
type: "rationale"
community: "Backend Price Service — De"
location: "L87"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_price_service_de
---

# Busca o preço atual de um ticker diretamente no Google Finance. Em caso de falha, tenta novamente até \`retries\` vezes com pausa de \`retry\_delay\` segundos. Retorna o preço como float ou None se todas as tentativas falharem.

## Connections
- [[fetch_from_google()]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_price_service_de
