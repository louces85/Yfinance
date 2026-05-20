---
source_file: "/home/fabiano/Documents/Yfinance/src/backend/services/decision_service.py"
type: "rationale"
community: "Backend Decision Service — Pelo"
location: "L48"
tags:
  - graphify/rationale
  - graphify/extracted
  - community/backend_decision_service_pelo
---

# Busca setor pelo ticker exato; fallback pelo radical de 4 letras. Ex: SAPR4 não encontrado → tenta qualquer chave que comece com 'SAPR'. Cobre todas as classes \(ON/PN/UNT\) da mesma empresa.

## Connections
- [[_lookup_sector()]] - `rationale\_for` [EXTRACTED]

#graphify/rationale #graphify/extracted #community/backend_decision_service_pelo
