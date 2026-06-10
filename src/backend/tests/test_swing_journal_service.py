"""
Testes unitários para swing_journal_service (diário de operações de swing).

Cobertura (funções puras, determinísticas):
  1. enrich_open    — P&L flutuante, %, dias na carteira, distância stop/alvo
  2. enrich_closed  — P&L realizado, %, valor da venda, dias entre compra e venda
  3. darf_summary   — soma das vendas do mês corrente vs. limite (ok/warn/over)
  4. add/close/update/delete — orquestração + validação (repo em memória)
  5. list_positions — separa abertas/fechadas, enriquece e calcula DARF
"""

import copy
from datetime import date

import pytest

from services import swing_journal_service as svc


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _open_pos(**kw):
    base = {
        "id": "X1", "ticker": "PETR4", "qty": 100,
        "entry_date": "2026-06-01", "entry_price": 16.0,
        "stop": 15.0, "target": 18.0,
        "exit_date": None, "exit_price": None,
        "status": "open", "source": "manual", "notes": "",
    }
    base.update(kw)
    return base


def _closed_pos(**kw):
    base = _open_pos(status="closed", exit_date="2026-06-21", exit_price=18.0)
    base.update(kw)
    return base


@pytest.fixture
def mem_repo(monkeypatch):
    """Repositório em memória (round-trip com deepcopy, imitando o disco)."""
    store = {"positions": []}
    monkeypatch.setattr(svc.repo, "load_swing_positions",
                        lambda: copy.deepcopy(store["positions"]))
    monkeypatch.setattr(svc.repo, "save_swing_positions",
                        lambda positions: store.__setitem__("positions", copy.deepcopy(positions)))
    return store


# ---------------------------------------------------------------------------
# 1. enrich_open — P&L flutuante
# ---------------------------------------------------------------------------

class TestEnrichOpen:

    def test_lucro(self):
        out = svc.enrich_open(_open_pos(), current_price=17.0, today=date(2026, 6, 11))
        assert out["current_price"] == 17.0
        assert out["unrealized_pl"] == 100.0            # (17-16)*100
        assert out["unrealized_pct"] == 6.25            # (17/16-1)*100
        assert out["days_held"] == 10                   # 01 → 11 de junho

    def test_prejuizo(self):
        out = svc.enrich_open(_open_pos(), current_price=15.5, today=date(2026, 6, 11))
        assert out["unrealized_pl"] == -50.0            # (15.5-16)*100
        assert out["unrealized_pct"] == -3.12           # round(-3.125,2) → half-to-even

    def test_distancia_stop_e_alvo(self):
        out = svc.enrich_open(_open_pos(), current_price=17.0, today=date(2026, 6, 11))
        assert out["dist_stop_pct"] == 13.33            # (17/15-1)*100 — acima do stop
        assert out["dist_target_pct"] == 5.88           # (18/17-1)*100 — falta p/ o alvo

    def test_sem_preco_atual(self):
        out = svc.enrich_open(_open_pos(), current_price=None, today=date(2026, 6, 11))
        assert out["current_price"] is None
        assert out["unrealized_pl"] is None
        assert out["unrealized_pct"] is None
        assert out["dist_stop_pct"] is None
        assert out["dist_target_pct"] is None
        assert out["days_held"] == 10                   # dias continua calculado


# ---------------------------------------------------------------------------
# 2. enrich_closed — P&L realizado
# ---------------------------------------------------------------------------

class TestEnrichClosed:

    def test_resultado_e_valor_venda(self):
        out = svc.enrich_closed(_closed_pos())
        assert out["realized_pl"] == 200.0              # (18-16)*100
        assert out["realized_pct"] == 12.5              # (18/16-1)*100
        assert out["sale_value"] == 1800.0              # 18*100
        assert out["days_held"] == 20                   # 01 → 21 de junho

    def test_prejuizo_realizado(self):
        out = svc.enrich_closed(_closed_pos(exit_price=15.0))
        assert out["realized_pl"] == -100.0             # (15-16)*100
        assert out["realized_pct"] == -6.25


# ---------------------------------------------------------------------------
# 3. darf_summary — vendas do mês vs. limite de isenção
# ---------------------------------------------------------------------------

class TestDarfSummary:

    def test_ok_abaixo_do_alerta(self):
        # 2 vendas de R$900 = R$1.800 → bem abaixo de R$18.000
        positions = [
            _closed_pos(qty=100, exit_price=9.0, exit_date="2026-06-05"),
            _closed_pos(qty=100, exit_price=9.0, exit_date="2026-06-20"),
        ]
        d = svc.darf_summary(positions, "2026-06")
        assert d["total_sales"] == 1800.0
        assert d["limit"] == 20000.0
        assert d["warn_threshold"] == 18000.0
        assert d["status"] == "ok"
        assert d["pct"] == 9.0

    def test_warn_no_limiar_de_18000(self):
        positions = [_closed_pos(qty=1000, exit_price=18.0, exit_date="2026-06-10")]
        d = svc.darf_summary(positions, "2026-06")
        assert d["total_sales"] == 18000.0
        assert d["status"] == "warn"

    def test_over_no_limiar_de_20000(self):
        positions = [_closed_pos(qty=1000, exit_price=20.0, exit_date="2026-06-10")]
        d = svc.darf_summary(positions, "2026-06")
        assert d["total_sales"] == 20000.0
        assert d["status"] == "over"

    def test_considera_apenas_o_mes_pedido(self):
        positions = [
            _closed_pos(qty=1000, exit_price=20.0, exit_date="2026-05-30"),  # outro mês
            _closed_pos(qty=100, exit_price=10.0, exit_date="2026-06-15"),   # conta
        ]
        d = svc.darf_summary(positions, "2026-06")
        assert d["total_sales"] == 1000.0
        assert d["status"] == "ok"

    def test_ignora_posicoes_abertas(self):
        positions = [_open_pos(qty=1000)]   # aberta, sem venda
        d = svc.darf_summary(positions, "2026-06")
        assert d["total_sales"] == 0.0
        assert d["status"] == "ok"


# ---------------------------------------------------------------------------
# 4. add / close / update / delete — orquestração
# ---------------------------------------------------------------------------

class TestCrud:

    def test_add_cria_aberta_com_id(self, mem_repo):
        pos = svc.add_position({
            "ticker": "vale3", "qty": 100, "entry_price": 60.0,
            "entry_date": "2026-06-01", "stop": 57.0, "target": 66.0,
            "source": "signal",
        })
        assert pos["id"]
        assert pos["ticker"] == "VALE3"        # normaliza p/ maiúsculas
        assert pos["status"] == "open"
        assert pos["exit_price"] is None
        assert len(mem_repo["positions"]) == 1

    def test_add_rejeita_campo_obrigatorio_ausente(self, mem_repo):
        with pytest.raises(ValueError):
            svc.add_position({"ticker": "VALE3", "qty": 100, "entry_price": 60.0})  # sem entry_date

    def test_close_transiciona_para_fechada(self, mem_repo):
        pos = svc.add_position({
            "ticker": "VALE3", "qty": 100, "entry_price": 60.0, "entry_date": "2026-06-01",
        })
        closed = svc.close_position(pos["id"], exit_price=66.0, exit_date="2026-06-20")
        assert closed["status"] == "closed"
        assert closed["exit_price"] == 66.0
        assert closed["exit_date"] == "2026-06-20"

    def test_close_id_inexistente(self, mem_repo):
        with pytest.raises(KeyError):
            svc.close_position("nao-existe", exit_price=10.0, exit_date="2026-06-20")

    def test_update_edita_stop_e_alvo(self, mem_repo):
        pos = svc.add_position({
            "ticker": "VALE3", "qty": 100, "entry_price": 60.0, "entry_date": "2026-06-01",
        })
        upd = svc.update_position(pos["id"], {"stop": 58.0, "target": 70.0})
        assert upd["stop"] == 58.0
        assert upd["target"] == 70.0

    def test_delete_remove(self, mem_repo):
        pos = svc.add_position({
            "ticker": "VALE3", "qty": 100, "entry_price": 60.0, "entry_date": "2026-06-01",
        })
        assert svc.delete_position(pos["id"]) is True
        assert mem_repo["positions"] == []

    def test_delete_id_inexistente_retorna_false(self, mem_repo):
        assert svc.delete_position("nao-existe") is False


# ---------------------------------------------------------------------------
# 5. list_positions — orquestração completa
# ---------------------------------------------------------------------------

class TestListPositions:

    def test_separa_abertas_fechadas_e_calcula_darf(self, mem_repo, monkeypatch):
        today = date.today()
        this_month = "%04d-%02d" % (today.year, today.month)
        mem_repo["positions"] = [
            _open_pos(id="A", ticker="PETR4", entry_date="2026-06-01"),
            _closed_pos(id="B", ticker="VALE3", qty=100, entry_price=60.0,
                        exit_price=66.0, exit_date=this_month + "-15"),
        ]
        monkeypatch.setattr(svc.repo, "get_all_prices",
                            lambda: {"PETR4": {"price_now": 17.0}})
        monkeypatch.setattr(svc.repo, "load_swing_data", lambda: [])

        out = svc.list_positions()
        assert len(out["open"]) == 1
        assert len(out["closed"]) == 1
        assert out["open"][0]["current_price"] == 17.0
        assert out["open"][0]["unrealized_pl"] == 100.0
        assert out["closed"][0]["sale_value"] == 6600.0
        assert out["darf"]["month"] == this_month
        assert out["darf"]["total_sales"] == 6600.0

    def test_preco_atual_usa_fallback_do_swing_data(self, mem_repo, monkeypatch):
        mem_repo["positions"] = [_open_pos(id="A", ticker="PETR4")]
        monkeypatch.setattr(svc.repo, "get_all_prices", lambda: {})  # sem preço em prices
        monkeypatch.setattr(svc.repo, "load_swing_data",
                            lambda: [{"ticker": "PETR4", "price": 16.5}])

        out = svc.list_positions()
        assert out["open"][0]["current_price"] == 16.5


# ---------------------------------------------------------------------------
# 6. position_alerts — alertas de stop/alvo p/ operações abertas
# ---------------------------------------------------------------------------

class TestPositionAlerts:

    def test_stop_disparado(self):
        pos = [_open_pos(id="A", ticker="PETR4", stop=15.0, target=18.0)]
        a = svc.position_alerts(pos, {"PETR4": 14.9})
        assert len(a) == 1
        assert a[0]["type"] == "stop"
        assert a[0]["ticker"] == "PETR4"
        assert a[0]["threshold"] == 15.0
        assert a[0]["id"] == "A"
        assert a[0]["price"] == 14.9

    def test_stop_no_limiar(self):
        a = svc.position_alerts([_open_pos(stop=15.0, target=18.0)], {"PETR4": 15.0})
        assert [x["type"] for x in a] == ["stop"]

    def test_alvo_disparado_no_limiar(self):
        a = svc.position_alerts([_open_pos(stop=15.0, target=18.0)], {"PETR4": 18.0})
        assert [x["type"] for x in a] == ["target"]

    def test_entre_stop_e_alvo_nao_dispara(self):
        assert svc.position_alerts([_open_pos(stop=15.0, target=18.0)], {"PETR4": 16.5}) == []

    def test_sem_preco_ignora(self):
        assert svc.position_alerts([_open_pos(ticker="PETR4", stop=15.0, target=18.0)], {}) == []

    def test_so_alvo_quando_sem_stop(self):
        a = svc.position_alerts([_open_pos(stop=None, target=18.0)], {"PETR4": 18.5})
        assert [x["type"] for x in a] == ["target"]
        # sem stop não dispara stop mesmo com preço baixo
        assert svc.position_alerts([_open_pos(stop=None, target=18.0)], {"PETR4": 1.0}) == []
