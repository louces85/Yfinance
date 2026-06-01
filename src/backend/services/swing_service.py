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
from config import rules


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
        "vol_confirm": ctx["vol_confirm"],
    }


def _target_for(setup_type, ctx, entry):
    """Alvo bruto por tipo de setup (antes do teto de ATR)."""
    if setup_type == "PULLBACK":
        return _recent_high(ctx["highs"], rules.PULLBACK_TARGET_LOOKBACK)
    if setup_type == "REVERSAL":
        bbm = ctx["bb_middle"][-1] if ctx["bb_middle"] else None
        cands = [c for c in (bbm, ctx["ma50"]) if c is not None and c > entry]
        return min(cands) if cands else None
    # BREAKOUT — measured move (resistência exclui o candle de rompimento de hoje,
    # consistente com detect_breakout)
    look = rules.BREAKOUT_LOOKBACK
    prior_window = ctx["highs"][-(look + 1):-1]
    prior_high = max(prior_window) if prior_window else None
    cons_low = _recent_low(ctx["lows"], look)
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
        window   = closes[i - period + 1: i + 1]
        mean     = sum(window) / period
        variance = sum((x - mean) ** 2 for x in window) / period
        std      = math.sqrt(variance)
        upper[i]  = round(mean + num_std * std, 2)
        middle[i] = round(mean, 2)
        lower[i]  = round(mean - num_std * std, 2)

    return {"upper": upper, "middle": middle, "lower": lower}


def calc_ma_series(closes, fast=20, slow=50):
    """SMA rápida e lenta para cada fechamento. None enquanto janela incompleta."""
    n       = len(closes)
    ma_fast = [None] * n
    ma_slow = [None] * n

    for i in range(fast - 1, n):
        ma_fast[i] = round(sum(closes[i - fast + 1: i + 1]) / fast, 2)

    for i in range(slow - 1, n):
        ma_slow[i] = round(sum(closes[i - slow + 1: i + 1]) / slow, 2)

    return {"ma20": ma_fast, "ma50": ma_slow}


def calc_macd_series(closes, fast=12, slow=26, signal_period=9):
    """MACD line, signal line e histograma para cada fechamento. None onde insuficiente."""
    n     = len(closes)
    empty = {"macd_line": [None] * n, "signal_line": [None] * n, "histogram": [None] * n}

    ema_fast = _ema_series(closes, fast)
    ema_slow = _ema_series(closes, slow)

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


# ---------------------------------------------------------------------------
# Execução principal
# ---------------------------------------------------------------------------

def run():
    """Busca OHLCV do yfinance para todos os tickers do monitoring_stocks.json,
    calcula os 4 indicadores e salva em swing_data.json."""
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
                1 if rsi_signal   else 0,
                1 if macd_bullish else 0,
                1 if bb_signal    else 0,
                1 if ma_signal    else 0,
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

            time.sleep(0.3)

        except Exception as e:
            print("[swing_service] ERRO em {}: {}".format(ticker, e))
            continue

    results.sort(key=lambda x: x["signals_count"], reverse=True)
    repo.save_swing_data(results)
    print("[swing_service] {} tickers calculados, {} setups.".format(
        len(results), sum(1 for r in results if r["is_setup"])
    ))
    return results
