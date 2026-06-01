import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend', 'services'))

from swing_service import calc_rsi, calc_macd, calc_bb, calc_ma_cross, calc_atr
from swing_service import calc_rsi_series, calc_bb_series, calc_ma_series, calc_macd_series
from swing_service import calc_sma, classify_trend
from swing_service import calc_avg_volume, vol_confirm, _recent_low, _recent_high
from swing_service import build_context


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
    # Primeiros 30 valores baixos, últimos 20 altos → MA20 > MA50
    closes = [10.0] * 30 + [20.0] * 20
    ma20, ma50, signal = calc_ma_cross(closes)
    assert signal is True


def test_ma_cross_death_cross():
    # Primeiros 30 altos, últimos 20 baixos → MA20 < MA50
    closes = [20.0] * 30 + [5.0] * 20
    ma20, ma50, signal = calc_ma_cross(closes)
    assert signal is False


def test_ma_cross_returns_none_when_insufficient():
    closes = [10.0] * 30  # menos de 50 pontos
    ma20, ma50, signal = calc_ma_cross(closes)
    assert ma20 is None and ma50 is None and signal is False


def test_macd_returns_none_when_insufficient():
    closes = [10.0] * 20  # menos de 26+9=35 pontos
    macd_val, sig_val, bullish = calc_macd(closes)
    assert macd_val is None and sig_val is None and bullish is False


def test_macd_bullish_after_recovery():
    # 40 preços estáveis, depois alta forte → EMA12 sobe antes de EMA26 → MACD > signal
    closes = [10.0] * 40 + [10.0 + float(i) * 2 for i in range(1, 21)]
    _, _, bullish = calc_macd(closes)
    assert bullish is True


def test_macd_bearish_after_drop():
    # 40 preços estáveis, depois queda forte → EMA12 cai antes de EMA26 → MACD < signal
    closes = [50.0] * 40 + [50.0 - float(i) * 2 for i in range(1, 21)]
    _, _, bullish = calc_macd(closes)
    assert bullish is False


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
