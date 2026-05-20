import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))
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
