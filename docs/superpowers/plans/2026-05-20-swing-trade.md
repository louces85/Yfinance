# Swing Trade Tab — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adicionar uma aba "Swing" ao lado de Radar que calcula RSI(14), MACD(12/26/9), Bollinger Bands(20) e MA Cross(20/50) para todos os ~127 tickers do Screening, exibindo setups onde ≥ 2 indicadores disparam juntos.

**Architecture:** Um `swing_service.py` busca OHLCV diretamente do yfinance (igual ao `/api/chart`), calcula os 4 indicadores, e salva em `swing_data.json` via atomic write. Um segundo daemon thread em `api_server.py` atualiza os dados uma vez por dia, verificando idade do arquivo. O frontend segue o padrão das outras abas: `loadSwing()` → `renderSwingTable()`, com clique na linha chamando `openDetail(ticker)`.

**Tech Stack:** Python 3.8, yfinance, Flask, JS vanilla (sem framework)

**Spec:** `docs/superpowers/specs/2026-05-20-swing-trade-design.md`

---

## File Map

| Arquivo | Ação | Responsabilidade |
|---------|------|-----------------|
| `src/backend/services/swing_service.py` | **Criar** | Funções de cálculo dos 4 indicadores + `run()` que busca yfinance e salva JSON |
| `src/backend/repositories/stock_repository.py` | **Modificar** | Adicionar `save_swing_data()` e `load_swing_data()` + `"swing"` no dict PATHS |
| `src/backend/api_server.py` | **Modificar** | Endpoint `GET /api/swing` + daemon thread de atualização diária |
| `src/frontend/index.html` | **Modificar** | Botão da aba, painel HTML, funções JS de carga/renderização/sort/filter |
| `src/backend/data/swing_data.json` | **Gerado** | Saída do swing_service; não editar manualmente |
| `tests/test_swing_service.py` | **Criar** | Testes das funções de cálculo (sem chamadas reais ao yfinance) |

---

## Task 1: Repository — save/load swing_data

**Files:**
- Modify: `src/backend/repositories/stock_repository.py`

- [ ] **Step 1: Adicionar `"swing"` ao dict PATHS**

Localizar o dict `PATHS` (linha ~15) e adicionar a entrada:

```python
PATHS = {
    "indicators":         os.path.join(DATA_DIR, "all_indicators.json"),
    "stocks_list":        os.path.join(DATA_DIR, "stocks_list.json"),
    "history":            os.path.join(DATA_DIR, "stock_history.json"),
    "prices":             os.path.join(DATA_DIR, "stock_prices.json"),
    "valuations":         os.path.join(DATA_DIR, "valuations.json"),
    "validity":           os.path.join(DATA_DIR, "stock_validity.json"),
    "monitoring_stocks":  os.path.join(DATA_DIR, "monitoring_stocks.json"),
    "financials_history": os.path.join(DATA_DIR, "financials_history.json"),
    "swing":              os.path.join(DATA_DIR, "swing_data.json"),   # ← adicionar
}
```

- [ ] **Step 2: Adicionar as duas funções ao final do arquivo**

```python
# ---------------------------------------------------------------------------
# Swing data
# ---------------------------------------------------------------------------

def save_swing_data(entries):
    """Salva lista de dicts com indicadores técnicos de swing trade."""
    _save(PATHS["swing"], entries)


def load_swing_data():
    """Retorna lista de swing_data ou [] se o arquivo não existir."""
    path = PATHS["swing"]
    if not os.path.exists(path):
        return []
    return _load(path)
```

- [ ] **Step 3: Verificar que `_load` aceita lista**

O `_load` existente usa `json.load(f)` e retorna o que o JSON contém — array ou dict. Verificar que não há nenhum `.get()` hardcoded em `_load`. Confirmado: a função retorna o valor bruto, então uma lista JSON funciona corretamente.

- [ ] **Step 4: Commit**

```bash
git add src/backend/repositories/stock_repository.py
git commit -m "feat: add swing_data save/load to stock_repository"
```

---

## Task 2: Funções de cálculo técnico (TDD)

**Files:**
- Create: `tests/test_swing_service.py`
- Create: `src/backend/services/swing_service.py` (só as funções puras — sem `run()` ainda)

- [ ] **Step 1: Escrever os testes para RSI**

Criar `tests/test_swing_service.py`:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend', 'services'))

from swing_service import calc_rsi, calc_macd, calc_bb, calc_ma_cross


def test_rsi_all_gains_returns_100():
    closes = [float(i) for i in range(1, 20)]  # 19 preços sempre subindo
    rsi = calc_rsi(closes, period=14)
    assert rsi == 100.0


def test_rsi_alternating_returns_near_50():
    closes = [10.0, 11.0, 10.0, 11.0, 10.0, 11.0, 10.0, 11.0,
              10.0, 11.0, 10.0, 11.0, 10.0, 11.0, 10.0, 11.0]
    rsi = calc_rsi(closes, period=14)
    assert rsi is not None
    assert 45.0 <= rsi <= 55.0


def test_rsi_returns_none_when_insufficient_data():
    closes = [10.0, 11.0, 12.0]  # menos de period+1 pontos
    assert calc_rsi(closes, period=14) is None


def test_rsi_signal_below_30():
    # 14 quedas seguidas → RSI próximo de 0
    closes = [20.0 - i for i in range(16)]
    rsi = calc_rsi(closes, period=14)
    assert rsi is not None
    assert rsi < 30.0


def test_bb_signal_when_price_at_lower_band():
    # 20 preços iguais: std=0, banda inferior = média = preço → sinal ativo
    closes = [10.0] * 20
    upper, middle, lower, signal = calc_bb(closes)
    assert signal is True
    assert upper == middle == lower == 10.0


def test_bb_no_signal_when_price_above_lower():
    base = [10.0] * 19
    closes = base + [15.0]  # último preço bem acima da banda
    _, _, lower, signal = calc_bb(closes)
    assert signal is False
    assert closes[-1] > lower


def test_bb_returns_none_when_insufficient_data():
    closes = [10.0] * 5
    upper, middle, lower, signal = calc_bb(closes, period=20)
    assert upper is None and middle is None and lower is None and signal is False


def test_ma_cross_golden_cross():
    # MA20 = 15 (médias dos últimos 20), MA50 = 10 (médias dos últimos 50)
    # Simular: primeiros 30 valores baixos, últimos 20 altos
    closes = [10.0] * 30 + [20.0] * 20
    ma20, ma50, signal = calc_ma_cross(closes)
    assert signal is True   # MA20 > MA50


def test_ma_cross_death_cross():
    # Primeiros 30 altos, últimos 20 baixos
    closes = [20.0] * 30 + [5.0] * 20
    ma20, ma50, signal = calc_ma_cross(closes)
    assert signal is False  # MA20 < MA50


def test_ma_cross_returns_none_when_insufficient():
    closes = [10.0] * 30  # menos de 50 pontos
    ma20, ma50, signal = calc_ma_cross(closes)
    assert ma20 is None and ma50 is None and signal is False


def test_macd_returns_none_when_insufficient():
    closes = [10.0] * 20  # menos de 26+9=35 pontos
    macd_val, sig_val, bullish = calc_macd(closes)
    assert macd_val is None and sig_val is None and bullish is False


def test_macd_bullish_in_uptrend():
    # Preços crescentes → EMA12 reage mais rápido → MACD positivo
    closes = [float(i) for i in range(1, 60)]
    _, _, bullish = calc_macd(closes)
    assert bullish is True


def test_macd_bearish_in_downtrend():
    # Preços decrescentes → EMA12 cai mais rápido → MACD negativo
    closes = [float(60 - i) for i in range(60)]
    _, _, bullish = calc_macd(closes)
    assert bullish is False
```

- [ ] **Step 2: Rodar os testes — devem falhar**

```bash
cd /home/fabiano/Documents/Yfinance
python -m pytest tests/test_swing_service.py -v 2>&1 | head -20
```

Esperado: `ModuleNotFoundError: No module named 'swing_service'`

- [ ] **Step 3: Criar `swing_service.py` com as funções puras**

Criar `src/backend/services/swing_service.py`:

```python
"""
swing_service.py — Indicadores técnicos para swing trade.

Funções puras de cálculo (calc_*) + run() que busca yfinance e salva JSON.
Atualização: uma vez por dia (daemon thread em api_server.py).
"""

import math
import time
import yfinance
from datetime import datetime

import repositories.stock_repository as repo


# ---------------------------------------------------------------------------
# Funções puras de cálculo
# ---------------------------------------------------------------------------

def calc_rsi(closes, period=14):
    """Retorna RSI (0-100) ou None se dados insuficientes."""
    if len(closes) < period + 1:
        return None

    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains  = [max(d, 0.0) for d in deltas]
    losses = [max(-d, 0.0) for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0.0:
        return 100.0

    rs = avg_gain / avg_loss
    return round(100.0 - (100.0 / (1.0 + rs)), 2)


def _ema_series(values, period):
    """Retorna série completa de EMA para um período dado."""
    if len(values) < period:
        return []
    k = 2.0 / (period + 1)
    ema = sum(values[:period]) / period
    result = [ema]
    for v in values[period:]:
        ema = v * k + ema * (1.0 - k)
        result.append(ema)
    return result


def calc_macd(closes, fast=12, slow=26, signal_period=9):
    """Retorna (macd_value, signal_line, is_bullish).
    is_bullish = True quando macd_value > signal_line no último fechamento.
    Retorna (None, None, False) se dados insuficientes."""
    if len(closes) < slow + signal_period:
        return None, None, False

    ema_fast = _ema_series(closes, fast)
    ema_slow = _ema_series(closes, slow)

    if not ema_fast or not ema_slow:
        return None, None, False

    n = len(ema_slow)
    ema_fast_aligned = ema_fast[-n:]
    macd_line = [ema_fast_aligned[i] - ema_slow[i] for i in range(n)]

    sig_series = _ema_series(macd_line, signal_period)
    if not sig_series:
        return None, None, False

    macd_val = macd_line[-1]
    sig_val  = sig_series[-1]
    return round(macd_val, 4), round(sig_val, 4), macd_val > sig_val


def calc_bb(closes, period=20, num_std=2):
    """Retorna (upper, middle, lower, signal).
    signal = True quando preço atual <= banda inferior.
    Retorna (None, None, None, False) se dados insuficientes."""
    if len(closes) < period:
        return None, None, None, False

    window   = closes[-period:]
    mean     = sum(window) / period
    variance = sum((x - mean) ** 2 for x in window) / period
    std      = math.sqrt(variance)

    upper  = round(mean + num_std * std, 2)
    middle = round(mean, 2)
    lower  = round(mean - num_std * std, 2)
    signal = closes[-1] <= lower

    return upper, middle, lower, signal


def calc_ma_cross(closes, fast=20, slow=50):
    """Retorna (ma_fast, ma_slow, is_golden_cross).
    is_golden_cross = True quando MA20 > MA50.
    Retorna (None, None, False) se dados insuficientes."""
    if len(closes) < slow:
        return None, None, False

    ma_fast = round(sum(closes[-fast:]) / fast, 2)
    ma_slow = round(sum(closes[-slow:]) / slow, 2)
    return ma_fast, ma_slow, ma_fast > ma_slow
```

- [ ] **Step 4: Rodar os testes — devem passar**

```bash
python -m pytest tests/test_swing_service.py -v
```

Esperado: todos os testes passando (`PASSED`).

- [ ] **Step 5: Commit**

```bash
git add tests/test_swing_service.py src/backend/services/swing_service.py
git commit -m "feat: add swing trade technical indicator functions with tests"
```

---

## Task 3: swing_service.run() — fetch yfinance + salvar JSON

**Files:**
- Modify: `src/backend/services/swing_service.py` (adicionar `run()` ao final)

- [ ] **Step 1: Adicionar função `run()` ao final de `swing_service.py`**

```python
# ---------------------------------------------------------------------------
# Execução principal
# ---------------------------------------------------------------------------

def run():
    """Busca OHLCV do yfinance para todos os tickers do decision_stocks.json,
    calcula os 4 indicadores e salva em swing_data.json."""
    # Usar os mesmos ~127 tickers pré-qualificados do Screening
    monitoring = repo.get_monitoring_stocks()
    tickers = [s["ticker"] for s in monitoring]

    results = []
    for ticker in tickers:
        try:
            yf_obj = yfinance.Ticker(ticker + ".SA")
            hist   = yf_obj.history(period="6mo")

            if hist.empty or len(hist) < 60:
                continue

            closes = []
            for v in hist["Close"]:
                try:
                    f = float(v)
                    if not math.isnan(f):
                        closes.append(f)
                except (TypeError, ValueError):
                    pass

            if len(closes) < 60:
                continue

            rsi_val    = calc_rsi(closes)
            rsi_signal = rsi_val is not None and rsi_val < 30.0

            macd_val, macd_sig_line, macd_bullish = calc_macd(closes)
            bb_upper, bb_middle, bb_lower, bb_signal = calc_bb(closes)
            ma20, ma50, ma_signal = calc_ma_cross(closes)

            signals_count = sum([
                1 if rsi_signal  else 0,
                1 if macd_bullish else 0,
                1 if bb_signal   else 0,
                1 if ma_signal   else 0,
            ])

            results.append({
                "ticker":           ticker,
                "price":            round(closes[-1], 2),
                "rsi":              rsi_val,
                "rsi_signal":       rsi_signal,
                "macd_value":       macd_val,
                "macd_signal_line": macd_sig_line,
                "macd_bullish":     macd_bullish,
                "bb_upper":         bb_upper,
                "bb_middle":        bb_middle,
                "bb_lower":         bb_lower,
                "bb_signal":        bb_signal,
                "ma20":             ma20,
                "ma50":             ma50,
                "ma_signal":        ma_signal,
                "signals_count":    signals_count,
                "is_setup":         signals_count >= 2,
                "updated_at":       datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            })

            time.sleep(0.3)  # evitar rate limit do yfinance

        except Exception as e:
            print("[swing_service] ERRO em {}: {}".format(ticker, e))
            continue

    results.sort(key=lambda x: x["signals_count"], reverse=True)
    repo.save_swing_data(results)
    print("[swing_service] {} tickers calculados, {} setups.".format(
        len(results), sum(1 for r in results if r["is_setup"])
    ))
    return results
```

- [ ] **Step 2: Testar run() manualmente (não usa yfinance de verdade nos testes unitários)**

Rodar diretamente para verificar que não há erro de importação:

```bash
cd /home/fabiano/Documents/Yfinance/src/backend
python -c "from services import swing_service; print('OK')"
```

Esperado: `OK`

- [ ] **Step 3: Rodar os testes existentes para confirmar que nada quebrou**

```bash
cd /home/fabiano/Documents/Yfinance
python -m pytest tests/test_swing_service.py -v
```

Esperado: todos passando.

- [ ] **Step 4: Commit**

```bash
git add src/backend/services/swing_service.py
git commit -m "feat: add swing_service.run() with yfinance OHLCV fetch"
```

---

## Task 4: API endpoint + scheduler diário

**Files:**
- Modify: `src/backend/api_server.py`

- [ ] **Step 1: Adicionar import do swing_service**

Localizar o bloco de imports dos services (por volta da linha 33):

```python
from services import decision_service
from services import market_service
from services import swing_service   # ← adicionar
```

- [ ] **Step 2: Adicionar endpoint GET /api/swing**

Localizar a seção de endpoints (antes do bloco do scheduler, ~linha 380). Adicionar após o último endpoint existente:

```python
@app.route("/api/swing")
def get_swing():
    data = repo.load_swing_data()
    return jsonify(data)
```

- [ ] **Step 3: Adicionar o scheduler diário**

Localizar a função `_scheduler_loop` (linha ~401). Logo abaixo da definição de `_scheduler_loop`, adicionar:

```python
def _swing_update_loop():
    """Verifica a cada hora se swing_data.json tem mais de 23h.
    Se sim, roda swing_service.run(). Garante dados frescos diariamente
    sem sobrecarregar o yfinance (127 tickers a cada 30 min seria excessivo)."""
    while True:
        needs_update = True
        data = repo.load_swing_data()
        if data:
            try:
                last = datetime.strptime(data[0]["updated_at"], "%Y-%m-%dT%H:%M:%S")
                age_hours = (datetime.now() - last).total_seconds() / 3600.0
                needs_update = age_hours >= 23.0
            except Exception:
                needs_update = True

        if needs_update:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("[swing-scheduler] {} — iniciando swing_service...".format(now))
            try:
                swing_service.run()
                print("[swing-scheduler] {} — concluído.".format(now))
            except Exception as e:
                print("[swing-scheduler] ERRO: {}".format(e))

        time.sleep(3600)  # verificar a cada 1 hora
```

- [ ] **Step 4: Iniciar o thread do swing scheduler no bloco `if __name__ == "__main__"`**

Localizar o bloco de inicialização (linha ~413):

```python
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    t = threading.Thread(target=_scheduler_loop, daemon=True, name="decision-scheduler")
    t.start()

    # ← adicionar estas duas linhas:
    t2 = threading.Thread(target=_swing_update_loop, daemon=True, name="swing-scheduler")
    t2.start()

    print(f"\n  YFINANCE API  →  http://localhost:{port}")
    print(f"  Frontend      →  {FRONTEND_DIR}")
    print(f"  Scheduler     →  decision_service a cada {REFRESH_INTERVAL_HOURS}h\n")
    app.run(host="0.0.0.0", port=port, debug=False)
```

- [ ] **Step 5: Verificar que o servidor sobe sem erro**

```bash
cd /home/fabiano/Documents/Yfinance/src/backend
python api_server.py &
sleep 3
curl -s http://localhost:5000/api/swing | python -m json.tool | head -20
kill %1
```

Esperado: JSON array (vazio `[]` se swing_data.json ainda não existir, ou com dados se já existir).

- [ ] **Step 6: Commit**

```bash
git add src/backend/api_server.py
git commit -m "feat: add /api/swing endpoint and daily swing scheduler"
```

---

## Task 5: Frontend — aba Swing (HTML + CSS + JS)

**Files:**
- Modify: `src/frontend/index.html`

Esta task tem 4 sub-partes: (a) botão de tab, (b) painel HTML, (c) CSS, (d) JS.

### 5a — Botão da aba

- [ ] **Step 1: Adicionar botão "Swing" após o botão "Radar" (~linha 829–834)**

Localizar:
```html
    <button class="tab-btn" data-tab="radar">
```

Logo após o fechamento desse botão (após `</button>`), adicionar:

```html
    <button class="tab-btn" data-tab="swing">
      <svg width="14" height="14" viewBox="0 0 16 16" fill="none" style="vertical-align:-2px;margin-right:4px">
        <path d="M2 12 L6 7 L9 10 L13 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="13" cy="4" r="1.5" fill="currentColor"/>
      </svg>
      Swing
    </button>
```

### 5b — Painel HTML

- [ ] **Step 2: Adicionar `div#swingView` após `div#radarView`**

Localizar o fechamento do `div#radarView` e adicionar logo após:

```html
<!-- ─── Swing Trade ──────────────────────────────────────────────── -->
<div id="swingView" style="display:none">

  <!-- Toolbar -->
  <div class="swing-toolbar">
    <div class="swing-cards">
      <div class="swing-scard">
        <div class="swing-val swing-green" id="swingCountSetup">—</div>
        <div class="swing-lbl">SETUPs</div>
      </div>
      <div class="swing-scard">
        <div class="swing-val swing-yellow" id="swingCountWatch">—</div>
        <div class="swing-lbl">Monitorar</div>
      </div>
      <div class="swing-scard">
        <div class="swing-val swing-blue" id="swingCountTotal">—</div>
        <div class="swing-lbl">Analisados</div>
      </div>
    </div>
    <div class="swing-sep"></div>
    <button class="swing-toggle" id="swingToggle" onclick="_swingToggleFilter()">● Só SETUPs</button>
    <span class="swing-updated" id="swingUpdated"></span>
  </div>

  <!-- Tabela -->
  <div class="table-wrap">
    <table class="swing-table" id="swingTable">
      <thead>
        <tr>
          <th style="text-align:left" onclick="_swingSort('ticker')">Ativo <span id="swingArrow_ticker" class="sort-arrow">↕</span></th>
          <th onclick="_swingSort('price')">Preço (R$) <span id="swingArrow_price" class="sort-arrow">↕</span></th>
          <th onclick="_swingSort('rsi')">RSI (14) <span id="swingArrow_rsi" class="sort-arrow">↕</span></th>
          <th>MACD</th>
          <th>Bollinger</th>
          <th>MA Cross</th>
          <th onclick="_swingSort('signals_count')">Sinais <span id="swingArrow_signals_count" class="sort-arrow">↑</span></th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody id="swingTbody"></tbody>
    </table>
  </div>

</div>
```

### 5c — CSS

- [ ] **Step 3: Adicionar CSS da aba Swing**

Localizar o bloco `/* ─── Radar ─── */` no CSS (~linha 742). Logo antes dele, adicionar:

```css
/* ─── Swing Trade ───────────────────────────────────────────────── */
.swing-toolbar { background: var(--surface); border-bottom: 1px solid var(--border); padding: 8px 16px; display: flex; align-items: center; gap: 12px; }
.swing-cards { display: flex; gap: 8px; }
.swing-scard { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 6px 12px; font-size: 11px; text-align: center; min-width: 70px; }
.swing-val { font-size: 16px; font-weight: 700; }
.swing-lbl { color: var(--muted); margin-top: 2px; }
.swing-green  { color: var(--green); }
.swing-yellow { color: var(--yellow); }
.swing-blue   { color: var(--blue); }
.swing-sep { width: 1px; height: 28px; background: var(--border); }
.swing-toggle { padding: 5px 12px; border-radius: 6px; border: 1px solid var(--border); background: rgba(63,185,80,.15); color: var(--green); font-size: 11px; cursor: pointer; }
.swing-toggle.off { background: rgba(139,148,158,.1); color: var(--muted); }
.swing-updated { font-size: 11px; color: var(--muted); }
.swing-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.swing-table th { font-size: 10px; color: var(--muted); font-weight: 400; padding: 6px 10px; text-align: center; border-bottom: 1px solid var(--border); white-space: nowrap; cursor: pointer; position: sticky; top: 0; background: var(--bg); z-index: 1; }
.swing-table th:first-child { text-align: left; }
.swing-table th:hover { color: var(--text); }
.swing-table td { padding: 7px 10px; border-bottom: 1px solid rgba(255,255,255,.04); white-space: nowrap; text-align: center; }
.swing-table td:first-child { text-align: left; }
.swing-table tbody tr { cursor: pointer; }
.swing-table tbody tr:hover td { background: rgba(88,166,255,.08); }
.swing-row-setup { background: rgba(63,185,80,.04); }
.swing-ind-on  { display:inline-block; padding:2px 6px; border-radius:3px; font-size:10px; font-weight:600; background:rgba(63,185,80,.2); color:var(--green); }
.swing-ind-off { display:inline-block; padding:2px 6px; border-radius:3px; font-size:10px; font-weight:600; background:rgba(139,148,158,.1); color:var(--muted); }
.swing-badge-setup { display:inline-block; padding:2px 7px; border-radius:4px; font-size:10px; font-weight:600; background:rgba(63,185,80,.2); color:var(--green); border:1px solid rgba(63,185,80,.4); }
.swing-badge-none  { display:inline-block; padding:2px 7px; border-radius:4px; font-size:10px; background:rgba(139,148,158,.1); color:var(--muted); border:1px solid var(--border); }
.swing-rsi-low  { color: var(--green); font-weight: 700; }
.swing-rsi-norm { color: var(--muted); }
.swing-sig-bar  { display:flex; gap:3px; justify-content:center; align-items:center; }
.swing-dot      { width:8px; height:8px; border-radius:50%; }
.swing-dot-on   { background: var(--green); }
.swing-dot-off  { background: var(--border); }
.swing-sig-n    { font-size:11px; font-weight:700; margin-left:4px; }
```

### 5d — JavaScript

- [ ] **Step 4: Adicionar variáveis de estado e funções JS**

Localizar a seção de JS do Radar (~linha 3544, `async function loadRadarFromServer()`). Logo antes dela, adicionar:

```javascript
// ─── Swing Trade ──────────────────────────────────────────────────
let _swingData      = [];
let _swingSortCol   = 'signals_count';
let _swingSortAsc   = false;
let _swingOnlySetup = true;
let _swingLoaded    = false;

async function loadSwing() {
  try {
    const res  = await fetch('/api/swing');
    _swingData = await res.json();
    _swingLoaded = true;
    renderSwingTable();
  } catch (e) {
    console.error('loadSwing error', e);
  }
}

function _swingToggleFilter() {
  _swingOnlySetup = !_swingOnlySetup;
  const btn = document.getElementById('swingToggle');
  if (_swingOnlySetup) {
    btn.classList.remove('off');
    btn.textContent = '● Só SETUPs';
  } else {
    btn.classList.add('off');
    btn.textContent = '○ Todos';
  }
  renderSwingTable();
}

function _swingSort(col) {
  if (_swingSortCol === col) {
    _swingSortAsc = !_swingSortAsc;
  } else {
    _swingSortCol = col;
    _swingSortAsc = col !== 'signals_count';  // signals_count: desc por padrão
  }
  renderSwingTable();
}

function renderSwingTable() {
  const data = _swingOnlySetup
    ? _swingData.filter(function(d) { return d.is_setup; })
    : _swingData;

  // Ordenar
  const col = _swingSortCol;
  const asc = _swingSortAsc;
  data.sort(function(a, b) {
    const va = a[col] != null ? a[col] : (asc ? Infinity : -Infinity);
    const vb = b[col] != null ? b[col] : (asc ? Infinity : -Infinity);
    if (va < vb) return asc ? -1 : 1;
    if (va > vb) return asc ? 1 : -1;
    return 0;
  });

  // Atualizar setas de sort
  ['ticker','price','rsi','signals_count'].forEach(function(c) {
    const el = document.getElementById('swingArrow_' + c);
    if (!el) return;
    if (c === col) {
      el.textContent = asc ? '↑' : '↓';
      el.style.opacity = '1';
      el.style.color = 'var(--blue)';
    } else {
      el.textContent = '↕';
      el.style.opacity = '0.4';
      el.style.color = '';
    }
  });

  // Atualizar cards de resumo
  const total  = _swingData.length;
  const setups = _swingData.filter(function(d) { return d.is_setup; }).length;
  const watch  = _swingData.filter(function(d) { return d.signals_count === 1; }).length;
  document.getElementById('swingCountSetup').textContent = setups;
  document.getElementById('swingCountWatch').textContent = watch;
  document.getElementById('swingCountTotal').textContent = total;

  // Timestamp
  const updEl = document.getElementById('swingUpdated');
  if (_swingData.length && _swingData[0].updated_at) {
    const d = new Date(_swingData[0].updated_at.replace('T', ' '));
    const hh = String(d.getHours()).padStart(2, '0');
    const mm = String(d.getMinutes()).padStart(2, '0');
    updEl.textContent = 'Atualizado: ' + hh + ':' + mm;
  }

  // Renderizar tbody
  const tbody = document.getElementById('swingTbody');
  if (!data.length) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:var(--muted);padding:32px">Nenhum setup encontrado</td></tr>';
    return;
  }

  tbody.innerHTML = data.map(function(d) {
    var rsiClass   = (d.rsi != null && d.rsi < 30) ? 'swing-rsi-low' : 'swing-rsi-norm';
    var rsiText    = d.rsi != null ? d.rsi.toFixed(1) : '—';
    var macdHtml   = d.macd_bullish
      ? '<span class="swing-ind-on">↑ Bull</span>'
      : '<span class="swing-ind-off">↓ Bear</span>';
    var bbHtml     = d.bb_signal
      ? '<span class="swing-ind-on">≤ Inf</span>'
      : '<span class="swing-ind-off">Normal</span>';
    var maHtml     = d.ma_signal
      ? '<span class="swing-ind-on">Golden</span>'
      : '<span class="swing-ind-off">Death</span>';

    var dots = [d.rsi_signal, d.macd_bullish, d.bb_signal, d.ma_signal].map(function(s) {
      return '<div class="swing-dot ' + (s ? 'swing-dot-on' : 'swing-dot-off') + '"></div>';
    }).join('');
    var countColor = d.signals_count >= 3 ? 'var(--green)' : (d.signals_count === 2 ? 'var(--yellow)' : 'var(--muted)');

    var badge = d.is_setup
      ? '<span class="swing-badge-setup">SETUP</span>'
      : '<span class="swing-badge-none">–</span>';

    var rowClass = d.is_setup ? 'swing-row-setup' : '';

    return '<tr class="' + rowClass + '" onclick="openDetail(\'' + d.ticker + '\')">' +
      '<td><span style="font-weight:600;color:var(--blue)">' + d.ticker + '</span></td>' +
      '<td>' + (d.price != null ? d.price.toFixed(2) : '—') + '</td>' +
      '<td><span class="' + rsiClass + '">' + rsiText + '</span></td>' +
      '<td>' + macdHtml + '</td>' +
      '<td>' + bbHtml + '</td>' +
      '<td>' + maHtml + '</td>' +
      '<td><div class="swing-sig-bar">' + dots + '<span class="swing-sig-n" style="color:' + countColor + '">' + d.signals_count + '/4</span></div></td>' +
      '<td>' + badge + '</td>' +
    '</tr>';
  }).join('');
}
```

- [ ] **Step 5: Integrar a aba no tab-switcher existente (~linha 3159)**

Localizar o bloco:
```javascript
document.querySelectorAll('.tab-btn:not([data-sub])').forEach(btn => {
```

Dentro do `addEventListener('click', ...)`, adicionar `swingView` às linhas de show/hide e a chamada `loadSwing()`:

```javascript
    document.getElementById('screeningView').style.display  = tab === 'screening' ? '' : 'none';
    document.getElementById('portfolioView').style.display  = tab === 'carteira'  ? '' : 'none';
    document.getElementById('favoritosView').style.display  = tab === 'favoritos' ? '' : 'none';
    document.getElementById('radarView').style.display      = tab === 'radar'     ? '' : 'none';
    document.getElementById('swingView').style.display      = tab === 'swing'     ? '' : 'none';   // ← adicionar
    if (tab === 'carteira')  { if (!_portfolioLoaded) loadPortfolio(); }
    if (tab === 'favoritos') renderFavoritos();
    if (tab === 'radar')     renderRadarView();
    if (tab === 'swing')     { if (!_swingLoaded) loadSwing(); else renderSwingTable(); }  // ← adicionar
```

- [ ] **Step 6: Commit**

```bash
git add src/frontend/index.html
git commit -m "feat: add Swing Trade tab with RSI/MACD/BB/MA Cross table"
```

---

## Task 6: Smoke test e verificação manual

- [ ] **Step 1: Rodar todos os testes unitários**

```bash
cd /home/fabiano/Documents/Yfinance
python -m pytest tests/test_swing_service.py -v
```

Esperado: todos passando.

- [ ] **Step 2: Verificar que swing_service importa corretamente**

```bash
cd /home/fabiano/Documents/Yfinance/src/backend
python -c "from services import swing_service; print('imports OK')"
```

Esperado: `imports OK`

- [ ] **Step 3: Rodar swing_service manualmente para 2 tickers**

```bash
cd /home/fabiano/Documents/Yfinance/src/backend
python - <<'EOF'
import sys
sys.path.insert(0, '.')
import yfinance, math, time
from datetime import datetime
from services.swing_service import calc_rsi, calc_macd, calc_bb, calc_ma_cross

for ticker in ['BBAS3', 'TAEE11']:
    yf = yfinance.Ticker(ticker + '.SA')
    hist = yf.history(period='6mo')
    closes = [float(v) for v in hist['Close'] if not math.isnan(float(v))]
    rsi = calc_rsi(closes)
    _, _, macd_bull = calc_macd(closes)
    _, _, _, bb_sig = calc_bb(closes)
    _, _, ma_sig = calc_ma_cross(closes)
    sigs = sum([rsi is not None and rsi < 30, macd_bull, bb_sig, ma_sig])
    print(f'{ticker}: RSI={rsi} MACD_bull={macd_bull} BB={bb_sig} MA={ma_sig} -> {sigs}/4 {"SETUP" if sigs>=2 else ""}')
    time.sleep(1)
EOF
```

Esperado: linhas com valores reais de RSI, MACD, etc. para os dois tickers.

- [ ] **Step 4: Subir o servidor e abrir o frontend**

```bash
cd /home/fabiano/Documents/Yfinance/src/backend
python api_server.py
```

Abrir `http://localhost:5000`, clicar na aba "Swing". Na primeira abertura, a tabela mostrará `—` nos cards enquanto o scheduler roda em background (ou vazia se swing_data.json não existir). Para forçar a carga imediata, acionar via endpoint:

```bash
curl -s http://localhost:5000/api/swing | python -m json.tool | head -30
```

- [ ] **Step 5: Verificar comportamentos**

- [ ] Clicar em um ticker na aba Swing abre o modal completo (gráfico, cards de preço, ranking no setor)
- [ ] Toggle "Só SETUPs" alterna entre mostrar todos e só setups
- [ ] Colunas RSI, Sinais e Preço são ordenáveis (clique no header)
- [ ] Cards de resumo mostram contagens corretas

- [ ] **Step 6: Commit final**

```bash
git add .
git commit -m "feat: swing trade tab complete - smoke test passed"
```
