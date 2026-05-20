# Backend Financials Fetcher — Dados

> 2 nodes · cohesion 1.00

## Key Concepts

- **get_stale_tickers()** (3 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **Detecta tickers com dados defasados no financials_history.json. Um ticker é considerado defasado quando: ano_atual - ultimo_ano_dre >= min_gap Exemplo em 2026: dados até 2024 → gap=2 → defasado. dados até 2025 → gap=1 → OK. Retorna lista de (ticker, ultimo** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`

## Audit Trail

- EXTRACTED: 4 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*