# Brain YFinance — Arquitetura, Classes e Diagramas

> Parte 2/4 do brain. Para filosofias → `brain_overview.md`. Para cálculos/fórmulas → `brain_calculations.md`. Para UI/dados/limitações → `brain_frontend.md`.

---

## 3. Arquitetura Geral e Fluxo de Dados

### Pipeline Completo

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FONTES DE DADOS                              │
│                                                                     │
│  Google Finance   Yahoo Finance (yfinance)   StatusInvest   B3 XLS │
│  (scraping)       (lib Python)               (API não-oficial)     │
└───────┬───────────────────┬─────────────────────┬──────────────────┘
        │                   │                     │
        ▼                   ▼                     ▼
┌───────────────┐  ┌────────────────────┐  ┌────────────────────────┐
│ stock_prices  │  │  stock_history     │  │  financials_history    │
│ .json         │  │  .json             │  │  .json                 │
│               │  │                   │  │                        │
│ Preço atual   │  │ 6m: min/max preço  │  │ 10 anos:               │
│ Cache 30 min  │  │ 5a: dividendos     │  │  DRE (receita, EBIT,  │
│               │  │ 5a: lucro líquido  │  │  EBITDA, lucro, ROE)  │
│               │  │ payout ratio       │  │  Balanço (ativos,     │
│               │  │ Buffett FCF/Owner  │  │  passivos, PL)        │
│               │  │ Tendências 4a      │  │  Fluxo de Caixa       │
└───────┬───────┘  └────────┬───────────┘  └────────────┬───────────┘
        │                   │                            │
        └───────────────────┼────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │     all_indicators.json     │
              │  (StatusInvest exportado)   │
              │                             │
              │ P/L, P/VP, ROE, ROIC,       │
              │ margens, dívidas, CAGR,     │
              │ VPA, LPA, EV/EBIT, PEG...  │
              └─────────────┬───────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │   valuation_calculator.py   │
              │                             │
              │  21 critérios binários      │
              │  Score Ponderado (0-100)    │
              │  Piotroski F-Score (0-9)    │
              │  Buffett Moat Score (0-10)  │
              │  Zonas de preço             │
              └─────────────┬───────────────┘
                            │
              ┌─────────────┴────────────┐
              ▼                          ▼
    ┌─────────────────┐       ┌────────────────────┐
    │ valuations.json │       │ monitoring_stocks  │
    │                 │       │ .json              │
    │ Valuation       │       │                    │
    │ completo por    │       │ ~127 tickers        │
    │ ticker          │       │ pré-qualificados   │
    └────────┬────────┘       │ sort: score DESC   │
             │                └─────────┬──────────┘
             │                          │
             └──────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │     decision_service.py     │  ◄── Roda a cada 30 min
              │                             │       (scheduler Flask)
              │  + Preço real atualizado    │
              │  + Recalcula zona           │
              │  + p_now_p_min              │
              │  + gain_pct, dy_real        │
              │  + Medalhas: Gold/Bronze    │
              │  + Selo Buffett             │
              │  + Setor/BEST               │
              │  + unified_rank (BRank)     │
              └─────────────┬───────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │    decision_stocks.json     │
              │                             │
              │ ~127 ações ordenadas por    │
              │ p_now_p_min ASC             │
              │ (mais próximo do suporte    │
              │  = primeiro da lista)       │
              └─────────────┬───────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │       api_server.py         │
              │        (Flask REST)         │
              │                             │
              │  GET /api/decision          │
              │  GET /api/portfolio         │
              │  GET /api/chart/<ticker>    │
              │  GET /api/favoritos         │
              │  GET /api/radar             │
              │  GET /api/swing             │  ← swing_data.json (cache diário)
              │  GET /api/swing/chart/<t>   │  ← on-demand: yfinance + séries
              │  POST /api/swing/refresh    │  ← força run() em background
              │  GET /api/swing/refresh/... │  ← status (running, updated_at)
              │  ...                        │
              └─────────────┬───────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │     Frontend (index.html)   │
              │     JS Vanilla              │
              │                             │
              │  Screening / Carteira /     │
              │  Favoritos / Radar / Swing  │
              └─────────────────────────────┘
```

### Padrão de Persistência — Atomic Write

Todos os arquivos JSON são escritos atomicamente para evitar corrupção em caso de falha de processo:

```python
# Padrão usado em stock_repository.py
import tempfile, os

with tempfile.NamedTemporaryFile('w', dir=data_dir, delete=False, suffix='.tmp') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    tmp_path = f.name

os.replace(tmp_path, final_path)  # Operação atômica no Linux
```

### Intervalos de Atualização

| Dado | Intervalo | Motivo |
|------|-----------|--------|
| Preço atual | 30 min | Cache para não sobrecarregar Google Finance |
| stock_history | 7 dias | Dividendos e financials são anuais |
| financials_history | 30 dias | DRE e Balanço mudam trimestralmente |
| decision_stocks | 30 min | Scheduler automático |
| market_data | 30 min | Scheduler automático (junto com decision_stocks) |
| swing_data | 1× por dia | `_swing_update_loop` verifica a cada 1h se dados > 23h — evita 127 calls yfinance a cada 30 min |
| swing_data (manual) | sob demanda | `POST /api/swing/refresh` força a coleta agora (botão ⟳ no toolbar Swing), ignorando a regra das 23h. Roda em background (1-3 min) |
| swing/chart on-demand | por clique | `GET /api/swing/chart/<ticker>` busca yfinance na hora (~1–2s) |

---

## 4. Árvore de Arquivos do Backend

```
YFINANCE_REFACTOR/
├── frontend/
│   └── index.html              ← SPA completo (JS vanilla, ~3800 linhas)
│
└── backend/
    ├── api_server.py           ← Flask app + scheduler de 30 min
    │
    ├── config/
    │   ├── __init__.py
    │   └── rules.py            ← TODOS os thresholds e constantes
    │
    ├── repositories/
    │   ├── __init__.py
    │   └── stock_repository.py ← Camada de dados: leitura/escrita atômica dos JSONs
    │
    ├── services/
    │   ├── __init__.py
    │   ├── stock_validator.py      ← Valida tickers via yfinance
    │   ├── price_service.py        ← Classe PriceService (injetável, com testes)
    │   ├── price_fetcher.py        ← Versão procedural do price_service
    │   ├── history_fetcher.py      ← 6m preços + 5a dividendos + Buffett metrics
    │   ├── buffett_fetcher.py      ← Fase 2 (FCF/OE) e Fase 3 (tendências 4a)
    │   ├── financials_fetcher.py   ← DRE + Balanço + FCF via StatusInvest (10 anos)
    │   ├── valuation_calculator.py ← Motor principal: 21 critérios + 3 scores
    │   ├── decision_service.py     ← Gera decision_stocks.json (30 min)
    │   ├── portfolio_service.py    ← Lê B3 XLS e calcula posições
    │   ├── market_service.py       ← Índices de mercado via yfinance (30 min)
    │   └── swing_journal_service.py ← Diário de operações de swing (compra/venda + P&L + DARF)
    │
    ├── tests/
    │   ├── conftest.py
    │   ├── __init__.py
    │   └── test_price_service.py
    │
    ├── data/
    │   ├── all_indicators.json     ← Indicadores fundamentalistas (StatusInvest, exportado)
    │   ├── all_sectors.json        ← Ticker → {setor, subsetor, segmento}
    │   ├── stocks_list.json        ← Lista mestre de tickers monitorados
    │   ├── stock_validity.json     ← Status de validação por ticker
    │   ├── stock_prices.json       ← Preços atuais com timestamp
    │   ├── stock_history.json      ← 6m preços + 5a dividendos + Buffett
    │   ├── financials_history.json ← 10 anos de DRE, Balanço e Cashflow
    │   ├── valuations.json         ← Valuation completo por ticker
    │   ├── monitoring_stocks.json  ← Tickers pré-qualificados (score DESC)
    │   ├── decision_stocks.json    ← Decisões finais (p_now_p_min ASC) + unified_rank
    │   ├── market_data.json        ← Índices de mercado (IBOV, USD, S&P, Ouro) — 30 min
    │   ├── favoritos.json          ← Favoritos do usuário
    │   ├── radar.json              ← Alertas de preço
    │   ├── swing_positions.json    ← Diário de operações de swing (abertas + fechadas) — manual
    │   └── B3/
    │       └── Custodia*.xls       ← Arquivo de custódia exportado da B3
    │
    └── libs/
        └── transcribe_meeting.py   ← Utilitário de transcrição de áudio (Whisper)
```

---

## 5. Descrição das Classes e Arquivos Principais

### 5.1 `config/rules.py` — Todos os Thresholds

Arquivo central com **todas as constantes** da aplicação. Nunca há magic numbers espalhados no código — tudo vem daqui.

```python
# Exemplos de constantes
BASIN_BASE    = 0.06   # Yield-alvo base (compra moderada — Bazin)
BASIN_MIN     = 0.05   # Yield-alvo mínimo (monitorar)
BASIN_MAX     = 0.08   # Yield-alvo agressivo (compra forte — Barsi)
P_L_MAX       = 15.0   # P/L máximo (Graham)
P_VP_MAX      = 1.5    # P/VP máximo (Graham)
WEIGHTED_SCORE_MAX = 40.0  # Soma dos pesos → normalizado para 100
```

---

### 5.2 `repositories/stock_repository.py` — Camada de Dados

Ponto central de acesso a todos os arquivos JSON. **Nunca acesse os JSONs diretamente nos services** — sempre via repository.

**Funções principais:**

| Função | Arquivo | Operação |
|--------|---------|---------|
| `get/save_price(ticker)` | stock_prices.json | R/W |
| `get/save_history(ticker)` | stock_history.json | R/W |
| `get/save_valuation(ticker)` | valuations.json | R/W |
| `get/save_financials(ticker)` | financials_history.json | R/W |
| `get/save_validity(ticker)` | stock_validity.json | R/W |
| `get_monitoring_stocks()` | monitoring_stocks.json | R |
| `save_monitoring_stocks(data)` | monitoring_stocks.json | W |
| `get_all_indicators()` | all_indicators.json | R (read-only) |
| `get_indicators_by_ticker(ticker)` | all_indicators.json | R |
| `get_valid_tickers()` | stock_validity.json | R |

---

### 5.3 `services/stock_validator.py`

Verifica se um ticker existe e tem dados suficientes no mercado.

**Lógica:**
```python
df = yfinance.Ticker(f"{ticker}.SA").history(period="6mo")
# Inválido se: df vazio, < 10 pregões, preço zero, ou exceção do yfinance
```

**Persistência:** `stock_validity.json`
**Intervalo:** 7 dias mínimo entre validações (`VALIDATION_INTERVAL_DAYS`)

---

### 5.4 `services/price_service.py` — Preço em Tempo Real

**Hierarquia de fallback (3 camadas):**

```
1. Google Finance (scraping HTML) — fonte primária
      URL: https://www.google.com/finance/quote/{TICKER}:BVMF
      Extração: CSS class "YMlKec fxKbKc"
      Regex: r'[\d]+[.,][\d]+'
      Retry: 3 tentativas com pausa de 1s entre cada uma
      Falha típica: "price block not found" (throttling ou estrutura HTML alterada)
         ↓ se todas as 3 falharem
2. yfinance (TICKER.SA) — fallback de API
      yfinance.Ticker("{TICKER}.SA").history(period="5d")
      Usa o último Close disponível nos últimos 5 dias
      Salva em stock_prices.json caso bem-sucedido
         ↓ se yfinance também falhar
3. Cache local (stock_prices.json) — último recurso
      Retorna o último preço salvo com sucesso
      Não atualiza o timestamp — ticker segue em ciclo normal na próxima rodada
      Se nunca houve preço salvo → retorna None → ticker excluído do decision_stocks
```

**Logs gerados durante fallback:**
```
[TICKER] tentativa 1/3 falhou (price block not found) — aguardando 1.0s
[TICKER] tentativa 2/3 falhou (price block not found) — aguardando 1.0s
[TICKER] todas as 3 tentativas falharam (price block not found)
[TICKER] tentando yfinance como fallback
[TICKER] yfinance OK: R$8.22          ← ou:
[TICKER] usando preço cacheado R$8.22
```

**Cache:** 30 min (`PRICE_UPDATE_INTERVAL_HOURS = 0.5` em `config/rules.py`)

**Classe `PriceService`:**
- Construtor com injeção de dependências (`repository`, `http_client_factory`) — facilita testes
- `fetch_from_google(ticker, retries=3, retry_delay=1.0)` → float ou None
- `fetch_from_yfinance(ticker)` → float ou None (último Close de 5d)
- `update(ticker, force=False)` → executa a hierarquia de 3 camadas + persiste
- `update_all(tickers, force, delay=0.3)` → batch com rate limiting

---

### 5.5 `services/history_fetcher.py`

Coleta dados históricos de 2 fontes e calcula métricas derivadas.

**O que coleta:**

```
Via yfinance:
  ├── Ticker.history(period="6mo")
  │     → price_min_6m, price_max_6m
  │     → close_avg_6m, volume_avg_6m
  │     → accumulation_score (% dias com P < avg_P e V < avg_V)
  │
  ├── Ticker.dividends (últimos 5 anos)
  │     → dividends_per_year {ano: valor}
  │     → avg_dividends_5y (ponderado: pesos [1,2,3,4,5])
  │     → dividends_sum_12m
  │     → paid_dividends_5_years (bool)
  │     → dividend_growing (último ano >= 90% do máximo anterior)
  │
  └── Ticker.financials["Net Income"] (últimos 5 anos)
        → net_income_per_year {ano: valor}
        → positive_income_5_years (bool)

Via StatusInvest:
  └── GET /acao/payoutresult?code={ticker_lower}
        → payout (campo "actual", float)

Via buffett_fetcher.py (chamado internamente):
  ├── Fase 2: buffett_cashflow {}
  │     → fcf, owner_earnings, fcf_lucro_ratio, capex_lucro_ratio
  │     → fcf_positivo, owner_earnings_positivo
  │     → fcf_quality_ok (fcf_lucro_ratio >= 0.80)
  │     → capex_moat_ok (capex_lucro_ratio <= 0.25)
  │
  └── Fase 3: buffett_trends {}
        → 4 anos de: margem_bruta, margem_liquida, roe, fcf,
                     divida_liq, capex_receita, sga_receita
        → trend por métrica: CRESCENDO | ESTAVEL | CAINDO | INDEFINIDO
```

**Intervalo:** 7 dias (`HISTORY_UPDATE_INTERVAL_DAYS`)

---

### 5.6 `services/buffett_fetcher.py` — Fases 2 e 3 do Moat

**Fase 2 — Qualidade de Caixa:**

```python
# Fonte: yfinance cashflow_stmt, income_stmt (últimos 4 anos, ano mais recente)
capex          = abs(cashflow["Capital Expenditure"])  # yfinance retorna negativo
da             = cashflow["Depreciation And Amortization"]
fco            = cashflow["Operating Cash Flow"]
net_income     = income_stmt["Net Income"]

fcf            = fco - capex                          # Fluxo de Caixa Livre
owner_earnings = net_income + da - capex              # Owner Earnings (Buffett)
fcf_lucro_ratio  = fcf / net_income                   # Qualidade do lucro
capex_lucro_ratio = capex / net_income                # Intensidade de CapEx
```

**Fase 3 — Tendências:**

```python
# Para cada métrica, calcula tendência via regressão linear (numpy)
def _calc_tendencia(valores: list, threshold_rel=0.05):
    # slope = coeficiente angular da regressão linear
    # mean  = média dos valores
    # Se slope / mean > +5%: CRESCENDO
    # Se slope / mean < -5%: CAINDO
    # Senão: ESTAVEL
    # Se < 2 pontos: INDEFINIDO
```

**Métricas com tendência calculada:**
`margem_bruta`, `margem_liquida`, `roe`, `fcf`, `divida_liq`, `capex_receita`, `sga_receita`

---

### 5.7 `services/financials_fetcher.py` — DRE 10 Anos do StatusInvest

Coleta o histórico longo de demonstrativos financeiros via API não oficial do StatusInvest.

**Endpoints StatusInvest:**

```
DRE (Demonstração de Resultado):
  GET https://statusinvest.com.br/acao/getdre
  Params: code={ticker}, type=0, range.min={ano}, range.max={ano}
  Campos: receita_liquida, lucro_bruto, ebitda, ebit, lucro_liquido,
          roe, roic, margem_bruta, margem_liquida, divida_bruta, divida_liquida

Balanço Patrimonial:
  GET https://statusinvest.com.br/acao/getativos
  Campos: ativo_total, ativo_circulante, caixa_equivalentes,
          passivo_total, passivo_circulante, patrimonio_liquido

Fluxo de Caixa:
  GET https://statusinvest.com.br/acao/getfluxocaixa
  Campos: fco (operacional), da (depreciação/amortização),
          fcf_livre, capex (via yfinance — mais confiável), financing
```

**Parse de valores StatusInvest:**
```python
# StatusInvest retorna valores formatados em PT-BR
"3.938,54 M"  → 3_938_540_000.0   (milhões × 10⁶)
"1,23 B"      → 1_230_000_000.0   (bilhões × 10⁹)
"-9,80"       → -9.8
"10,07%"      → 10.07
"-"           → None
```

**Rate limiting:** 1.5 segundos entre chamadas para não ser bloqueado
**Intervalo de atualização:** 30 dias (`FINANCIALS_UPDATE_INTERVAL_DAYS`)
**Anos coletados:** 10 (`FINANCIALS_YEARS`)

> **Nota importante sobre CapEx:** A linha de CapEx do StatusInvest não é confiável. Por isso, o CapEx é buscado diretamente do `yfinance.cashflow` e combinado com os dados do SI.

**Flags de linha de comando:**

| Comando | Comportamento |
|---------|--------------|
| `python financials_fetcher.py` | Atualiza todos os tickers válidos (respeita intervalo 30 dias) |
| `python financials_fetcher.py BBAS3 PETR4` | Tickers específicos |
| `python financials_fetcher.py --force` | Força todos, ignora intervalo |
| `python financials_fetcher.py BBAS3 --force` | Força ticker específico |
| `python financials_fetcher.py --update` | **Detecta e atualiza apenas tickers defasados** (≥ 2 anos) |
| `python financials_fetcher.py --update --force` | Força todos os defasados, ignora intervalo |

**Detecção de tickers defasados (`get_stale_tickers`):**

```python
def get_stale_tickers(min_gap: int = 2) -> List[tuple]:
    """
    Lê financials_history.json e retorna tickers onde:
        ano_atual - ultimo_ano_dre >= min_gap

    Exemplo em 2026: dados até 2024 → gap=2 → defasado.
                     dados até 2025 → gap=1 → OK.

    Retorna lista de (ticker, ultimo_ano) ordenada por último ano ASC.
    """
```

```python
def _latest_dre_year(entry: dict) -> Optional[int]:
    """Extrai o maior ano inteiro das chaves da DRE, excluindo 'ttm'."""
```

**Comportamento de `--update`:**
- `--update` sem `--force`: respeita o intervalo de 30 dias → tickers defasados mas buscados recentemente são SKIPados (evita re-fetch desnecessário quando o StatusInvest ainda não publicou o ano mais recente)
- `--update --force`: força o fetch de todos os defasados independente de quando foram buscados pela última vez

---

### 5.8 `services/valuation_calculator.py` — Motor Principal

**O coração da aplicação.** Combina todos os dados e aplica os 21 critérios de investimento.

**Entradas:**
- `all_indicators.json` → indicadores fundamentalistas (P/L, P/VP, ROE, ROIC, margens, dívidas, CAGR...)
- `stock_history.json` → histórico 6m + dividendos 5a + Buffett metrics
- `stock_prices.json` → preço atual
- `financials_history.json` → DRE/Balanço 10 anos (para tendências do Moat)

**Saídas:**
- `valuations.json` → valuation completo por ticker
- `monitoring_stocks.json` → apenas os tickers que passaram pelos filtros, ordenados por score

**Funções principais:**

| Função | Retorno |
|--------|---------|
| `calculate(ticker)` | dict com valuation completo |
| `_calc_buffett_moat_score(...)` | dict com score 0-10, flags, cashflow_values, trends |
| `_calc_piotroski(...)` | dict com score 0-9, flags individuais |
| `_calc_weighted_score(flags)` | dict com score 0-100 |
| `_calc_zone(price, t6, t8, t5)` | string: COMPRA_FORTE \| COMPRA \| MONITORAR \| CARO |

**Detector de resultado não recorrente (`resultado_nao_recorrente`):**

Calculado dentro de `_calc_buffett_moat_score()` após construir as tendências estendidas. Detecta anos com spike de margem líquida causado por eventos tributários/extraordinários não recorrentes.

```python
# Condições simultâneas para ativar o flag:
# 1. ML do último ano >= 1.8× a média dos 4 anos anteriores
# 2. Crescimento de receita do último ano < 10%
# Se ambos verdadeiros: resultado_nao_recorrente = True
```

O campo `resultado_nao_recorrente: bool` é persistido em `valuations.json` dentro de `buffett_moat.trends_values`. Ver detalhes da fórmula em `brain_calculations.md` seção 7.11.

**Linha de comando:** `python valuation_calculator.py TICKER1 TICKER2` para recalcular tickers específicos.

---

### 5.9 `services/decision_service.py`

Gera a visão final de entrada com **preço em tempo real**. Roda automaticamente a cada 30 minutos.

**O que faz para cada ticker:**
1. Busca preço atual (Google Finance via PriceService)
2. Carrega valuation pré-calculado (valuations.json)
3. Carrega histórico 6m (stock_history.json)
4. Recalcula zona com preço atual
5. Calcula métricas de entrada: `p_now_p_min`, `gain_pct`, `dy_real`
6. Calcula acumulação 30d: `yfinance.Ticker.history(period="1mo")`
7. Avalia medalhas: `is_gold`, `is_bronze`, `is_below_vpa_target`
8. Avalia Selo Buffett: `is_buffett_seal`
9. Busca setor e classifica `is_best`
10. **Calcula `unified_rank` via `_calc_unified_rank(entry)`** — ver brain_calculations.md seção 7.9

**Ordenação:** por `p_now_p_min` ASC → ações mais próximas do suporte aparecem primeiro.

**Campos adicionais expostos em `decision_stocks.json`:**
- `owner_earnings_positivo` (bool) — usado como gate no BRank
- `unified_rank` (float 0-100) — Ranking Unificado Buffett × Barsi × Bazin

---

### 5.10 `services/portfolio_service.py`

Lê o arquivo XLS de custódia exportado da B3 e enriquece com análise fundamentalista.

**Processo:**
1. Encontra o arquivo XLS mais recente em `data/B3/`
2. Parse com `xlrd` → {ticker, qtd, preco_medio, total_investido}
3. Consolida duplicatas (mesmo ticker em múltiplas corretoras)
4. Separa Ações de FIIs
5. **Para ações**: busca valuation pré-calculado + preços em paralelo (10 workers)
6. **Para FIIs**: busca `dividends_sum_12m` via yfinance em paralelo (8 workers)
7. Calcula: valor_atual, retorno R$/%, DY s/PM, `unified_rank`

**Recomendações geradas:**
```
AUMENTAR     → zone COMPRA_FORTE + rank ≥ 12 + p_now_p_min ≤ 1.15
COMPRAR_MAIS → zone COMPRA ou COMPRA_FORTE + rank ≥ 9
AGUARDAR     → zone MONITORAR ou rank 6-8
AVALIAR_VENDA→ rank < 6 ou zone CARO
```

**unified_rank na carteira:**
- Ações em `decision_stocks.json` → valor pré-computado (paridade exata com screening)
- Ações FORA_CRITERIOS → calculado com `_calc_unified_rank` a partir do `forced_val`

---

### 5.11 `api_server.py` — Flask + Scheduler

**Endpoints principais:**

| Endpoint | Método | Fonte | Descrição |
|----------|--------|-------|-----------|
| `/api/decision` | GET | decision_stocks.json | Lista principal de decisões |
| `/api/market` | GET | market_data.json | Índices de mercado (IBOV, USD, S&P, Ouro) |
| `/api/portfolio` | GET | B3 XLS + valuations | Carteira com análise |
| `/api/chart/<ticker>` | GET | yfinance (live) | OHLCV 6 meses para gráfico |
| `/api/history/<ticker>` | GET | stock_history.json | Histórico de dividendos/preços |
| `/api/valuation/<ticker>` | GET | valuations.json | Valuation detalhado |
| `/api/dividends_ytd/<ticker>` | GET | yfinance (live) | Dividendos acumulados no ano |
| `/api/favoritos` | GET/POST | favoritos.json | Lista de favoritos |
| `/api/radar` | GET/POST | radar.json | Alertas de preço |
| `/api/radar/alerts` | GET | radar + prices + swing_positions | Alertas disparados. Mescla os alertas do Radar (`buy`/`sell`) com os de **stop/alvo das operações de swing abertas** (`type` `stop`/`target`, `source: "swing"`, com `id` da operação) via `swing_journal_service.position_alerts()`, usando preço ao vivo |
| `/api/radar/dismiss` | POST | radar.json | Silencia alerta por 24h |
| `/api/swing` | GET | swing_data.json | Lista de sinais swing (cache diário) |
| `/api/swing/chart/<ticker>` | GET | yfinance (live) | Séries de indicadores p/ gráfico |
| `/api/swing/refresh` | POST | swing_service | Força run() em background (guard `_do_swing_run`) |
| `/api/swing/refresh/status` | GET | flag + swing_data | `{running, updated_at}` p/ polling do frontend |
| `/api/swing/positions` | GET | swing_journal_service | `{open, closed, darf}` — P&L ao vivo + vendas do mês |
| `/api/swing/positions` | POST | swing_positions.json | Cria operação aberta (campos: ticker, qty, entry_price, entry_date, stop, target) |
| `/api/swing/positions/<id>/close` | POST | swing_positions.json | Registra venda (exit_price, exit_date) → move p/ histórico |
| `/api/swing/positions/<id>` | PUT/DELETE | swing_positions.json | Edita / exclui operação |

**Diário de swing (DARF):** `swing_journal_service` enriquece operações abertas com preço atual (`get_all_prices()`, fallback p/ `swing_data.json`), calcula P&L flutuante/realizado e soma as **vendas do mês corrente** vs. o limite de isenção do swing comum (`SWING_DARF_MONTHLY_LIMIT` = R$ 20.000; alerta em `SWING_DARF_WARN_RATIO` = 90%). Status `ok`/`warn`/`over`.

**Scheduler:**
```python
# Daemon thread que roda em background
def _scheduler_loop():
    _run_decision()   # roda imediatamente ao iniciar
    while True:
        time.sleep(REFRESH_INTERVAL_HOURS * 3600)  # 30 min
        _run_decision()

def _run_decision():
    decision_service.run()   # atualiza decision_stocks.json
    market_service.fetch()   # atualiza market_data.json
```

**Scheduler de swing + refresh manual:** thread separada `_swing_update_loop` verifica a cada 1h se `swing_data.json` tem > 23h. Tanto o scheduler quanto o botão `⟳ Atualizar` (POST `/api/swing/refresh`) passam pelo helper `_do_swing_run()`, protegido por `_swing_lock` + flag `_swing_running` — só uma execução de `swing_service.run()` por vez. O refresh manual roda em thread daemon e o frontend acompanha via `GET /api/swing/refresh/status`.

```python
_swing_lock = threading.Lock()
_swing_running = False

def _do_swing_run():
    global _swing_running
    with _swing_lock:
        if _swing_running:
            return False        # já rodando — ignora
        _swing_running = True
    try:
        swing_service.run()
    finally:
        with _swing_lock:
            _swing_running = False
    return True
```

---

### 5.12 `services/market_service.py` — Índices de Mercado

Busca 4 índices via `yfinance.fast_info` (sem download de histórico — rápido) e persiste em `market_data.json`.

**Símbolos monitorados:**

| Chave | Símbolo yfinance | Descrição |
|-------|-----------------|-----------|
| `IBOV` | `^BVSP` | Ibovespa (pontos) |
| `USD` | `BRL=X` | Dólar / Real |
| `SP500` | `^GSPC` | S&P 500 (pontos) |
| `OURO` | `GC=F` | Ouro (USD/oz) |

**Estrutura de `market_data.json`:**
```json
{
  "last_updated": "2026-04-16T10:30:00",
  "data": {
    "IBOV":  { "price": 137420.0, "change_pct": 0.8  },
    "USD":   { "price": 5.12,     "change_pct": -0.3 },
    "SP500": { "price": 5234.0,   "change_pct": 0.5  },
    "OURO":  { "price": 2320.0,   "change_pct": 1.2  }
  }
}
```

**Funções:** `fetch()` → busca + salva (atomic write) | `load()` → lê do disco

**Atualização:** a cada 30 min, chamado em `_run_decision()` no scheduler do `api_server.py`.

---

## 6. Diagramas de Sequência

### Diagrama 1 — Pipeline de Inicialização (Execução Manual)

```
Operador          stock_validator   yfinance          repo              JSON
   │                    │               │               │                │
   │  validate_all()    │               │               │                │
   ├───────────────────►│               │               │                │
   │                    │ .history(6mo) │               │                │
   │                    ├──────────────►│               │                │
   │                    │◄── DataFrame ─┤               │                │
   │                    │     save_validity(ticker)     │                │
   │                    ├──────────────────────────────►│                │
   │                    │               │               ├── atomic_write►│ stock_validity.json
   │                    │               │               │                │
   │  update_all()      history_fetcher │               │                │
   ├───────────────────────────────────►│               │                │
   │                    │  .history(), .dividends,      │                │
   │                    │  .financials  │               │                │
   │                    │         [buffett_fetcher]     │                │
   │                    │  yfinance cashflow, income    │                │
   │                    │  → FCF, OE, tendências 4a     │                │
   │                    │     save_history(ticker)      │                │
   │                    ├──────────────────────────────►│                │
   │                    │               │               ├── atomic_write►│ stock_history.json
   │                    │               │               │                │
   │  update_all()      financials_fetcher              │                │
   ├──────────────────────────────────────────────────► │                │
   │                    │     StatusInvest:             │                │
   │                    │     /getdre, /getativos,      │                │
   │                    │     /getfluxocaixa (10 anos)  │                │
   │                    │     save_financials(ticker)   │                │
   │                    ├──────────────────────────────►│                │
   │                    │               │               ├── atomic_write►│ financials_history.json
   │                    │               │               │                │
   │  calculate_all()   valuation_calc  │               │                │
   ├──────────────────────────────────────────────────► │                │
   │                    │  calc_21_criteria()           │                │
   │                    │  calc_buffett_moat() ──── 3 fases              │
   │                    │  calc_piotroski()             │                │
   │                    │  calc_weighted_score()        │                │
   │                    │     save_valuation(ticker)    │                │
   │                    ├──────────────────────────────►│                │
   │                    │               │               ├── atomic_write►│ valuations.json
   │                    │     save_monitoring_stocks()  │                │
   │                    ├──────────────────────────────►│                │
   │                    │               │               ├── atomic_write►│ monitoring_stocks.json
```

---

### Diagrama 2 — Ciclo de Decisão Automático (a cada 30 min)

```
Flask Scheduler    decision_service   PriceService   Google Finance   repo
      │                   │                │                │           │
      │  run()            │                │                │           │
      ├──────────────────►│                │                │           │
      │                   │  get_monitoring_stocks()                    │
      │                   ├───────────────────────────────────────────►│
      │                   │◄── ~127 tickers ──────────────────────────┤
      │         [loop para cada ticker]    │                │           │
      │                   │  update(ticker)│                │           │
      │                   ├───────────────►│                │           │
      │                   │                │  GET /finance/quote/BVMF  │
      │                   │                ├───────────────►│           │
      │                   │                │◄── HTML preço ─┤           │
      │                   │◄── price_now ──┤                │           │
      │                   │  get_valuation() + get_history()            │
      │                   ├───────────────────────────────────────────►│
      │                   │◄── valuation{} + history{} ───────────────┤
      │                   │  _calc_zone, p_now_p_min, gain_pct         │
      │                   │  _calc_accumulation_30d() via yfinance     │
      │                   │  is_gold, is_bronze, is_buffett_seal       │
      │                   │  _calc_unified_rank(entry) → BRank         │
      │                   │  sort by p_now_p_min ASC                   │
      │                   │  save_decision_stocks()                    │
      │                   ├───────────────────────────────────────────►│
      │                   │               │                │            ├── atomic_write
      │                   │               │                │            │   decision_stocks.json
```

---

### Diagrama 3 — Carregamento da Carteira

```
Browser   api_server   portfolio_service   repo    ThreadPool   yfinance   Google Finance
   │           │               │             │         │            │            │
   │  GET /api/portfolio        │             │         │            │            │
   ├──────────►│               │             │         │            │            │
   │           │  load()        │             │         │            │            │
   │           ├──────────────►│             │         │            │            │
   │           │               │  parse B3 XLS (xlrd)  │            │            │
   │           │               │  consolidar tickers    │            │            │
   │           │               │  separar Ações / FIIs  │            │            │
   │           │               │  get_valuation(t)       │            │            │
   │           │               ├────────────►│         │            │            │
   │           │               │◄── val{} ───┤         │            │            │
   │           │               │  load decision_stocks → unified_rank lookup     │
   │           │               │  [10 workers paralelos — preços]   │            │
   │           │               ├────────────────────────►│          │            │
   │           │               │             │         │  price_service.update() │
   │           │               │             │         ├────────────────────────►│
   │           │               │             │         │◄── price_now ──────────┤
   │           │               │◄── prices[] ┤         │            │            │
   │           │               │  [8 workers paralelos — FII dividendos]         │
   │           │               ├────────────────────────────────────►│            │
   │           │               │  calc: retorno, DY s/PM, BRank, recomendações   │
   │           │◄── portfolio{} ┤             │         │            │            │
   │◄── JSON ──┤               │             │         │            │            │
```
