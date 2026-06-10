"""
Testes unitários para swing_service — fatores de assertividade da nota
(desconto vs. médias 1m/3m/6m e volume crescente).
"""

from config import rules
from services import swing_service as svc


# ---------------------------------------------------------------
# _below_avg_count
# ---------------------------------------------------------------

class TestBelowAvgCount:
    def test_preco_abaixo_das_tres_medias(self):
        # 129 fechamentos a 10.0 e o último a 9.0: abaixo de 1m, 3m e 6m
        closes = [10.0] * 129 + [9.0]
        assert svc._below_avg_count(closes) == 3

    def test_preco_acima_de_todas_as_medias(self):
        # série ascendente: último preço é o topo, acima de qualquer média
        closes = [float(i) for i in range(1, 131)]
        assert svc._below_avg_count(closes) == 0

    def test_historico_curto_ignora_media_6m(self):
        # 70 closes: médias 1m/3m existem, 6m (126) não — conta no máx. 2
        closes = [10.0] * 69 + [9.0]
        assert svc._below_avg_count(closes) == 2

    def test_abaixo_apenas_da_media_curta(self):
        # caiu recente: abaixo da média 1m, mas ainda acima das médias longas
        closes = [5.0] * 100 + [20.0] * 29 + [15.0]
        assert svc._below_avg_count(closes) == 1


# ---------------------------------------------------------------
# _vol_rising
# ---------------------------------------------------------------

class TestVolRising:
    def test_volume_crescente(self):
        volumes = [100.0] * 42 + [200.0] * 21   # média 1m=200 > média 3m≈133
        assert svc._vol_rising(volumes) is True

    def test_volume_decrescente(self):
        volumes = [200.0] * 42 + [100.0] * 21   # média 1m=100 < média 3m≈167
        assert svc._vol_rising(volumes) is False

    def test_historico_insuficiente_retorna_false(self):
        volumes = [100.0] * 30                  # < 63: média 3m indisponível
        assert svc._vol_rising(volumes) is False


# ---------------------------------------------------------------
# build_context expõe os campos novos
# ---------------------------------------------------------------

def _ohlcv(n, close=10.0, vol=100.0):
    closes = [close] * n
    highs = [close + 0.5] * n
    lows = [close - 0.5] * n
    volumes = [vol] * n
    return closes, highs, lows, volumes


class TestBuildContext:
    def test_contexto_tem_below_avgs_e_vol_rising(self):
        closes, highs, lows, volumes = _ohlcv(130)
        ctx = svc.build_context(closes, highs, lows, volumes)
        assert "below_avgs" in ctx
        assert "vol_rising" in ctx
        assert ctx["below_avgs"] == 0          # série plana: nunca estritamente abaixo
        assert ctx["vol_rising"] is False      # volume constante
