---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/portfolio_service.py"
type: "rationale"
community: "Backend Portfolio Service"
location: "L1"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_portfolio_service
---

# Portfolio service — lê o arquivo de custódia B3 \(XLS\) e cruza com valuations.json para gerar recomendações por ativo. Apenas ativos presentes em valuations.json são incluídos. FIIs e outros ativos sem cobertura são ignorados silenciosamente.

## Connections
- [[portfolio_service.py]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_portfolio_service
