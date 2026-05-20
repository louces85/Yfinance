# Backend Portfolio Service — Em

> 3 nodes · cohesion 0.67

## Key Concepts

- **load()** (4 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/portfolio_service.py`
- **_recommend()** (2 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/portfolio_service.py`
- **Lê o arquivo de custódia B3, cruza com valuations e retorna { summary, positions, fiis, fiis_summary }. - Ativo em valuations.json → dados completos + recomendação - Ativo em stocks_list mas não em valuations → incluído como "FORA_CRITERIOS" - FIIs e outro** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/portfolio_service.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `/home/fabiano/Documents/Yfinance/src/backend/services/portfolio_service.py`

## Audit Trail

- EXTRACTED: 7 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*