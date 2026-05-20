---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/price_service.py"
type: "rationale"
community: "Backend Price Service — Pre \\(2\\)"
location: "L200"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_price_service_pre_2
---

# Busca o preço ao vivo e persiste no JSON. Se force=False e o preço ainda está dentro do intervalo mínimo, retorna o preço já salvo sem fazer nova requisição. Retorna o preço \(novo ou cacheado\) ou None em caso de falha.

## Connections
- [[update()]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_price_service_pre_2
