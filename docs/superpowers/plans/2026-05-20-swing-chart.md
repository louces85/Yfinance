# Swing Trade Chart Modal — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adicionar um ícone 📈 ao lado do badge SETUP na aba Swing que, ao clicado, abre um modal com 3 painéis Chart.js mostrando Preço+BB+MAs, RSI(14) e MACD(12/26/9) ao longo dos 6 meses.

**Architecture:** Novas funções de série em `swing_service.py` retornam arrays completos (um valor por fechamento, `None` onde dados são insuficientes). Um novo endpoint `GET /api/swing/chart/<ticker>` busca OHLCV do yfinance on-demand e retorna todas as séries. O frontend exibe um modal com 3 `<canvas>` Chart.js sobrepostos verticalmente, reutilizando o tema escuro e as constantes de cor já existentes.

**Tech Stack:** Python 3.8, yfinance, Flask, Chart.js 4.4.0 (já carregado), JS vanilla

---

## File Map

| Arquivo | Ação | Responsabilidade |
|---------|------|-----------------|
| `src/backend/services/swing_service.py` | **Modificar** | Adicionar 4 funções de série: `calc_rsi_series`, `calc_bb_series`, `calc_ma_series`, `calc_macd_series` |
| `src/backend/api_server.py` | **Modificar** | Adicionar `GET /api/swing/chart/<ticker>` |
| `src/frontend/index.html` | **Modificar** | Ícone na tabela, modal HTML, CSS, funções JS |
| `tests/test_swing_service.py` | **Modificar** | Testes das funções de série |

---

## Task 1: Funções de série (TDD)

**Files:**
- Modify: `tests/test_swing_service.py`
- Modify: `src/backend/services/swing_service.py`

- [ ] **Step 1: Adicionar testes das séries em `tests/test_swing_service.py`**

Acrescentar ao final do arquivo:

```python
from swing_service import (
    calc_rsi_series, calc_bb_series, calc_ma_series, calc_macd_series
)


# ─── RSI série ────────────────────────────────────────────────────

def test_rsi_series_length_matches_closes():
    closes = [float(i) for i in range(1, 21)]  # 20 preços
    assert len(calc_rsi_series(closes, period=14)) == 20


def test_rsi_series_first_period_are_none():
    closes = [float(i) for i in range(1, 21)]
    series = calc_rsi_series(closes, period=14)
    assert all(v is None for v in series[:14])
    assert series[14] is not None


def test_rsi_series_last_matches_scalar():
    closes = [float(i) for i in range(1, 30)]
    assert calc_rsi_series(closes, period=14)[-1] == calc_rsi(closes, period=14)


# ─── Bollinger série ───────────────────────────────────────────────

def test_bb_series_length_matches_closes():
    closes = [10.0] * 30
    r = calc_bb_series(closes, period=20)
    assert len(r["upper"]) == len(r["middle"]) == len(r["lower"]) == 30


def test_bb_series_first_period_minus1_are_none():
    closes = [10.0] * 30
    r = calc_bb_series(closes, period=20)
    assert all(v is None for v in r["upper"][:19])
    assert r["upper"][19] is not None


def test_bb_series_last_matches_scalar():
    closes = [10.0 + float(i) * 0.1 for i in range(30)]
    series = calc_bb_series(closes, period=20)
    _, _, lower_scalar, _ = calc_bb(closes, period=20)
    assert series["lower"][-1] == lower_scalar


# ─── MA série ──────────────────────────────────────────────────────

def test_ma_series_length_matches_closes():
    closes = [float(i) for i in range(1, 60)]
    r = calc_ma_series(closes, fast=20, slow=50)
    assert len(r["ma20"]) == len(r["ma50"]) == 59


def test_ma_series_none_for_insufficient_slow():
    closes = [float(i) for i in range(1, 60)]
    r = calc_ma_series(closes, fast=20, slow=50)
    assert all(v is None for v in r["ma50"][:49])
    assert r["ma50"][49] is not None


def test_ma_series_last_matches_scalar():
    closes = [float(i) for i in range(1, 60)]
    r = calc_ma_series(closes, fast=20, slow=50)
    ma20_scalar, ma50_scalar, _ = calc_ma_cross(closes, fast=20, slow=50)
    assert r["ma20"][-1] == ma20_scalar
    assert r["ma50"][-1] == ma50_scalar


# ─── MACD série ────────────────────────────────────────────────────

def test_macd_series_length_matches_closes():
    closes = [float(i) for i in range(1, 80)]
    r = calc_macd_series(closes)
    assert len(r["macd_line"]) == len(r["signal_line"]) == len(r["histogram"]) == 79


def test_macd_series_last_macd_matches_scalar():
    closes = [float(i) for i in range(1, 80)]
    series = calc_macd_series(closes)
    scalar_macd, scalar_sig, _ = calc_macd(closes)
    last_macd = next(v for v in reversed(series["macd_line"]) if v is not None)
    last_sig  = next(v for v in reversed(series["signal_line"]) if v is not None)
    assert last_macd == scalar_macd
    assert last_sig  == scalar_sig


def test_macd_series_histogram_is_macd_minus_signal():
    closes = [float(i) for i in range(1, 80)]
    r = calc_macd_series(closes)
    for i, h in enumerate(r["histogram"]):
        if h is not None:
            assert abs(h - (r["macd_line"][i] - r["signal_line"][i])) < 1e-6
```

- [ ] **Step 2: Rodar — devem falhar**

```bash
cd /home/fabiano/Documents/Yfinance
python3 -m pytest tests/test_swing_service.py -k "series" -v 2>&1 | head -15
```

Esperado: `ImportError: cannot import name 'calc_rsi_series'`

- [ ] **Step 3: Adicionar as 4 funções de série ao final da seção de funções puras em `swing_service.py`**

Localizar o comentário `# ---------------------------------------------------------------------------` que separa as funções puras do `run()`. Inserir antes dele:

```python
# ---------------------------------------------------------------------------
# Funções de série (retornam array completo — um valor por fechamento)
# ---------------------------------------------------------------------------

def calc_rsi_series(closes, period=14):
    """RSI para cada fechamento. None para os primeiros 'period' elementos."""
    n = len(closes)
    if n <= period:
        return [None] * n

    deltas = [closes[i] - closes[i - 1] for i in range(1, n)]
    gains  = [max(d, 0.0) for d in deltas]
    losses = [max(-d, 0.0) for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    def _rsi(g, l):
        if l == 0.0:
            return 100.0
        return round(100.0 - 100.0 / (1.0 + g / l), 2)

    result = [None] * period + [_rsi(avg_gain, avg_loss)]
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        result.append(_rsi(avg_gain, avg_loss))

    return result  # len == n


def calc_bb_series(closes, period=20, num_std=2):
    """Bollinger Bands para cada fechamento. None enquanto janela incompleta."""
    n = len(closes)
    upper  = [None] * n
    middle = [None] * n
    lower  = [None] * n

    for i in range(period - 1, n):
        window   = closes[i - period + 1 : i + 1]
        mean     = sum(window) / period
        variance = sum((x - mean) ** 2 for x in window) / period
        std      = math.sqrt(variance)
        upper[i]  = round(mean + num_std * std, 2)
        middle[i] = round(mean, 2)
        lower[i]  = round(mean - num_std * std, 2)

    return {"upper": upper, "middle": middle, "lower": lower}


def calc_ma_series(closes, fast=20, slow=50):
    """SMA rápida e lenta para cada fechamento. None enquanto janela incompleta."""
    n      = len(closes)
    ma_fast = [None] * n
    ma_slow = [None] * n

    for i in range(fast - 1, n):
        ma_fast[i] = round(sum(closes[i - fast + 1 : i + 1]) / fast, 2)

    for i in range(slow - 1, n):
        ma_slow[i] = round(sum(closes[i - slow + 1 : i + 1]) / slow, 2)

    return {"ma20": ma_fast, "ma50": ma_slow}


def calc_macd_series(closes, fast=12, slow=26, signal_period=9):
    """MACD line, signal line e histograma para cada fechamento. None onde insuficiente."""
    n = len(closes)
    empty = {"macd_line": [None] * n, "signal_line": [None] * n, "histogram": [None] * n}

    ema_fast = _ema_series(closes, fast)   # len = n - fast + 1
    ema_slow = _ema_series(closes, slow)   # len = n - slow + 1

    if not ema_fast or not ema_slow:
        return empty

    n_slow           = len(ema_slow)
    ema_fast_aligned = ema_fast[-n_slow:]
    macd_vals        = [ema_fast_aligned[i] - ema_slow[i] for i in range(n_slow)]

    # macd_line começa em closes[slow-1]
    macd_line = [None] * (slow - 1) + [round(v, 4) for v in macd_vals]

    sig_series = _ema_series(macd_vals, signal_period)
    if not sig_series:
        return {"macd_line": macd_line, "signal_line": [None] * n, "histogram": [None] * n}

    # signal_line começa em closes[slow-1 + signal_period-1]
    offset      = slow - 1 + signal_period - 1
    signal_line = [None] * offset + [round(v, 4) for v in sig_series]

    histogram = [None] * n
    for i in range(offset, n):
        m = macd_line[i]
        s = signal_line[i]
        if m is not None and s is not None:
            histogram[i] = round(m - s, 4)

    return {"macd_line": macd_line, "signal_line": signal_line, "histogram": histogram}
```

- [ ] **Step 4: Rodar — devem passar**

```bash
cd /home/fabiano/Documents/Yfinance
python3 -m pytest tests/test_swing_service.py -v
```

Esperado: todos os testes passando (os 13 anteriores + os novos de série).

- [ ] **Step 5: Commit**

```bash
git add tests/test_swing_service.py src/backend/services/swing_service.py
git commit -m "feat: add swing indicator series functions with tests"
```

---

## Task 2: Endpoint GET /api/swing/chart/<ticker>

**Files:**
- Modify: `src/backend/api_server.py`

- [ ] **Step 1: Adicionar o endpoint logo após `GET /api/swing`**

Localizar:
```python
@app.route("/api/swing")
def get_swing():
    data = repo.load_swing_data()
    return jsonify(data)
```

Adicionar logo depois:

```python
@app.route("/api/swing/chart/<ticker>")
def get_swing_chart(ticker):
    t = ticker.upper()
    try:
        yf_obj = yfinance.Ticker(t + ".SA")
        hist   = yf_obj.history(period="6mo")
        if hist.empty:
            return jsonify({"error": "no data"}), 404

        closes = []
        dates  = []
        for idx, row in hist.iterrows():
            try:
                v = float(row["Close"])
                if not math.isnan(v):
                    closes.append(round(v, 2))
                    dates.append(idx.strftime("%Y-%m-%d"))
            except (TypeError, ValueError):
                pass

        if not closes:
            return jsonify({"error": "no valid closes"}), 404

        bb   = swing_service.calc_bb_series(closes)
        ma   = swing_service.calc_ma_series(closes)
        rsi  = swing_service.calc_rsi_series(closes)
        macd = swing_service.calc_macd_series(closes)

        return jsonify({
            "ticker":       t,
            "dates":        dates,
            "closes":       closes,
            "bb_upper":     bb["upper"],
            "bb_middle":    bb["middle"],
            "bb_lower":     bb["lower"],
            "ma20":         ma["ma20"],
            "ma50":         ma["ma50"],
            "rsi":          rsi,
            "macd_line":    macd["macd_line"],
            "macd_signal":  macd["signal_line"],
            "macd_hist":    macd["histogram"],
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

- [ ] **Step 2: Verificar que `math` está importado em `api_server.py`**

```bash
grep "^import math" /home/fabiano/Documents/Yfinance/src/backend/api_server.py
```

Esperado: linha `import math` presente. Se não estiver, adicionar no bloco de imports.

- [ ] **Step 3: Testar o endpoint manualmente**

```bash
cd /home/fabiano/Documents/Yfinance/src/backend
python3 api_server.py &
sleep 3
curl -s "http://localhost:5000/api/swing/chart/BBAS3" | python3 -m json.tool | head -30
kill %1 2>/dev/null; wait %1 2>/dev/null
```

Esperado: JSON com campos `dates`, `closes`, `bb_upper`, `rsi`, `macd_line`, etc. Arrays do mesmo comprimento.

- [ ] **Step 4: Commit**

```bash
git add src/backend/api_server.py
git commit -m "feat: add /api/swing/chart/<ticker> endpoint with full indicator series"
```

---

## Task 3: Frontend — ícone + modal com 3 gráficos

**Files:**
- Modify: `src/frontend/index.html`

Esta task tem 4 sub-partes: (a) CSS, (b) HTML do modal, (c) JS, (d) ícone na tabela.

### 3a — CSS

- [ ] **Step 1: Adicionar CSS do modal de gráfico**

Localizar `.swing-sig-n { ... }` no CSS e adicionar logo depois:

```css
.swing-chart-btn { background: none; border: none; cursor: pointer; color: var(--muted); font-size: 13px; padding: 0 4px; line-height: 1; opacity: .7; vertical-align: middle; }
.swing-chart-btn:hover { color: var(--blue); opacity: 1; }
#swingChartModal { position: fixed; inset: 0; background: rgba(0,0,0,.75); display: flex; align-items: center; justify-content: center; z-index: 900; }
#swingChartModal.hidden { display: none; }
.swing-chart-box { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; width: min(680px, 96vw); padding: 16px; }
.swing-chart-hdr { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.swing-chart-title { font-size: 14px; font-weight: 700; color: var(--blue); }
.swing-chart-close { background: none; border: none; color: var(--muted); font-size: 18px; cursor: pointer; line-height: 1; }
.swing-chart-close:hover { color: var(--text); }
.swing-chart-label { font-size: 9px; font-weight: 600; color: var(--muted); letter-spacing: .5px; text-transform: uppercase; margin: 10px 0 4px; }
.swing-chart-label:first-of-type { margin-top: 0; }
```

### 3b — HTML do modal

- [ ] **Step 2: Adicionar modal antes do fechamento do `</body>`**

Localizar `</body>` no final do arquivo e adicionar antes:

```html
<!-- ─── Swing Chart Modal ─────────────────────────────────────── -->
<div id="swingChartModal" class="hidden" onclick="if(event.target===this)closeSwingChart()">
  <div class="swing-chart-box">
    <div class="swing-chart-hdr">
      <span class="swing-chart-title" id="swingChartTitle">—</span>
      <button class="swing-chart-close" onclick="closeSwingChart()">✕</button>
    </div>
    <div class="swing-chart-label">Preço · Bollinger Bands · MA20 / MA50</div>
    <canvas id="swingPriceCanvas" height="180"></canvas>
    <div class="swing-chart-label">RSI (14) — linha em 30</div>
    <canvas id="swingRsiCanvas" height="100"></canvas>
    <div class="swing-chart-label">MACD (12 / 26 / 9)</div>
    <canvas id="swingMacdCanvas" height="100"></canvas>
  </div>
</div>
```

### 3c — JavaScript

- [ ] **Step 3: Adicionar funções JS**

Localizar `async function loadSwing()` e adicionar logo antes:

```javascript
// ─── Swing Chart Modal ────────────────────────────────────────────
let _swingChartPrice = null;
let _swingChartRsi   = null;
let _swingChartMacd  = null;

function closeSwingChart() {
  document.getElementById('swingChartModal').classList.add('hidden');
  if (_swingChartPrice) { _swingChartPrice.destroy(); _swingChartPrice = null; }
  if (_swingChartRsi)   { _swingChartRsi.destroy();   _swingChartRsi   = null; }
  if (_swingChartMacd)  { _swingChartMacd.destroy();  _swingChartMacd  = null; }
}

async function openSwingChart(ticker) {
  closeSwingChart();
  document.getElementById('swingChartTitle').textContent = ticker + ' · Indicadores 6m';
  document.getElementById('swingChartModal').classList.remove('hidden');

  let data;
  try {
    const res = await fetch('/api/swing/chart/' + ticker);
    if (!res.ok) throw new Error('erro ' + res.status);
    data = await res.json();
  } catch (e) {
    document.getElementById('swingChartTitle').textContent = ticker + ' · erro ao carregar';
    return;
  }

  const labels    = data.dates;
  const gridColor = 'rgba(48,54,61,.6)';
  const tickColor = '#8b949e';
  const baseOpts  = {
    responsive: true,
    animation: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { labels: { color: tickColor, font: { size: 10 }, boxWidth: 14, padding: 8 } },
      tooltip: {
        backgroundColor: '#161b22',
        borderColor: '#30363d',
        borderWidth: 1,
        titleColor: '#e6edf3',
        bodyColor: '#8b949e',
      },
    },
    scales: {
      x: { ticks: { color: tickColor, maxTicksLimit: 6, font: { size: 9 } }, grid: { color: gridColor } },
      y: { ticks: { color: tickColor, font: { size: 9 } }, grid: { color: gridColor } },
    },
  };

  // ── Painel 1: Preço + BB + MAs
  _swingChartPrice = new Chart(document.getElementById('swingPriceCanvas'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Preço',    data: data.closes,    borderColor: '#58a6ff', borderWidth: 1.5, pointRadius: 0, tension: 0.2 },
        { label: 'BB Sup',   data: data.bb_upper,  borderColor: 'rgba(139,148,158,.4)', borderWidth: 1, borderDash: [3,3], pointRadius: 0, fill: false },
        { label: 'BB Mid',   data: data.bb_middle, borderColor: 'rgba(139,148,158,.25)', borderWidth: 1, borderDash: [2,4], pointRadius: 0, fill: false },
        { label: 'BB Inf',   data: data.bb_lower,  borderColor: 'rgba(139,148,158,.4)', borderWidth: 1, borderDash: [3,3], pointRadius: 0, fill: false },
        { label: 'MA20',     data: data.ma20,      borderColor: '#d29922', borderWidth: 1.2, pointRadius: 0 },
        { label: 'MA50',     data: data.ma50,      borderColor: '#a371f7', borderWidth: 1.2, pointRadius: 0 },
      ],
    },
    options: Object.assign({}, baseOpts, {
      scales: Object.assign({}, baseOpts.scales, {
        y: Object.assign({}, baseOpts.scales.y, {
          ticks: Object.assign({}, baseOpts.scales.y.ticks, { callback: function(v) { return 'R$' + v.toFixed(2); } }),
        }),
      }),
    }),
  });

  // ── Painel 2: RSI
  var rsiData = data.rsi;
  _swingChartRsi = new Chart(document.getElementById('swingRsiCanvas'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'RSI(14)',
          data: rsiData,
          borderColor: '#3fb950',
          borderWidth: 1.5,
          pointRadius: 0,
          tension: 0.2,
          fill: false,
        },
        {
          label: 'Nível 30',
          data: labels.map(function() { return 30; }),
          borderColor: 'rgba(248,81,73,.5)',
          borderWidth: 1,
          borderDash: [4, 3],
          pointRadius: 0,
          fill: false,
        },
        {
          label: 'Nível 70',
          data: labels.map(function() { return 70; }),
          borderColor: 'rgba(210,153,34,.4)',
          borderWidth: 1,
          borderDash: [4, 3],
          pointRadius: 0,
          fill: false,
        },
      ],
    },
    options: Object.assign({}, baseOpts, {
      scales: Object.assign({}, baseOpts.scales, {
        y: Object.assign({}, baseOpts.scales.y, { min: 0, max: 100 }),
      }),
    }),
  });

  // ── Painel 3: MACD
  _swingChartMacd = new Chart(document.getElementById('swingMacdCanvas'), {
    data: {
      labels,
      datasets: [
        {
          type: 'bar',
          label: 'Histograma',
          data: data.macd_hist,
          backgroundColor: data.macd_hist.map(function(v) {
            if (v === null) return 'transparent';
            return v >= 0 ? 'rgba(63,185,80,.45)' : 'rgba(248,81,73,.45)';
          }),
          borderWidth: 0,
        },
        {
          type: 'line',
          label: 'MACD',
          data: data.macd_line,
          borderColor: '#58a6ff',
          borderWidth: 1.5,
          pointRadius: 0,
          tension: 0.2,
        },
        {
          type: 'line',
          label: 'Sinal',
          data: data.macd_signal,
          borderColor: '#f85149',
          borderWidth: 1.2,
          pointRadius: 0,
          tension: 0.2,
          borderDash: [3, 2],
        },
      ],
    },
    options: baseOpts,
  });
}
```

### 3d — Ícone na tabela

- [ ] **Step 4: Adicionar ícone 📈 na coluna Status de `renderSwingTable()`**

Localizar dentro de `renderSwingTable()` a variável `badge`:

```javascript
    var badge = d.is_setup
      ? '<span class="swing-badge-setup">SETUP</span>'
      : '<span class="swing-badge-none">–</span>';
```

Substituir por:

```javascript
    var badgeLabel = d.is_setup ? '<span class="swing-badge-setup">SETUP</span>' : '<span class="swing-badge-none">–</span>';
    var badge = badgeLabel + ' <button class="swing-chart-btn" onclick="event.stopPropagation();openSwingChart(\'' + d.ticker + '\')" title="Ver gráfico indicadores">📈</button>';
```

- [ ] **Step 5: Commit**

```bash
git add src/frontend/index.html
git commit -m "feat: add swing chart modal with price/BB/MA/RSI/MACD panels"
```

---

## Task 4: Smoke test

- [ ] **Step 1: Rodar todos os testes**

```bash
cd /home/fabiano/Documents/Yfinance
python3 -m pytest tests/test_swing_service.py -v 2>&1 | tail -8
```

Esperado: todos passando.

- [ ] **Step 2: Subir servidor e testar endpoint**

```bash
cd /home/fabiano/Documents/Yfinance/src/backend
python3 api_server.py &
sleep 3
curl -s "http://localhost:5000/api/swing/chart/BBAS3" | python3 -c "
import json, sys
d = json.load(sys.stdin)
n = len(d['dates'])
print('datas:', n)
print('RSI nulos iniciais:', sum(1 for v in d['rsi'] if v is None))
print('MACD último:', d['macd_line'][-1])
print('BB lower último:', d['bb_lower'][-1])
print('MA20 último:', d['ma20'][-1])
"
kill %1 2>/dev/null; wait %1 2>/dev/null
```

Esperado:
```
datas: ~120
RSI nulos iniciais: 14
MACD último: <float>
BB lower último: <float>
MA20 último: <float>
```

- [ ] **Step 3: Verificar UI manualmente**

Abrir `http://localhost:5000`, ir para aba Swing. Para cada linha da tabela:
- [ ] Coluna Status mostra badge + ícone 📈
- [ ] Clicar no ícone 📈 abre o modal (não abre o modal de detalhe do ativo)
- [ ] Clicar na linha (fora do ícone) abre o modal de detalhe normalmente
- [ ] Modal mostra 3 gráficos: preço+BB+MAs, RSI com linhas em 30/70, MACD com histograma
- [ ] Fechar o modal com ✕ ou clicando fora funciona

- [ ] **Step 4: Commit final**

```bash
git add .
git commit -m "feat: swing chart modal smoke test passed"
```
