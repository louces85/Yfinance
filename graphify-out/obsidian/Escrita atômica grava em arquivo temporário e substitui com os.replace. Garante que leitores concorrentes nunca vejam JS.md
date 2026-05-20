---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/repositories/stock_repository.py"
type: "rationale"
community: "Backend Stock Repository"
location: "L33"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_stock_repository
---

# Escrita atômica: grava em arquivo temporário e substitui com os.replace. Garante que leitores concorrentes nunca vejam JSON incompleto/corrompido.

## Connections
- [[_save()]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_stock_repository
