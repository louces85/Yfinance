# Backend Decision Service — Pelo

> 2 nodes · cohesion 1.00

## Key Concepts

- **_lookup_sector()** (3 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/decision_service.py`
- **Busca setor pelo ticker exato; fallback pelo radical de 4 letras. Ex: SAPR4 não encontrado → tenta qualquer chave que comece com 'SAPR'. Cobre todas as classes (ON/PN/UNT) da mesma empresa.** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/decision_service.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `/home/fabiano/Documents/Yfinance/src/backend/services/decision_service.py`

## Audit Trail

- EXTRACTED: 4 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*