"""
Testes unitários para history_dashboard_service.

Cobertura:
  1. build_dashboard (lógica pura, série sintética determinística)
     - série/acumulado/labels
     - detecção de marcos de 10K (data + meses desde o marco anterior)
     - próximo marco: progresso, faltante, next_milestone
     - previsão faixa 6–12m (otimista = ETA mais cedo)
     - comparativo YTD (mesmo período ano anterior)
     - agregação por ano (total, média mensal, crescimento A/A)
     - agregação por trimestre
  2. load (integração com o Excel real data/History/B3.xlsx)
     - trava os números reais do dashboard do usuário
"""

import os
from datetime import datetime

import pytest

from services.history_dashboard_service import build_dashboard, load


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _series(start_year, start_month, values, patrimony=50000.0):
    """Constrói uma série mensal [(datetime, value, patrimony)] a partir de
    uma lista de proventos mensais, incrementando o mês a cada item."""
    out = []
    y, m = start_year, start_month
    for v in values:
        out.append((datetime(y, m, 1), float(v), float(patrimony)))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def _next_milestone(d):
    """Retorna o dict do próximo marco (o único com reached=False)."""
    return [ms for ms in d["milestones"] if not ms["reached"]][-1]


def _reached(d):
    return [ms for ms in d["milestones"] if ms["reached"]]


# ---------------------------------------------------------------------------
# 1. build_dashboard — série e acumulado
# ---------------------------------------------------------------------------

class TestSeriesEAcumulado:

    def test_labels_no_formato_ano_mes(self):
        d = build_dashboard(_series(2020, 1, [1000, 1000, 1000, 1000, 1000]))
        assert d["series"]["labels"] == ["2020-01", "2020-02", "2020-03", "2020-04", "2020-05"]

    def test_acumulado_e_soma_corrida(self):
        d = build_dashboard(_series(2020, 1, [1000, 1000, 1000, 1000, 1000]))
        assert d["series"]["acumulado"] == [1000, 2000, 3000, 4000, 5000]

    def test_proventos_mes_preservados(self):
        d = build_dashboard(_series(2020, 1, [100, 250, 50]))
        assert d["series"]["proventos_mes"] == [100, 250, 50]

    def test_total_e_ultimo_mes_no_summary(self):
        d = build_dashboard(_series(2020, 1, [1000, 1000, 1000, 1000, 1000]))
        assert d["summary"]["total_proventos"] == 5000
        assert d["summary"]["last_month"] == "2020-05"
        assert d["summary"]["patrimony"] == 50000


# ---------------------------------------------------------------------------
# 2. build_dashboard — marcos de 10K
# ---------------------------------------------------------------------------

class TestMarcos10K:

    def test_marcos_atingidos_data_e_meses(self):
        # 25 meses de R$1000 → acumulado cruza 10K no mês 10 e 20K no mês 20
        d = build_dashboard(_series(2020, 1, [1000] * 25))
        reached = _reached(d)
        targets = {ms["target"]: ms for ms in reached}

        assert 10000 in targets
        assert targets[10000]["date"] == "2020-10"
        assert targets[10000]["months"] == 10  # desde o início (2020-01), inclusivo

        assert 20000 in targets
        assert targets[20000]["date"] == "2021-08"
        assert targets[20000]["months"] == 11  # desde o marco anterior (2020-10), inclusivo

    def test_proximo_marco_progresso_e_faltante(self):
        d = build_dashboard(_series(2020, 1, [1000] * 25))  # total = 25000
        nxt = _next_milestone(d)
        assert nxt["reached"] is False
        assert nxt["target"] == 30000
        assert nxt["progress_pct"] == 50.0          # (25000-20000)/10000
        assert d["summary"]["next_milestone"] == 30000
        assert d["summary"]["progress_pct"] == 50.0
        assert d["summary"]["remaining"] == 5000.0


# ---------------------------------------------------------------------------
# 3. build_dashboard — previsão faixa 6–12 meses
# ---------------------------------------------------------------------------

class TestPrevisao:

    def test_faixa_otimista_e_conservadora(self):
        # 6 meses a R$500 + 6 meses a R$1500 → total 12000
        # ritmo recente (6m)=1500 > ritmo 12m=1000 ⇒ 6m é o otimista
        d = build_dashboard(_series(2020, 1, [500] * 6 + [1500] * 6))
        nxt = _next_milestone(d)
        fc = nxt["forecast"]

        assert nxt["target"] == 20000
        assert nxt["remaining"] == 8000.0

        # otimista = ETA mais cedo
        assert fc["optimistic"]["rate"] == 1500.0
        assert fc["optimistic"]["window_months"] == 6
        assert fc["optimistic"]["eta"] == "2021-06"   # 2020-12 + ceil(8000/1500)=6

        assert fc["conservative"]["rate"] == 1000.0
        assert fc["conservative"]["window_months"] == 12
        assert fc["conservative"]["eta"] == "2021-08"  # 2020-12 + 8000/1000=8

        assert fc["optimistic"]["eta"] <= fc["conservative"]["eta"]

    def test_previsao_meses_arredondado(self):
        d = build_dashboard(_series(2020, 1, [500] * 6 + [1500] * 6))
        fc = _next_milestone(d)["forecast"]
        assert fc["optimistic"]["months"] == 5.3      # round(8000/1500, 1)
        assert fc["conservative"]["months"] == 8.0


# ---------------------------------------------------------------------------
# 4. build_dashboard — comparativo YTD
# ---------------------------------------------------------------------------

class TestYTD:

    def test_compara_mesmo_periodo_do_ano_anterior(self):
        # 2024: 12 meses de 100 ; 2025: 5 meses (jan–mai) de 300
        serie = _series(2024, 1, [100] * 12 + [300] * 5)
        d = build_dashboard(serie)
        s = d["summary"]
        assert s["ytd_current"] == {"year": 2025, "value": 1500.0}   # jan–mai 2025
        assert s["ytd_prev"] == {"year": 2024, "value": 500.0}       # jan–mai 2024 (5×100)
        assert s["ytd_growth_pct"] == 200.0                          # (1500/500-1)*100


# ---------------------------------------------------------------------------
# 5. build_dashboard — por ano e por trimestre
# ---------------------------------------------------------------------------

class TestAgregacoes:

    def test_por_ano_total_media_e_crescimento(self):
        serie = _series(2024, 1, [100] * 12 + [300] * 5)
        d = build_dashboard(serie)
        by_year = {y["year"]: y for y in d["by_year"]}

        assert by_year[2024]["total"] == 1200.0
        assert by_year[2024]["monthly_avg"] == 100.0     # ano completo → /12
        assert by_year[2024]["growth_pct"] is None       # primeiro ano

        assert by_year[2025]["total"] == 1500.0
        assert by_year[2025]["monthly_avg"] == 300.0     # ano corrente → /meses presentes (5)
        assert by_year[2025]["growth_pct"] == 25.0       # (1500/1200-1)*100

    def test_por_trimestre_soma_e_label(self):
        serie = _series(2024, 1, [100] * 12 + [300] * 5)
        d = build_dashboard(serie)
        by_q = {q["label"]: q["total"] for q in d["by_quarter"]}

        assert by_q["Q1 2024"] == 300.0     # jan+fev+mar
        assert by_q["Q1 2025"] == 900.0     # jan+fev+mar 2025 (3×300)
        assert by_q["Q2 2025"] == 600.0     # abr+mai 2025 (2×300, trimestre parcial)
        # ordem cronológica ascendente
        assert d["by_quarter"][0]["label"] == "Q1 2024"


# ---------------------------------------------------------------------------
# 6. load — integração com o Excel real
# ---------------------------------------------------------------------------

_REAL_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "History", "B3.xlsx",
)


@pytest.mark.skipif(not os.path.exists(_REAL_FILE), reason="B3.xlsx não disponível")
class TestArquivoReal:

    def test_summary_numeros_reais(self):
        d = load()
        s = d["summary"]
        assert s["total_proventos"] == pytest.approx(25738.65, abs=0.5)
        assert s["patrimony"] == pytest.approx(127474.02, abs=1.0)
        assert s["last_month"] == "2026-05"
        assert s["next_milestone"] == 30000
        assert s["progress_pct"] == pytest.approx(57.39, abs=0.3)
        assert s["remaining"] == pytest.approx(4261.35, abs=1.0)

    def test_marcos_reais(self):
        d = load()
        targets = {ms["target"]: ms for ms in d["milestones"] if ms["reached"]}
        assert targets[10000]["date"] == "2024-07"
        assert targets[10000]["months"] == 48
        assert targets[20000]["date"] == "2025-11"
        assert targets[20000]["months"] == 17

    def test_ytd_real(self):
        s = load()["summary"]
        assert s["ytd_current"]["year"] == 2026
        assert s["ytd_current"]["value"] == pytest.approx(3817.39, abs=1.0)
        assert s["ytd_prev"]["year"] == 2025
        assert s["ytd_prev"]["value"] == pytest.approx(2370.98, abs=1.0)
        assert s["ytd_growth_pct"] == pytest.approx(61.0, abs=1.5)

    def test_previsao_presente_e_ordenada(self):
        d = load()
        fc = _next_milestone(d)["forecast"]
        assert fc["optimistic"]["eta"] <= fc["conservative"]["eta"]
        assert fc["optimistic"]["window_months"] == 6
        assert fc["conservative"]["window_months"] == 12

    def test_por_ano_real(self):
        by_year = {y["year"]: y for y in load()["by_year"]}
        assert by_year[2020]["total"] == pytest.approx(138.62, abs=0.5)
        assert by_year[2025]["total"] == pytest.approx(9482.87, abs=1.0)

    def test_por_trimestre_comeca_q3_2020(self):
        d = load()
        assert d["by_quarter"][0]["label"] == "Q3 2020"
