"""
Testes do recálculo dos campos derivados de preço na carteira.

Contexto do bug:
  valuations.json guarda um retrato do dia da apuração (roda esporadicamente).
  decision_stocks.json é regerado a cada ciclo de 30 min e recalcula a zona com
  o preço corrente. A carteira lia `zone`/`dy_real`/`p_now_p_min`/`gain_pct`
  direto do valuations.json enquanto exibia o preço vivo na mesma linha — logo a
  coluna Sinal mostrava a zona de semanas atrás, divergindo do screening e do
  modal (que leem decision_stocks.json).

  Caso real: FLRY3 apurado a 16,86 (<= alvo 6% de 16,98 → COMPRA) e negociado
  hoje a 18,23 (entre alvo 6% e alvo 5% de 20,37 → MONITORAR).

Cobertura:
  1. a zona é recalculada com o preço corrente, não herdada do snapshot
  2. paridade exata com decision_service._calc_zone (fonte do screening/modal)
  3. dy_real / p_now_p_min / gain_pct seguem as mesmas fórmulas do decision_service
  4. sem preço corrente, cai no snapshot em vez de quebrar
  5. a recomendação deriva da zona recalculada
"""

import pytest

from services.decision_service import _calc_zone
from services.portfolio_service import _recommend, _refresh_price_derived


# Snapshot real do FLRY3 em valuations.json (apurado em 2026-07-29)
FLRY3_SNAPSHOT = {
    "ticker":            "FLRY3",
    "price_now":         16.86,
    "price_target_5pct": 20.37,
    "price_target_6pct": 16.98,
    "price_target_8pct": 12.73,
    "price_min_6m":      14.31,
    "price_max_6m":      18.10,
    "avg_dividends_5y":  1.0186,
    "dy_real":           7.17,
    "p_now_p_min":       1.1782,
    "gain_pct_to_target": 0.71,
    "zone":              "COMPRA",
    "rank":              14,
    "rank_max":          21,
}

PRECO_HOJE = 18.23


def test_zona_recalculada_com_preco_corrente():
    """O snapshot diz COMPRA; a 18,23 a zona real é MONITORAR."""
    live = _refresh_price_derived(FLRY3_SNAPSHOT, PRECO_HOJE)
    assert live["zone"] == "MONITORAR"
    assert FLRY3_SNAPSHOT["zone"] == "COMPRA"  # snapshot intacto


def test_snapshot_nao_e_mutado():
    """O recálculo não pode escrever de volta no dict do valuations.json."""
    original = dict(FLRY3_SNAPSHOT)
    _refresh_price_derived(FLRY3_SNAPSHOT, PRECO_HOJE)
    assert FLRY3_SNAPSHOT == original


@pytest.mark.parametrize("preco, esperado", [
    (12.00, "COMPRA_FORTE"),   # <= alvo 8%
    (12.73, "COMPRA_FORTE"),   # limite do alvo 8%
    (16.00, "COMPRA"),         # entre alvo 8% e alvo 6%
    (16.98, "COMPRA"),         # limite do alvo 6%
    (18.23, "MONITORAR"),      # entre alvo 6% e alvo 5% — caso FLRY3
    (20.37, "MONITORAR"),      # limite do alvo 5%
    (25.00, "CARO"),           # acima do alvo 5%
])
def test_paridade_com_decision_service(preco, esperado):
    """A carteira precisa usar exatamente a mesma função do screening/modal."""
    live = _refresh_price_derived(FLRY3_SNAPSHOT, preco)
    assert live["zone"] == esperado
    assert live["zone"] == _calc_zone(
        preco,
        FLRY3_SNAPSHOT["price_target_6pct"],
        FLRY3_SNAPSHOT["price_target_8pct"],
        FLRY3_SNAPSHOT["price_target_5pct"],
    )


def test_metricas_derivadas_batem_com_decision_stocks():
    """Valores conferidos contra a entrada real do FLRY3 em decision_stocks.json."""
    live = _refresh_price_derived(FLRY3_SNAPSHOT, PRECO_HOJE)
    assert live["dy_real"]     == 5.59     # 1.0186 / 18.23
    assert live["p_now_p_min"] == 1.2739   # 18.23 / 14.31
    assert live["gain_pct"]    == -6.86    # (16.98 - 18.23) / 18.23


@pytest.mark.parametrize("preco", [None, 0, -1.0])
def test_sem_preco_corrente_cai_no_snapshot(preco):
    """Sem preço vivo não há o que recalcular — preserva o snapshot."""
    live = _refresh_price_derived(FLRY3_SNAPSHOT, preco)
    assert live["zone"]        == "COMPRA"
    assert live["dy_real"]     == 7.17
    assert live["p_now_p_min"] == 1.1782
    assert live["gain_pct"]    == 0.71


def test_alvos_ausentes_nao_quebram():
    """Ativo sem dividendos não tem alvos — não pode estourar exceção."""
    val = {"price_min_6m": 10.0, "rank": 3}
    live = _refresh_price_derived(val, 12.0)
    assert live["zone"]        == "CARO"
    assert live["dy_real"]     is None
    assert live["gain_pct"]    is None
    assert live["p_now_p_min"] == 1.2


def test_recomendacao_segue_a_zona_recalculada():
    """
    Com rank 14 e zona COMPRA do snapshot, _recommend devolveria COMPRAR_MAIS.
    Com a zona recalculada (MONITORAR) precisa virar AGUARDAR.
    """
    assert _recommend(FLRY3_SNAPSHOT) == "COMPRAR_MAIS"

    live = _refresh_price_derived(FLRY3_SNAPSHOT, PRECO_HOJE)
    val_live = dict(FLRY3_SNAPSHOT, **live)
    assert _recommend(val_live) == "AGUARDAR"
