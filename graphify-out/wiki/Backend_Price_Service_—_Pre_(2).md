# Backend Price Service — Pre (2)

> 3 nodes · cohesion 0.67

## Key Concepts

- **.update()** (7 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/price_service.py`
- **.update_all()** (2 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/price_service.py`
- **Busca o preço ao vivo e persiste no JSON. Se force=False e o preço ainda está dentro do intervalo mínimo, retorna o preço já salvo sem fazer nova requisição. Retorna o preço (novo ou cacheado) ou None em caso de falha.** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/price_service.py`

## Relationships

- No strong cross-community connections detected

## Source Files

- `/home/fabiano/Documents/Yfinance/src/backend/services/price_service.py`

## Audit Trail

- EXTRACTED: 10 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*