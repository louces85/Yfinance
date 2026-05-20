---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/stock_validator.py"
type: "rationale"
community: "Backend Stock Validator"
location: "L1"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_stock_validator
---

# Serviço de validação de tickers. Verifica periodicamente se cada ticker ainda está ativo e com dados disponíveis. Um ticker é marcado como INVÁLIDO quando ocorre qualquer das condições: - yfinance não retorna histórico de preço nos últimos 6 meses \(sem neg

## Connections
- [[stock_validator.py]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_stock_validator
