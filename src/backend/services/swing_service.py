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
