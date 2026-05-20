# Backend Financials Fetcher

> 29 nodes · cohesion 0.12

## Key Concepts

- **financials_fetcher.py** (20 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **fetch_financials()** (7 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **_fetch_fluxo_caixa()** (7 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **_fetch_statusinvest()** (6 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **_fetch_balanco()** (5 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **_fetch_dre()** (5 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **_fetch_fluxo_caixa_si()** (5 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **_map_fields()** (5 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **update_ticker()** (5 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **_has_data()** (4 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **update_all()** (4 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **_fetch_capex_yf()** (3 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **_fetch_cashflow_yf_fallback()** (3 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **_needs_update()** (3 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **parse_statusinvest_value()** (3 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **Busca Balanço Patrimonial do StatusInvest. Retorna dict com campos snake_case + '_source', ou {} em caso de falha.** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **Busca apenas CAPEX via yfinance (4-5 anos). O StatusInvest não tem linha dedicada de CAPEX no getfluxocaixa. Retorna dict { "ano_str": valor_negativo } ou {} em caso de falha. CAPEX é negativo no yfinance (saída de caixa).** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **Fallback completo para yfinance quando StatusInvest falhar. Retorna fco, capex, da, fcf (4-5 anos).** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **Busca DRE histórica do StatusInvest. Retorna dict com campos snake_case + '_source', ou {} em caso de falha.** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **Orquestra os três fetches para um ticker com rate limiting entre chamadas SI. Fluxo: _fetch_dre() → sleep(1.5s) _fetch_balanco() → sleep(1.5s) _fetch_fluxo_caixa() → sleep(1.5s) ← StatusInvest (10+ anos) + yfinance CAPEX Política de falha parcial: salva qu** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **Fluxo de Caixa combinado: - Fonte primária: StatusInvest getfluxocaixa (10+ anos) → fco, da, fcf_livre, investing, financing, etc. - Complemento: yfinance para 'capex' (linha dedicada, 4-5 anos) + 'fcf' calculado como FCO - |capex| Fallback para yfinance c** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **Busca Fluxo de Caixa do StatusInvest (getfluxocaixa) — até 10+ anos históricos. Campos principais: fco — Caixa Líquido Atividades Operacionais da — Depreciação e Amortização fcf_livre — Fluxo de Caixa Livre (FCO - Investimentos, já calculado pelo SI) inves** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **Busca dados históricos do StatusInvest para um endpoint ('getdre' ou 'getativos'). Retorna dict: { nome_indicador_raw: { "ano_str": valor_float_ou_None, ... } } ou {} em caso de qualquer falha. Estrutura da resposta: data.grid com linhas isHeader/isData e** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **True se o dict tem pelo menos uma chave sem prefixo '_'.** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- **Aplica field_map ao dict raw, retornando apenas os campos mapeados.** (1 connections) — `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`
- *... and 4 more nodes in this community*

## Relationships

- No strong cross-community connections detected

## Source Files

- `/home/fabiano/Documents/Yfinance/src/backend/services/financials_fetcher.py`

## Audit Trail

- EXTRACTED: 99 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*