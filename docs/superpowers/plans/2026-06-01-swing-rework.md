# Swing Tab Rework — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Substituir o score "soma de 4 indicadores" da aba de swing por 3 setups coerentes (pullback, reversão, rompimento) com gatilho real, filtro de tendência, níveis de risco (entrada/stop/alvo/R:R) e nota A/B/C.

**Architecture:** Backend `swing_service.py` ganha funções puras testáveis (ATR, tendência, detectores, níveis, nota) orquestradas por `analyze_ticker()`/`run()`. Todos os limiares vão para `config/rules.py`. O `swing_data.json` muda de schema; o frontend (`index.html`) passa a mostrar colunas acionáveis. Os `calc_*` antigos permanecem (usados pelo endpoint `/api/swing/chart`).

**Tech Stack:** Python 3.8 (sem f-strings complexas, sem walrus), pytest, JS vanilla, Chart.js.

**Spec:** `docs/superpowers/specs/2026-06-01-swing-rework-design.md`

---

## File Map

- **Modify** `src/backend/config/rules.py` — bloco de constantes de swing
- **Modify** `src/backend/services/swing_service.py` — novas funções puras + `build_context`/`analyze_ticker` + reescrita do `run()`
- **Modify** `tests/test_swing_service.py` — novos testes (TDD)
- **Modify** `src/frontend/index.html` — CSS, header da tabela, `renderSwingTable()`, helpers, modal band
- **Modify** `src/brain/brain_calculations.md` — §7.12 reescrita
- **Modify** `src/brain/brain_frontend.md` — §9.5 atualizada

**Test command (sempre da raiz do repo):**
`python -m pytest tests/test_swing_service.py -v`

---

## Task 1: Thresholds em rules.py

**Files:**
- Modify: `src/backend/config/rules.py` (append ao final)

- [ ] **Step 1: Adicionar o bloco de constantes**

Adicione ao final de `src/backend/config/rules.py`:

```python

# --- Swing Trade: indicadores e setups ---
RSI_OVERSOLD             = 30     # RSI abaixo disso = sobrevenda (reversão)
PULLBACK_RSI_LO          = 35     # faixa de recuo saudável (pullback) — mínimo
PULLBACK_RSI_HI          = 50     # faixa de recuo saudável (pullback) — máximo
PULLBACK_RECENT_LOOKBACK = 5      # janela p/ detectar recuo/gatilho do pullback
REVERSAL_RECENT_LOOKBACK = 3      # janela p/ sobrevenda + reconquista (reversão)
BREAKOUT_LOOKBACK        = 20     # nº de pregões da resistência rompida
SWING_LOW_LOOKBACK       = 10     # fundo recente p/ stop estrutural
PULLBACK_TARGET_LOOKBACK = 30     # máxima anterior usada como alvo do pullback
MA50_SLOPE_LOOKBACK      = 10     # pregões p/ medir inclinação da MA50
VOL_SURGE_MULT           = 1.5    # volume > mult × média(20) = confirmação
RR_MIN                   = 1.5    # R:R mínimo p/ qualificar como setup
RR_STRONG                = 2.0    # R:R a partir do qual a nota ganha bônus cheio
ATR_STOP_MIN             = 1.0    # distância mínima do stop em múltiplos de ATR
ATR_STOP_MAX             = 3.0    # distância máxima do stop em múltiplos de ATR
ATR_TARGET_MAX           = 3.0    # teto do alvo em múltiplos de ATR
# Pesos do score de qualidade (0–100) e cortes de nota
W_TREND_ALTA             = 30
W_TREND_LATERAL          = 12
W_TRIGGER_PER            = 8      # por motivo de gatilho (cap 3)
W_VOLUME                 = 15
W_RR_HIGH                = 20     # R:R >= RR_STRONG
W_RR_OK                  = 10     # RR_MIN <= R:R < RR_STRONG
GRADE_A                  = 70     # score >= 70 → nota A
GRADE_B                  = 50     # score >= 50 → nota B (senão C)
```

- [ ] **Step 2: Verificar import**

Run: `python -c "import sys; sys.path.insert(0,'src/backend'); from config import rules; print(rules.RR_MIN, rules.GRADE_A, rules.W_TREND_ALTA)"`
Expected: `1.5 70 30`

- [ ] **Step 3: Commit**

```bash
git add src/backend/config/rules.py
git commit -m "feat(swing): thresholds de setups, risco e nota em rules.py"
```

---

## Task 2: calc_atr (ATR de Wilder)

**Files:**
- Modify: `src/backend/services/swing_service.py`
- Test: `tests/test_swing_service.py`

- [ ] **Step 1: Escrever o teste que falha**

Adicione no fim de `tests/test_swing_service.py` (e acrescente `calc_atr` à linha de import do `swing_service`):

```python
# ─── ATR ───────────────────────────────────────────────────────────

def test_atr_constant_true_range():
    # high-low = 2 em todo pregão, sem gaps → TR=2 → ATR=2
    closes = [10.0] * 20
    highs  = [11.0] * 20
    lows   = [9.0]  * 20
    assert calc_atr(highs, lows, closes, period=14) == 2.0


def test_atr_none_when_insufficient():
    closes = [10.0] * 5
    highs  = [11.0] * 5
    lows   = [9.0]  * 5
    assert calc_atr(highs, lows, closes, period=14) is None
```

Atualize a linha de import existente para incluir a função (mantenha as demais):

```python
from swing_service import calc_rsi, calc_macd, calc_bb, calc_ma_cross, calc_atr
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_swing_service.py::test_atr_constant_true_range -v`
Expected: FAIL com `ImportError` / `cannot import name 'calc_atr'`

- [ ] **Step 3: Implementar**

Adicione em `src/backend/services/swing_service.py`, logo após `calc_ma_cross` (antes da seção "Funções de série"):

```python
def calc_atr(highs, lows, closes, period=14):
    """ATR (Average True Range) de Wilder. Retorna escalar ou None se insuficiente."""
    n = len(closes)
    if n < period + 1 or len(highs) != n or len(lows) != n:
        return None

    trs = []
    for i in range(1, n):
        tr = max(highs[i] - lows[i],
                 abs(highs[i] - closes[i - 1]),
                 abs(lows[i] - closes[i - 1]))
        trs.append(tr)

    atr = sum(trs[:period]) / period
    for i in range(period, len(trs)):
        atr = (atr * (period - 1) + trs[i]) / period
    return round(atr, 4)
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_swing_service.py -k atr -v`
Expected: PASS (2 testes)

- [ ] **Step 5: Commit**

```bash
git add src/backend/services/swing_service.py tests/test_swing_service.py
git commit -m "feat(swing): calc_atr (ATR de Wilder)"
```

---

## Task 3: calc_sma, _sma_at e classify_trend

**Files:**
- Modify: `src/backend/services/swing_service.py`
- Test: `tests/test_swing_service.py`

- [ ] **Step 1: Escrever os testes que falham**

Adicione em `tests/test_swing_service.py`:

```python
# ─── SMA / tendência ───────────────────────────────────────────────

def test_sma_last_window():
    assert calc_sma([float(i) for i in range(1, 11)], 5) == 8.0  # média de 6..10


def test_sma_none_when_insufficient():
    assert calc_sma([1.0, 2.0], 5) is None


def test_trend_alta_when_rising_above_mas():
    closes = [float(i) for i in range(1, 261)]  # uptrend forte
    assert classify_trend(closes) == "ALTA"


def test_trend_baixa_when_falling_below_mas():
    closes = [float(260 - i) for i in range(260)]  # downtrend forte
    assert classify_trend(closes) == "BAIXA"


def test_trend_lateral_when_flat():
    assert classify_trend([10.0] * 260) == "LATERAL"


def test_trend_lateral_when_no_ma200():
    assert classify_trend([float(i) for i in range(1, 100)]) == "LATERAL"
```

Atualize o import:

```python
from swing_service import calc_atr, calc_sma, classify_trend
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_swing_service.py -k "sma or trend" -v`
Expected: FAIL com `cannot import name 'calc_sma'`

- [ ] **Step 3: Implementar**

Adicione em `src/backend/services/swing_service.py`. Primeiro, no topo do arquivo, acrescente o import de rules logo após `import repositories.stock_repository as repo`:

```python
from config import rules
```

Depois adicione as funções após `calc_atr`:

```python
def calc_sma(values, period):
    """SMA escalar dos últimos 'period' valores. None se insuficiente."""
    if len(values) < period:
        return None
    return round(sum(values[-period:]) / period, 4)


def _sma_at(values, period, offset=0):
    """SMA de 'period' valores terminando 'offset' posições antes do fim."""
    end = len(values) - offset
    start = end - period
    if start < 0:
        return None
    return sum(values[start:end]) / period


def classify_trend(closes):
    """Retorna 'ALTA' | 'BAIXA' | 'LATERAL' com base em MA50, MA200 e inclinação da MA50."""
    ma50 = calc_sma(closes, 50)
    ma200 = calc_sma(closes, 200)
    if ma50 is None or ma200 is None:
        return "LATERAL"

    price = closes[-1]
    ma50_prev = _sma_at(closes, 50, rules.MA50_SLOPE_LOOKBACK)
    ma50_rising = ma50_prev is not None and ma50 > ma50_prev
    ma50_falling = ma50_prev is not None and ma50 < ma50_prev

    if price > ma50 > ma200 and ma50_rising:
        return "ALTA"
    if price < ma200 and ma50_falling:
        return "BAIXA"
    return "LATERAL"
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_swing_service.py -k "sma or trend" -v`
Expected: PASS (6 testes)

- [ ] **Step 5: Commit**

```bash
git add src/backend/services/swing_service.py tests/test_swing_service.py
git commit -m "feat(swing): calc_sma e classify_trend (ALTA/BAIXA/LATERAL)"
```

---

## Task 4: Helpers de volume e estrutura

**Files:**
- Modify: `src/backend/services/swing_service.py`
- Test: `tests/test_swing_service.py`

- [ ] **Step 1: Escrever os testes que falham**

Adicione em `tests/test_swing_service.py`:

```python
# ─── Volume / estrutura ────────────────────────────────────────────

def test_avg_volume_last_20():
    vols = [100.0] * 19 + [200.0]
    assert calc_avg_volume(vols, period=20) == 105.0


def test_avg_volume_none_when_insufficient():
    assert calc_avg_volume([100.0] * 5, period=20) is None


def test_vol_confirm_true_on_surge():
    vols = [100.0] * 19 + [200.0]  # média 105, último 200 > 1.5*105=157.5
    assert vol_confirm(vols, 1.5) is True


def test_vol_confirm_false_when_normal():
    vols = [100.0] * 20
    assert vol_confirm(vols, 1.5) is False


def test_recent_low_and_high():
    assert _recent_low([5.0, 3.0, 4.0, 9.0], 3) == 3.0
    assert _recent_high([5.0, 3.0, 4.0, 9.0], 3) == 9.0
```

Atualize o import:

```python
from swing_service import calc_avg_volume, vol_confirm, _recent_low, _recent_high
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_swing_service.py -k "volume or vol_confirm or recent" -v`
Expected: FAIL com `cannot import name 'calc_avg_volume'`

- [ ] **Step 3: Implementar**

Adicione em `src/backend/services/swing_service.py` após `classify_trend`:

```python
def calc_avg_volume(volumes, period=20):
    """Média de volume dos últimos 'period' pregões. None se insuficiente."""
    if len(volumes) < period:
        return None
    return round(sum(volumes[-period:]) / period, 2)


def vol_confirm(volumes, mult):
    """True quando o volume de hoje supera mult × média(20)."""
    avg = calc_avg_volume(volumes)
    if avg is None or avg == 0:
        return False
    return volumes[-1] > mult * avg


def _recent_low(lows, lookback):
    """Menor mínima dos últimos 'lookback' pregões."""
    window = lows[-lookback:]
    return min(window) if window else None


def _recent_high(highs, lookback):
    """Maior máxima dos últimos 'lookback' pregões."""
    window = highs[-lookback:]
    return max(window) if window else None
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_swing_service.py -k "volume or vol_confirm or recent" -v`
Expected: PASS (5 testes)

- [ ] **Step 5: Commit**

```bash
git add src/backend/services/swing_service.py tests/test_swing_service.py
git commit -m "feat(swing): helpers de volume e fundo/topo recentes"
```

---

## Task 5: build_context

**Files:**
- Modify: `src/backend/services/swing_service.py`
- Test: `tests/test_swing_service.py`

- [ ] **Step 1: Escrever o teste que falha**

Adicione em `tests/test_swing_service.py`:

```python
# ─── Contexto ──────────────────────────────────────────────────────

def test_build_context_keys_and_trend():
    closes = [float(i) for i in range(1, 261)]
    highs  = [c + 0.5 for c in closes]
    lows   = [c - 0.5 for c in closes]
    vols   = [100.0] * 260
    ctx = build_context(closes, highs, lows, vols)
    for key in ("closes", "highs", "lows", "volumes", "rsi", "macd_hist",
                "bb_lower", "bb_middle", "ma20", "ma50", "ma200",
                "trend", "atr", "vol_confirm"):
        assert key in ctx
    assert ctx["trend"] == "ALTA"
    assert ctx["atr"] is not None
    assert len(ctx["rsi"]) == len(closes)
```

Atualize o import:

```python
from swing_service import build_context
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_swing_service.py::test_build_context_keys_and_trend -v`
Expected: FAIL com `cannot import name 'build_context'`

- [ ] **Step 3: Implementar**

Adicione em `src/backend/services/swing_service.py` após os helpers da Task 4:

```python
def build_context(closes, highs, lows, volumes):
    """Pré-calcula todos os indicadores num dict, para os detectores consumirem."""
    bb = calc_bb_series(closes)
    return {
        "closes":      closes,
        "highs":       highs,
        "lows":        lows,
        "volumes":     volumes,
        "rsi":         calc_rsi_series(closes),
        "macd_hist":   calc_macd_series(closes)["histogram"],
        "bb_lower":    bb["lower"],
        "bb_middle":   bb["middle"],
        "ma20":        calc_ma_series(closes)["ma20"],
        "ma50":        calc_sma(closes, 50),
        "ma200":       calc_sma(closes, 200),
        "trend":       classify_trend(closes),
        "atr":         calc_atr(highs, lows, closes),
        "vol_confirm": vol_confirm(volumes, rules.VOL_SURGE_MULT),
    }
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_swing_service.py::test_build_context_keys_and_trend -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/backend/services/swing_service.py tests/test_swing_service.py
git commit -m "feat(swing): build_context pré-calcula indicadores"
```

---

## Task 6: detect_pullback

**Files:**
- Modify: `src/backend/services/swing_service.py`
- Test: `tests/test_swing_service.py`

- [ ] **Step 1: Escrever os testes que falham**

Adicione em `tests/test_swing_service.py` um helper de contexto sintético e os testes:

```python
# ─── Detectores ────────────────────────────────────────────────────

def _ctx(trend="ALTA", rsi=None, macd_hist=None, closes=None, lows=None,
         highs=None, bb_lower=None, bb_middle=None, ma20=None, ma50=100.0,
         vol_confirm=False):
    """Monta um contexto mínimo para testar detectores de forma determinística."""
    closes = closes if closes is not None else [100.0, 101.0]
    return {
        "closes": closes,
        "highs": highs if highs is not None else list(closes),
        "lows": lows if lows is not None else list(closes),
        "volumes": [100.0] * len(closes),
        "rsi": rsi if rsi is not None else [40.0, 42.0],
        "macd_hist": macd_hist if macd_hist is not None else [-1.0, -0.5],
        "bb_lower": bb_lower if bb_lower is not None else [90.0] * len(closes),
        "bb_middle": bb_middle if bb_middle is not None else [100.0] * len(closes),
        "ma20": ma20 if ma20 is not None else [99.0] * len(closes),
        "ma50": ma50,
        "ma200": 80.0,
        "trend": trend,
        "atr": 2.0,
        "vol_confirm": vol_confirm,
    }


def test_pullback_fires_in_uptrend_with_rsi_dip_and_turn():
    ctx = _ctx(trend="ALTA",
               rsi=[60.0, 45.0, 47.0],     # recuo p/ faixa 35-50 + virando pra cima
               closes=[100.0, 98.0, 99.0]) # repique
    out = detect_pullback(ctx)
    assert out is not None
    assert out["setup_type"] == "PULLBACK"
    assert out["trigger"]
    assert out["strength"] >= 1


def test_pullback_none_when_not_uptrend():
    ctx = _ctx(trend="LATERAL", rsi=[60.0, 45.0, 47.0], closes=[100.0, 98.0, 99.0])
    assert detect_pullback(ctx) is None


def test_pullback_none_without_turning_trigger():
    # recuo presente mas tudo caindo: RSI caindo, macd caindo, preço caindo
    ctx = _ctx(trend="ALTA",
               rsi=[60.0, 47.0, 45.0],
               macd_hist=[-0.5, -1.0],
               closes=[100.0, 99.0, 97.0])
    assert detect_pullback(ctx) is None
```

Atualize o import:

```python
from swing_service import detect_pullback
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_swing_service.py -k pullback -v`
Expected: FAIL com `cannot import name 'detect_pullback'`

- [ ] **Step 3: Implementar**

Adicione em `src/backend/services/swing_service.py` após `build_context`:

```python
def _turning_reasons(ctx):
    """Lista de motivos de virada para cima (RSI, MACD, repique de preço)."""
    rsi = ctx["rsi"]
    hist = ctx["macd_hist"]
    closes = ctx["closes"]
    reasons = []
    if len(rsi) >= 2 and rsi[-1] is not None and rsi[-2] is not None and rsi[-1] > rsi[-2]:
        reasons.append("RSI virando")
    if len(hist) >= 2 and hist[-1] is not None and hist[-2] is not None and hist[-1] > hist[-2]:
        reasons.append("MACD subindo")
    if len(closes) >= 2 and closes[-1] > closes[-2]:
        reasons.append("repique")
    return reasons


def _touched_support(ctx, look):
    """True se alguma mínima recente tocou a MA20 ou a banda-média."""
    lows = ctx["lows"]
    n = len(lows)
    ma20 = ctx["ma20"][-1] if ctx["ma20"] else None
    bbm = ctx["bb_middle"][-1] if ctx["bb_middle"] else None
    for i in range(max(0, n - look), n):
        if ma20 is not None and lows[i] <= ma20:
            return True
        if bbm is not None and lows[i] <= bbm:
            return True
    return False


def detect_pullback(ctx):
    """Setup pullback: recuo numa tendência de alta + gatilho de virada."""
    if ctx["trend"] != "ALTA":
        return None

    look = rules.PULLBACK_RECENT_LOOKBACK
    recent = [r for r in ctx["rsi"][-look:] if r is not None]
    rsi_pull = any(rules.PULLBACK_RSI_LO <= r <= rules.PULLBACK_RSI_HI for r in recent)
    if not (rsi_pull or _touched_support(ctx, look)):
        return None

    reasons = _turning_reasons(ctx)
    if not reasons:
        return None

    return {
        "setup_type": "PULLBACK",
        "trigger": " + ".join(reasons),
        "strength": len(reasons),
        "vol_confirm": ctx["vol_confirm"],
    }
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_swing_service.py -k pullback -v`
Expected: PASS (3 testes)

- [ ] **Step 5: Commit**

```bash
git add src/backend/services/swing_service.py tests/test_swing_service.py
git commit -m "feat(swing): detect_pullback (recuo em tendência de alta)"
```

---

## Task 7: detect_reversal

**Files:**
- Modify: `src/backend/services/swing_service.py`
- Test: `tests/test_swing_service.py`

- [ ] **Step 1: Escrever os testes que falham**

Adicione em `tests/test_swing_service.py` (reusa o helper `_ctx`):

```python
def test_reversal_fires_on_oversold_turn_and_reclaim():
    ctx = _ctx(trend="LATERAL",
               rsi=[25.0, 28.0],                    # sobrevenda + virando pra cima
               closes=[88.0, 95.0],                 # reconquistou a banda inferior
               bb_lower=[90.0, 90.0])               # tocou(<=90) ontem, hoje 95>90
    out = detect_reversal(ctx)
    assert out is not None
    assert out["setup_type"] == "REVERSAL"


def test_reversal_none_in_downtrend():
    ctx = _ctx(trend="BAIXA", rsi=[25.0, 28.0], closes=[88.0, 95.0],
               bb_lower=[90.0, 90.0])
    assert detect_reversal(ctx) is None


def test_reversal_none_when_not_reclaimed():
    # ainda abaixo da banda inferior hoje
    ctx = _ctx(trend="LATERAL", rsi=[25.0, 28.0], closes=[88.0, 89.0],
               bb_lower=[90.0, 90.0])
    assert detect_reversal(ctx) is None
```

Atualize o import:

```python
from swing_service import detect_reversal
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_swing_service.py -k reversal -v`
Expected: FAIL com `cannot import name 'detect_reversal'`

- [ ] **Step 3: Implementar**

Adicione em `src/backend/services/swing_service.py` após `detect_pullback`:

```python
def detect_reversal(ctx):
    """Setup reversão: sobrevenda virando + reconquista da banda inferior. Fora de downtrend."""
    if ctx["trend"] == "BAIXA":
        return None

    rsi = ctx["rsi"]
    look = rules.REVERSAL_RECENT_LOOKBACK
    recent = [r for r in rsi[-look:] if r is not None]
    was_oversold = any(r < rules.RSI_OVERSOLD for r in recent)
    turning = (len(rsi) >= 2 and rsi[-1] is not None
               and rsi[-2] is not None and rsi[-1] > rsi[-2])
    if not (was_oversold and turning):
        return None

    lower = ctx["bb_lower"]
    closes = ctx["closes"]
    n = len(closes)
    reclaimed = lower[-1] is not None and closes[-1] > lower[-1]
    touched = any(lower[i] is not None and closes[i] <= lower[i]
                  for i in range(max(0, n - look - 1), n - 1))
    if not (reclaimed and touched):
        return None

    return {
        "setup_type": "REVERSAL",
        "trigger": "RSI saindo de sobrevenda + reconquista banda inf",
        "strength": 2,
        "vol_confirm": ctx["vol_confirm"],
    }
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_swing_service.py -k reversal -v`
Expected: PASS (3 testes)

- [ ] **Step 5: Commit**

```bash
git add src/backend/services/swing_service.py tests/test_swing_service.py
git commit -m "feat(swing): detect_reversal (sobrevenda + reconquista)"
```

---

## Task 8: detect_breakout

**Files:**
- Modify: `src/backend/services/swing_service.py`
- Test: `tests/test_swing_service.py`

- [ ] **Step 1: Escrever os testes que falham**

Adicione em `tests/test_swing_service.py`:

```python
def test_breakout_fires_on_new_high_with_volume():
    closes = [100.0] * 21 + [112.0]          # rompe a máxima dos 20 anteriores
    highs  = [110.0] * 21 + [112.0]          # resistência ~110
    ctx = _ctx(trend="LATERAL", closes=closes, highs=highs, ma50=100.0,
               vol_confirm=True)
    out = detect_breakout(ctx)
    assert out is not None
    assert out["setup_type"] == "BREAKOUT"


def test_breakout_none_without_volume():
    closes = [100.0] * 21 + [112.0]
    highs  = [110.0] * 21 + [112.0]
    ctx = _ctx(trend="LATERAL", closes=closes, highs=highs, ma50=100.0,
               vol_confirm=False)
    assert detect_breakout(ctx) is None


def test_breakout_none_below_ma50():
    closes = [100.0] * 21 + [112.0]
    highs  = [110.0] * 21 + [112.0]
    ctx = _ctx(trend="LATERAL", closes=closes, highs=highs, ma50=120.0,
               vol_confirm=True)
    assert detect_breakout(ctx) is None
```

Atualize o import:

```python
from swing_service import detect_breakout
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_swing_service.py -k breakout -v`
Expected: FAIL com `cannot import name 'detect_breakout'`

- [ ] **Step 3: Implementar**

Adicione em `src/backend/services/swing_service.py` após `detect_reversal`:

```python
def detect_breakout(ctx):
    """Setup rompimento: fecha acima da máxima de N pregões, acima da MA50, com volume."""
    closes = ctx["closes"]
    highs = ctx["highs"]
    ma50 = ctx["ma50"]
    if ma50 is None or closes[-1] <= ma50:
        return None

    look = rules.BREAKOUT_LOOKBACK
    if len(highs) < look + 1:
        return None

    prior_high = max(highs[-(look + 1):-1])  # resistência, excluindo o pregão atual
    if closes[-1] <= prior_high:
        return None
    if not ctx["vol_confirm"]:
        return None

    return {
        "setup_type": "BREAKOUT",
        "trigger": "Rompeu máxima " + str(look) + "p + volume",
        "strength": 2,
        "vol_confirm": True,
    }
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_swing_service.py -k breakout -v`
Expected: PASS (3 testes)

- [ ] **Step 5: Commit**

```bash
git add src/backend/services/swing_service.py tests/test_swing_service.py
git commit -m "feat(swing): detect_breakout (rompimento com volume)"
```

---

## Task 9: calc_levels (entrada/stop/alvo/R:R)

**Files:**
- Modify: `src/backend/services/swing_service.py`
- Test: `tests/test_swing_service.py`

- [ ] **Step 1: Escrever os testes que falham**

Adicione em `tests/test_swing_service.py`:

```python
# ─── Níveis de risco ───────────────────────────────────────────────

def test_levels_stop_clamped_by_atr_floor():
    # fundo recente muito perto (99.5) → stop deve respeitar piso 1×ATR (=2) → 98.0
    ctx = _ctx(closes=[100.0], highs=[100.0], lows=[99.5])
    ctx["lows"] = [99.5] * 10
    ctx["atr"] = 2.0
    lv = calc_levels("REVERSAL", ctx)
    assert lv["entry"] == 100.0
    assert lv["stop"] == 98.0           # 100 - max(0.5, 1*2)


def test_levels_rr_computed():
    ctx = _ctx(closes=[100.0], highs=[100.0], lows=[100.0])
    ctx["lows"] = [95.0] * 10           # stop estrutural 95 (dentro do clamp 2..6)
    ctx["atr"] = 2.0
    ctx["bb_middle"] = [110.0]
    ctx["ma50"] = 110.0
    lv = calc_levels("REVERSAL", ctx)   # alvo = min(110,110)=110, capado por 100+3*2=106
    assert lv["stop"] == 95.0
    assert lv["target"] == 106.0
    assert lv["rr"] == round((106.0 - 100.0) / (100.0 - 95.0), 2)  # 1.2


def test_levels_none_without_atr():
    ctx = _ctx(closes=[100.0])
    ctx["atr"] = None
    assert calc_levels("PULLBACK", ctx) is None
```

Atualize o import:

```python
from swing_service import calc_levels
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_swing_service.py -k levels -v`
Expected: FAIL com `cannot import name 'calc_levels'`

- [ ] **Step 3: Implementar**

Adicione em `src/backend/services/swing_service.py` após `detect_breakout`:

```python
def _target_for(setup_type, ctx, entry):
    """Alvo bruto por tipo de setup (antes do teto de ATR)."""
    if setup_type == "PULLBACK":
        return _recent_high(ctx["highs"], rules.PULLBACK_TARGET_LOOKBACK)
    if setup_type == "REVERSAL":
        bbm = ctx["bb_middle"][-1] if ctx["bb_middle"] else None
        cands = [c for c in (bbm, ctx["ma50"]) if c is not None and c > entry]
        return min(cands) if cands else None
    # BREAKOUT — measured move
    prior_high = _recent_high(ctx["highs"], rules.BREAKOUT_LOOKBACK + 1)
    cons_low = _recent_low(ctx["lows"], rules.BREAKOUT_LOOKBACK)
    if prior_high is not None and cons_low is not None:
        return entry + (prior_high - cons_low)
    return None


def calc_levels(setup_type, ctx):
    """Entrada/stop/alvo/R:R. Stop estrutural com clamp de ATR; alvo capado por ATR."""
    closes = ctx["closes"]
    atr = ctx["atr"]
    entry = closes[-1]
    if atr is None or atr <= 0:
        return None

    swing_low = _recent_low(ctx["lows"], rules.SWING_LOW_LOOKBACK)
    raw_stop = swing_low if swing_low is not None else entry - rules.ATR_STOP_MIN * atr
    dist = entry - raw_stop
    min_d = rules.ATR_STOP_MIN * atr
    max_d = rules.ATR_STOP_MAX * atr
    if dist < min_d:
        dist = min_d
    elif dist > max_d:
        dist = max_d
    stop = round(entry - dist, 2)

    target = _target_for(setup_type, ctx, entry)
    max_target = entry + rules.ATR_TARGET_MAX * atr
    if target is None or target <= entry:
        target = max_target
    if target > max_target:
        target = max_target
    target = round(target, 2)

    risk = entry - stop
    rr = round((target - entry) / risk, 2) if risk > 0 else None
    return {"entry": round(entry, 2), "stop": stop, "target": target, "rr": rr}
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_swing_service.py -k levels -v`
Expected: PASS (3 testes)

- [ ] **Step 5: Commit**

```bash
git add src/backend/services/swing_service.py tests/test_swing_service.py
git commit -m "feat(swing): calc_levels (stop estrutural + ATR, alvo por setup, R:R)"
```

---

## Task 10: grade_setup, _pick_best_setup e analyze_ticker

**Files:**
- Modify: `src/backend/services/swing_service.py`
- Test: `tests/test_swing_service.py`

- [ ] **Step 1: Escrever os testes que falham**

Adicione em `tests/test_swing_service.py`:

```python
# ─── Nota e orquestração ───────────────────────────────────────────

def test_grade_a_for_strong_pullback():
    setup = {"strength": 3, "vol_confirm": True}
    levels = {"rr": 2.5}
    score, grade = grade_setup(setup, levels, "ALTA")
    # 30 (ALTA) + 24 (3 gatilhos) + 15 (vol) + 20 (rr forte) = 89
    assert score == 89
    assert grade == "A"


def test_grade_c_for_weak_setup():
    setup = {"strength": 1, "vol_confirm": False}
    levels = {"rr": 1.5}
    score, grade = grade_setup(setup, levels, "LATERAL")
    # 12 + 8 + 0 + 10 = 30
    assert score == 30
    assert grade == "C"


def test_analyze_ticker_no_setup_returns_base():
    closes = [10.0] * 260            # flat → nenhum setup
    highs  = [10.5] * 260
    lows   = [9.5] * 260
    vols   = [100.0] * 260
    out = analyze_ticker("FLAT3", closes, highs, lows, vols)
    assert out["ticker"] == "FLAT3"
    assert out["setup_type"] is None
    assert out["is_setup"] is False
    assert out["trend"] == "LATERAL"
    assert "updated_at" in out


def test_analyze_ticker_detects_setup_with_levels():
    # uptrend longo + rompimento com volume → algum setup qualifica
    base   = [100.0] * 220
    closes = base + [112.0]
    highs  = [110.0] * 220 + [112.0]
    lows   = [98.0] * 221
    vols   = [100.0] * 220 + [400.0]   # surto de volume
    out = analyze_ticker("BRK3", closes, highs, lows, vols)
    assert out["setup_type"] in ("PULLBACK", "BREAKOUT", "REVERSAL")
    assert out["is_setup"] is True
    assert out["entry"] == 112.0
    assert out["rr"] is not None and out["rr"] >= 1.5
    assert out["grade"] in ("A", "B", "C")
```

Atualize o import:

```python
from swing_service import grade_setup, analyze_ticker
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_swing_service.py -k "grade or analyze" -v`
Expected: FAIL com `cannot import name 'grade_setup'`

- [ ] **Step 3: Implementar**

Adicione em `src/backend/services/swing_service.py` após `calc_levels`:

```python
def grade_setup(setup, levels, trend):
    """Score composto 0–100 e nota A/B/C."""
    score = 0
    if trend == "ALTA":
        score += rules.W_TREND_ALTA
    elif trend == "LATERAL":
        score += rules.W_TREND_LATERAL

    score += min(setup["strength"], 3) * rules.W_TRIGGER_PER

    if setup["vol_confirm"]:
        score += rules.W_VOLUME

    rr = levels["rr"] or 0
    if rr >= rules.RR_STRONG:
        score += rules.W_RR_HIGH
    elif rr >= rules.RR_MIN:
        score += rules.W_RR_OK

    score = min(int(round(score)), 100)
    if score >= rules.GRADE_A:
        grade = "A"
    elif score >= rules.GRADE_B:
        grade = "B"
    else:
        grade = "C"
    return score, grade


def _pick_best_setup(ctx):
    """Roda os 3 detectores, calcula níveis/nota e escolhe o melhor (1 por ticker)."""
    precedence = {"PULLBACK": 3, "BREAKOUT": 2, "REVERSAL": 1}
    candidates = []
    for det in (detect_pullback, detect_reversal, detect_breakout):
        m = det(ctx)
        if not m:
            continue
        levels = calc_levels(m["setup_type"], ctx)
        if levels is None or levels["rr"] is None:
            continue
        is_setup = levels["rr"] >= rules.RR_MIN
        if is_setup:
            score, grade = grade_setup(m, levels, ctx["trend"])
        else:
            score, grade = None, None
        cand = {
            "setup_type": m["setup_type"],
            "trigger": m["trigger"],
            "vol_confirm": m["vol_confirm"],
            "is_setup": is_setup,
            "score": score,
            "grade": grade,
        }
        cand.update(levels)
        candidates.append(cand)

    if not candidates:
        return None

    candidates.sort(key=lambda c: (
        1 if c["is_setup"] else 0,
        c["score"] if c["score"] is not None else -1,
        precedence[c["setup_type"]],
    ), reverse=True)
    return candidates[0]


def analyze_ticker(ticker, closes, highs, lows, volumes):
    """Entrada completa do swing_data.json para um ticker (com ou sem setup)."""
    ctx = build_context(closes, highs, lows, volumes)
    entry = {
        "ticker":      ticker,
        "price":       round(closes[-1], 2),
        "trend":       ctx["trend"],
        "rsi":         calc_rsi(closes),
        "setup_type":  None,
        "grade":       None,
        "score":       None,
        "trigger":     None,
        "entry":       None,
        "stop":        None,
        "target":      None,
        "rr":          None,
        "vol_confirm": False,
        "is_setup":    False,
        "updated_at":  datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }
    best = _pick_best_setup(ctx)
    if best is not None:
        entry.update(best)
    return entry
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_swing_service.py -k "grade or analyze" -v`
Expected: PASS (4 testes)

- [ ] **Step 5: Rodar a suíte inteira**

Run: `python -m pytest tests/test_swing_service.py -v`
Expected: PASS (todos — os testes antigos dos `calc_*` continuam verdes)

- [ ] **Step 6: Commit**

```bash
git add src/backend/services/swing_service.py tests/test_swing_service.py
git commit -m "feat(swing): grade_setup, _pick_best_setup e analyze_ticker"
```

---

## Task 11: Reescrever run()

**Files:**
- Modify: `src/backend/services/swing_service.py` (função `run()` e helper de extração)

- [ ] **Step 1: Substituir run()**

Em `src/backend/services/swing_service.py`, substitua TODA a função `run()` atual (da assinatura `def run():` até o `return results` final) por:

```python
def _extract_ohlcv(hist):
    """Extrai listas alinhadas de close/high/low/volume, descartando linhas inválidas."""
    closes, highs, lows, volumes = [], [], [], []
    for c, h, l, v in zip(hist["Close"], hist["High"], hist["Low"], hist["Volume"]):
        try:
            cf = float(c); hf = float(h); lf = float(l); vf = float(v)
        except (TypeError, ValueError):
            continue
        if math.isnan(cf) or math.isnan(hf) or math.isnan(lf):
            continue
        closes.append(cf)
        highs.append(hf)
        lows.append(lf)
        volumes.append(0.0 if math.isnan(vf) else vf)
    return closes, highs, lows, volumes


def run():
    """Busca OHLCV (1 ano) de cada ticker monitorado, detecta o melhor setup e salva."""
    monitoring = repo.get_monitoring_stocks()
    tickers = [s["ticker"] for s in monitoring]

    results = []
    for ticker in tickers:
        try:
            yf_obj = yfinance.Ticker(ticker + ".SA")
            hist = yf_obj.history(period="1y")

            if hist.empty or len(hist) < 60:
                continue

            closes, highs, lows, volumes = _extract_ohlcv(hist)
            if len(closes) < 60:
                continue

            results.append(analyze_ticker(ticker, closes, highs, lows, volumes))
            time.sleep(0.3)

        except Exception as e:
            print("[swing_service] ERRO em {}: {}".format(ticker, e))
            continue

    results.sort(key=lambda x: (
        1 if x["is_setup"] else 0,
        x["score"] if x["score"] is not None else -1,
        x["rr"] or 0,
    ), reverse=True)

    repo.save_swing_data(results)
    n_setups = sum(1 for r in results if r["is_setup"])
    print("[swing_service] {} analisados, {} setups.".format(len(results), n_setups))
    return results
```

- [ ] **Step 2: Verificar que a suíte continua verde**

Run: `python -m pytest tests/test_swing_service.py -v`
Expected: PASS (run() não é testado por unidade; garante que nada quebrou na importação do módulo)

- [ ] **Step 3: Smoke test manual (1 ticker)**

Run:
```bash
python -c "import sys; sys.path.insert(0,'src/backend'); sys.path.insert(0,'src/backend/services'); \
import swing_service as s; \
import yfinance as yf; \
h = yf.Ticker('PETR4.SA').history(period='1y'); \
c,hi,lo,v = s._extract_ohlcv(h); \
print(s.analyze_ticker('PETR4', c, hi, lo, v))"
```
Expected: imprime um dict com `setup_type`, `trend`, `entry/stop/target/rr` (ou nulls se sem setup) — sem exceção.

- [ ] **Step 4: Commit**

```bash
git add src/backend/services/swing_service.py
git commit -m "feat(swing): run() usa 1y OHLCV + analyze_ticker (novo schema)"
```

---

## Task 12: Frontend — CSS, header e renderSwingTable

**Files:**
- Modify: `src/frontend/index.html`

- [ ] **Step 1: Adicionar CSS dos badges de setup e nota**

Em `src/frontend/index.html`, logo após a regra `.swing-badge-none { ... }` (perto da linha 773), adicione:

```css
.swing-setup-badge { display:inline-block; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:600; border:1px solid; }
.swing-setup-pullback { background:rgba(63,185,80,.15);  color:var(--green);  border-color:rgba(63,185,80,.4); }
.swing-setup-reversal { background:rgba(88,166,255,.15); color:var(--blue);   border-color:rgba(88,166,255,.4); }
.swing-setup-breakout { background:rgba(210,153,34,.15); color:var(--yellow); border-color:rgba(210,153,34,.4); }
.swing-grade { display:inline-block; min-width:18px; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:700; text-align:center; }
.swing-grade-A { background:rgba(63,185,80,.2);  color:var(--green); }
.swing-grade-B { background:rgba(210,153,34,.2); color:var(--yellow); }
.swing-grade-C { background:rgba(139,148,158,.15); color:var(--muted); }
```

- [ ] **Step 2: Substituir o header da tabela**

Substitua o bloco `<thead>...</thead>` da `swing-table` (linhas ~1204-1214) por:

```html
        <tr>
          <th style="text-align:left" onclick="_swingSort('ticker')">Ativo <span id="swingArrow_ticker" class="sort-arrow">↕</span></th>
          <th onclick="_swingSort('price')">Preço (R$) <span id="swingArrow_price" class="sort-arrow">↕</span></th>
          <th>Setup</th>
          <th onclick="_swingSort('score')">Nota <span id="swingArrow_score" class="sort-arrow">↓</span></th>
          <th style="text-align:left">Gatilho</th>
          <th>Entrada</th>
          <th>Stop</th>
          <th>Alvo</th>
          <th onclick="_swingSort('rr')">R:R <span id="swingArrow_rr" class="sort-arrow">↕</span></th>
        </tr>
```

- [ ] **Step 3: Trocar a coluna de ordenação default**

Em `src/frontend/index.html`, na declaração de estado do swing (perto da linha 3651), altere:

```javascript
let _swingSortCol   = 'signals_count';
```
para:
```javascript
let _swingSortCol   = 'score';
```

- [ ] **Step 4: Substituir renderSwingTable() e adicionar helper de badge**

Substitua TODA a função `renderSwingTable()` (linhas ~3844-3925) por:

```javascript
function _swingSetupBadge(d) {
  if (!d.setup_type) return '<span class="swing-badge-none">–</span>';
  var label = { PULLBACK: 'Pullback ↑', REVERSAL: 'Reversão', BREAKOUT: 'Rompimento' }[d.setup_type] || d.setup_type;
  var cls = 'swing-setup-' + d.setup_type.toLowerCase();
  return '<span class="swing-setup-badge ' + cls + '" style="cursor:pointer" ' +
         'onclick="event.stopPropagation();openSwingChart(\'' + d.ticker + '\')" ' +
         'title="Ver gráfico técnico">' + label + '</span>';
}

function renderSwingTable() {
  const data = _swingOnlySetup
    ? _swingData.filter(function(d) { return d.is_setup; })
    : _swingData.slice();

  const col = _swingSortCol;
  const asc = _swingSortAsc;
  data.sort(function(a, b) {
    const va = a[col] != null ? a[col] : (asc ? Infinity : -Infinity);
    const vb = b[col] != null ? b[col] : (asc ? Infinity : -Infinity);
    if (va < vb) return asc ? -1 : 1;
    if (va > vb) return asc ? 1 : -1;
    return 0;
  });

  ['ticker', 'price', 'score', 'rr'].forEach(function(c) {
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

  const total  = _swingData.length;
  const setups = _swingData.filter(function(d) { return d.is_setup; }).length;
  const watch  = _swingData.filter(function(d) { return d.setup_type && !d.is_setup; }).length;
  document.getElementById('swingCountSetup').textContent = setups;
  document.getElementById('swingCountWatch').textContent = watch;
  document.getElementById('swingCountTotal').textContent = total;

  const updEl = document.getElementById('swingUpdated');
  if (_swingData.length && _swingData[0].updated_at) {
    const d = new Date(_swingData[0].updated_at.replace('T', ' '));
    const hh = String(d.getHours()).padStart(2, '0');
    const mm = String(d.getMinutes()).padStart(2, '0');
    updEl.textContent = 'Atualizado: ' + hh + ':' + mm;
  }

  const tbody = document.getElementById('swingTbody');
  if (!data.length) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:var(--muted);padding:32px">Nenhum setup encontrado</td></tr>';
    return;
  }

  const fmt = function(v) { return v != null ? v.toFixed(2) : '—'; };

  tbody.innerHTML = data.map(function(d) {
    var gradeHtml = d.grade
      ? '<span class="swing-grade swing-grade-' + d.grade + '">' + d.grade + '</span>'
      : '<span class="swing-badge-none">–</span>';
    var rrColor = d.rr == null ? 'var(--muted)'
      : (d.rr >= 2 ? 'var(--green)' : (d.rr >= 1.5 ? 'var(--yellow)' : 'var(--muted)'));
    var rrHtml = d.rr != null
      ? '<span style="font-weight:700;color:' + rrColor + '">' + d.rr.toFixed(1) + '</span>'
      : '—';
    var rowClass = d.is_setup ? 'swing-row-setup' : '';
    return '<tr class="' + rowClass + '" onclick="openDetail(\'' + d.ticker + '\')">' +
      '<td><span style="font-weight:600;color:var(--blue)">' + d.ticker + '</span></td>' +
      '<td>' + fmt(d.price) + '</td>' +
      '<td>' + _swingSetupBadge(d) + '</td>' +
      '<td>' + gradeHtml + '</td>' +
      '<td style="text-align:left;color:var(--muted);font-size:11px">' + (d.trigger || '—') + '</td>' +
      '<td>' + fmt(d.entry) + '</td>' +
      '<td style="color:var(--red)">' + fmt(d.stop) + '</td>' +
      '<td style="color:var(--green)">' + fmt(d.target) + '</td>' +
      '<td>' + rrHtml + '</td>' +
    '</tr>';
  }).join('');
}
```

- [ ] **Step 5: Verificação manual**

Inicie o backend e abra a aba Swing no navegador. Confirme: a tabela mostra colunas `Ativo | Preço | Setup | Nota | Gatilho | Entrada | Stop | Alvo | R:R`; badges de setup coloridos por tipo; ordenação por Nota (default) e por R:R/Preço funcionando; clicar no badge abre o modal do gráfico; clicar na linha abre o detalhe; cards do toolbar mostram SETUPs / Monitorar / Analisados coerentes.

- [ ] **Step 6: Commit**

```bash
git add src/frontend/index.html
git commit -m "feat(swing): tabela acionável (setup, nota, entrada/stop/alvo/R:R)"
```

---

## Task 13: Frontend — faixa de info no modal do gráfico

**Files:**
- Modify: `src/frontend/index.html`

- [ ] **Step 1: Adicionar o elemento da faixa no HTML do modal**

Em `src/frontend/index.html`, no `#swingChartModal` (linha ~4587), insira uma faixa logo após o `</div>` que fecha o `.swing-chart-hdr`:

```html
    <div id="swingChartBand" style="display:none;font-size:11px;color:var(--muted);margin-bottom:8px;padding:6px 8px;background:var(--bg);border:1px solid var(--border);border-radius:6px"></div>
```

(Fica entre `</div>` do header e a primeira `<div class="swing-chart-label">`.)

- [ ] **Step 2: Popular a faixa no openSwingChart()**

Em `openSwingChart()`, logo após a linha `document.getElementById('swingChartModal').classList.remove('hidden');` (linha ~3671), adicione:

```javascript
  var _info = (_swingData || []).filter(function(s) { return s.ticker === ticker; })[0];
  var _band = document.getElementById('swingChartBand');
  if (_info && _info.setup_type) {
    var _lbl = { PULLBACK: 'Pullback ↑', REVERSAL: 'Reversão', BREAKOUT: 'Rompimento' }[_info.setup_type] || _info.setup_type;
    var _f = function(v) { return v != null ? v.toFixed(2) : '—'; };
    _band.innerHTML = '<b style="color:var(--text)">' + _lbl + '</b>' +
      (_info.grade ? ' · Nota ' + _info.grade : '') +
      ' · Entrada ' + _f(_info.entry) +
      ' · Stop ' + _f(_info.stop) +
      ' · Alvo ' + _f(_info.target) +
      (_info.rr != null ? ' · R:R ' + _info.rr.toFixed(1) : '') +
      (_info.trigger ? '<br>' + _info.trigger : '');
    _band.style.display = 'block';
  } else {
    _band.style.display = 'none';
  }
```

- [ ] **Step 3: Verificação manual**

Na aba Swing, clique num badge de setup: o modal abre com a faixa mostrando tipo/nota/entrada/stop/alvo/R:R/gatilho acima dos 3 gráficos. Clique num badge de setup pela aba Screening/Carteira (onde `_swingData` pode estar vazio): a faixa fica oculta e o gráfico abre normalmente.

- [ ] **Step 4: Commit**

```bash
git add src/frontend/index.html
git commit -m "feat(swing): faixa de setup/risco no topo do modal de gráfico"
```

---

## Task 14: Atualizar documentação (brain files)

**Files:**
- Modify: `src/brain/brain_calculations.md` (§7.12)
- Modify: `src/brain/brain_frontend.md` (§9.5)

- [ ] **Step 1: Reescrever brain_calculations.md §7.12**

Substitua o conteúdo da seção §7.12 (de `### 7.12 Indicadores Técnicos de Swing Trade` até o fim de `#### 7.12.5`, antes de `### 7.10 DCF`) por uma descrição da nova lógica, cobrindo:
- Dados: `history(period="1y")`, uso de High/Low/Close/Volume.
- Tendência (`classify_trend`): regras ALTA/BAIXA/LATERAL.
- Os 3 setups (pullback, reversão, rompimento) com condições e gatilhos.
- Modelo de risco: stop estrutural com clamp de ATR (`ATR_STOP_MIN`/`MAX`), alvo por tipo de setup com teto `ATR_TARGET_MAX`, R:R, gate `RR_MIN`.
- Nota A/B/C: pesos (`W_TREND_ALTA`, `W_TRIGGER_PER`, `W_VOLUME`, `W_RR_HIGH`/`OK`) e cortes (`GRADE_A`/`GRADE_B`). Observe que a "profundidade/qualidade" do sinal entra como desempate via R:R na ordenação.
- Precedência Pullback → Rompimento → Reversão; um setup por ticker.
- Novo schema do `swing_data.json` (campos: `setup_type, grade, score, trend, trigger, entry, stop, target, rr, vol_confirm, is_setup, rsi`).
- Que todos os limiares estão em `config/rules.py`.

- [ ] **Step 2: Atualizar brain_frontend.md §9.5**

Atualize a §9.5 para refletir: novas colunas (`Ativo | Preço | Setup | Nota | Gatilho | Entrada | Stop | Alvo | R:R`), badges de setup clicáveis por tipo, cards `SETUPs / Monitorar / Analisados` (Monitorar = casou setup mas R:R < mínimo), ordenação por `score`/`rr`/`price`, e a faixa de info no topo do modal de gráfico.

- [ ] **Step 3: Commit**

```bash
git add src/brain/brain_calculations.md src/brain/brain_frontend.md
git commit -m "docs(swing): atualiza brain com setups, risco, nota e novo schema"
```

---

## Verificação final

- [ ] `python -m pytest tests/test_swing_service.py -v` → todos verdes (antigos + novos)
- [ ] Smoke do `run()` num subconjunto pequeno (ou 1 ticker via Task 11 Step 3) sem exceção
- [ ] Aba Swing renderiza colunas novas, ordenação, badges clicáveis e modal com faixa
- [ ] Nenhum valor de swing hardcoded fora de `config/rules.py`
