---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/decision_service.py"
type: "rationale"
community: "Backend Decision Service"
location: "L1"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_decision_service
---

# Serviço de decisão de compra. Lê os ativos qualificados de monitoring\_stocks.json, atualiza o preço via Google Finance, correlaciona com o histórico de 6 meses e calcula métricas de entrada. Persiste em data/decision\_stocks.json. Campos no JSON de saída \(o

## Connections
- [[decision_service.py]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_decision_service
