"""
Testes unitários para PriceService.

Cobertura:
  1. fetch_from_google — leitura via Google Finance (httpx mockado)
     - preço lido com sucesso (vírgula como decimal)
     - preço lido com sucesso (ponto como decimal)
     - status HTTP != 200 → retorna None
     - bloco "YMlKec fxKbKc" ausente no HTML → retorna None
     - bloco presente mas sem número válido → retorna None
     - exceção de rede (timeout) → retorna None

  2. get_from_json — leitura do stock_prices.json (repositório mockado)
     - preço existe no JSON → retorna float
     - ticker não existe no JSON → retorna None

  3. update — busca ao vivo + persistência (repositório e http mockados)
     - fetch retorna preço válido → salva no repo e retorna preço
     - fetch retorna None → não chama save, retorna None
     - fetch retorna zero → não salva, retorna None
     - force=False e dentro do intervalo → retorna cache sem nova requisição
     - force=True dentro do intervalo → ignora cache e faz nova requisição
     - force=False e fora do intervalo → faz nova requisição
"""

from unittest.mock import MagicMock, patch, call
from datetime import datetime, timedelta

import pytest

from services.price_service import PriceService, GOOGLE_FINANCE_URL
from config.rules import PRICE_UPDATE_INTERVAL_HOURS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_html(price_str: str) -> str:
    """Monta HTML mínimo com o marcador de preço do Google Finance."""
    return f'<div class="YMlKec fxKbKc">{price_str}</div> extra content here'


def _make_mock_response(status_code: int = 200, text: str = "") -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    return response


def _make_http_factory(response: MagicMock):
    """Retorna uma factory que entrega um context-manager com a response mockada."""
    client = MagicMock()
    client.get.return_value = response
    client.__enter__ = MagicMock(return_value=client)
    client.__exit__ = MagicMock(return_value=False)
    return lambda: client


def _make_repo(price=None, all_prices=None, tickers=None):
    """Cria um mock do repositório com os valores informados."""
    mock_repo = MagicMock()
    mock_repo.get_price.return_value = price
    mock_repo.get_all_prices.return_value = all_prices or {}
    mock_repo.get_valid_tickers.return_value = tickers or []
    mock_repo.get_tickers_list.return_value = tickers or []
    return mock_repo


# ---------------------------------------------------------------------------
# 1. fetch_from_google
# ---------------------------------------------------------------------------

class TestFetchFromGoogle:

    def test_preco_virgula_decimal(self):
        """Preço BR com vírgula: '25,40' deve virar 25.40."""
        html = _make_html("R$25,40")
        svc = PriceService(http_client_factory=_make_http_factory(_make_mock_response(text=html)))

        price = svc.fetch_from_google("BBAS3")

        assert price == 25.40

    def test_preco_ponto_decimal(self):
        """Preço com ponto: '25.40' deve virar 25.40."""
        html = _make_html("25.40")
        svc = PriceService(http_client_factory=_make_http_factory(_make_mock_response(text=html)))

        price = svc.fetch_from_google("PETR4")

        assert price == 25.40

    def test_url_contem_ticker_e_bvmf(self):
        """A URL enviada ao Google deve ter o ticker e ':BVMF'."""
        html = _make_html("12,50")
        client = MagicMock()
        client.get.return_value = _make_mock_response(text=html)
        client.__enter__ = MagicMock(return_value=client)
        client.__exit__ = MagicMock(return_value=False)

        svc = PriceService(http_client_factory=lambda: client)
        svc.fetch_from_google("vale3")

        called_url = client.get.call_args[0][0]
        assert "VALE3" in called_url
        assert "BVMF" in called_url

    def test_status_404_retorna_none(self):
        """HTTP 404 → retorna None."""
        svc = PriceService(
            http_client_factory=_make_http_factory(_make_mock_response(status_code=404))
        )
        assert svc.fetch_from_google("BBAS3") is None

    def test_sem_bloco_price_retorna_none(self):
        """HTML sem o marcador 'YMlKec fxKbKc' → retorna None."""
        html = "<html>sem bloco de preco aqui</html>"
        svc = PriceService(
            http_client_factory=_make_http_factory(_make_mock_response(text=html))
        )
        assert svc.fetch_from_google("BBAS3") is None

    def test_bloco_sem_numero_retorna_none(self):
        """Marcador presente mas sem número → retorna None."""
        html = "qualquer coisa YMlKec fxKbKc sem numero aqui"
        svc = PriceService(
            http_client_factory=_make_http_factory(_make_mock_response(text=html))
        )
        assert svc.fetch_from_google("BBAS3") is None

    def test_excecao_de_rede_retorna_none(self):
        """Qualquer exceção na requisição → retorna None (sem estourar)."""
        def failing_factory():
            client = MagicMock()
            client.get.side_effect = Exception("connection timeout")
            client.__enter__ = MagicMock(return_value=client)
            client.__exit__ = MagicMock(return_value=False)
            return client

        svc = PriceService(http_client_factory=failing_factory)
        assert svc.fetch_from_google("BBAS3") is None

    def test_ticker_normalizado_para_maiusculo(self):
        """Ticker em minúsculo deve ser normalizado para maiúsculo na URL."""
        html = _make_html("10,00")
        client = MagicMock()
        client.get.return_value = _make_mock_response(text=html)
        client.__enter__ = MagicMock(return_value=client)
        client.__exit__ = MagicMock(return_value=False)

        svc = PriceService(http_client_factory=lambda: client)
        svc.fetch_from_google("itub4")

        called_url = client.get.call_args[0][0]
        assert "ITUB4" in called_url
        assert "itub4" not in called_url


# ---------------------------------------------------------------------------
# 2. get_from_json
# ---------------------------------------------------------------------------

class TestGetFromJson:

    def test_preco_existente_retorna_float(self):
        """Ticker salvo no JSON retorna o preço float."""
        mock_repo = _make_repo(price=32.50)
        svc = PriceService(repository=mock_repo)

        price = svc.get_from_json("BBAS3")

        assert price == 32.50
        mock_repo.get_price.assert_called_once_with("BBAS3")

    def test_ticker_inexistente_retorna_none(self):
        """Ticker sem entrada no JSON retorna None."""
        mock_repo = _make_repo(price=None)
        svc = PriceService(repository=mock_repo)

        price = svc.get_from_json("XXXX3")

        assert price is None

    def test_entrada_completa_get_entry(self):
        """get_entry_from_json retorna o dict completo com metadados."""
        entry = {
            "ticker": "BBAS3",
            "price_now": 32.50,
            "last_updated": "2026-03-15T10:00:00",
            "source": "google_finance",
        }
        mock_repo = _make_repo(all_prices={"BBAS3": entry})
        svc = PriceService(repository=mock_repo)

        result = svc.get_entry_from_json("BBAS3")

        assert result["price_now"] == 32.50
        assert result["source"] == "google_finance"
        assert result["last_updated"] == "2026-03-15T10:00:00"

    def test_entry_ticker_minusculo_normalizado(self):
        """get_entry_from_json normaliza ticker para maiúsculo antes de buscar."""
        entry = {"ticker": "PETR4", "price_now": 40.0, "last_updated": "2026-03-15T10:00:00"}
        mock_repo = _make_repo(all_prices={"PETR4": entry})
        svc = PriceService(repository=mock_repo)

        result = svc.get_entry_from_json("petr4")

        assert result is not None
        assert result["ticker"] == "PETR4"


# ---------------------------------------------------------------------------
# 3. needs_update
# ---------------------------------------------------------------------------

class TestNeedsUpdate:

    def test_sem_entrada_precisa_atualizar(self):
        mock_repo = _make_repo(all_prices={})
        svc = PriceService(repository=mock_repo)
        assert svc.needs_update("BBAS3") is True

    def test_dentro_do_intervalo_nao_precisa(self):
        recent = (datetime.now() - timedelta(minutes=30)).isoformat()
        entry = {"ticker": "BBAS3", "price_now": 32.0, "last_updated": recent}
        mock_repo = _make_repo(all_prices={"BBAS3": entry})
        svc = PriceService(repository=mock_repo)
        assert svc.needs_update("BBAS3") is False

    def test_fora_do_intervalo_precisa(self):
        old = (datetime.now() - timedelta(hours=PRICE_UPDATE_INTERVAL_HOURS + 1)).isoformat()
        entry = {"ticker": "BBAS3", "price_now": 32.0, "last_updated": old}
        mock_repo = _make_repo(all_prices={"BBAS3": entry})
        svc = PriceService(repository=mock_repo)
        assert svc.needs_update("BBAS3") is True

    def test_sem_last_updated_precisa(self):
        entry = {"ticker": "BBAS3", "price_now": 32.0}  # sem last_updated
        mock_repo = _make_repo(all_prices={"BBAS3": entry})
        svc = PriceService(repository=mock_repo)
        assert svc.needs_update("BBAS3") is True


# ---------------------------------------------------------------------------
# 4. update
# ---------------------------------------------------------------------------

class TestUpdate:

    def test_fetch_valido_salva_e_retorna_preco(self):
        """Google retorna preço → salva no repo e retorna o valor."""
        html = _make_html("45,30")
        mock_repo = _make_repo(all_prices={})  # sem cache → needs_update=True
        svc = PriceService(
            repository=mock_repo,
            http_client_factory=_make_http_factory(_make_mock_response(text=html)),
        )

        price = svc.update("WEGE3")

        assert price == 45.30
        mock_repo.save_price.assert_called_once_with("WEGE3", 45.30)

    def test_fetch_retorna_none_nao_salva(self):
        """Google retorna None → save_price não é chamado, retorna None."""
        html = "<html>sem preco</html>"
        mock_repo = _make_repo(all_prices={})
        svc = PriceService(
            repository=mock_repo,
            http_client_factory=_make_http_factory(_make_mock_response(text=html)),
        )

        price = svc.update("BBAS3")

        assert price is None
        mock_repo.save_price.assert_not_called()

    def test_fetch_retorna_zero_nao_salva(self):
        """Preço zero não é válido → save_price não é chamado."""
        html = _make_html("0,00")
        mock_repo = _make_repo(all_prices={})
        svc = PriceService(
            repository=mock_repo,
            http_client_factory=_make_http_factory(_make_mock_response(text=html)),
        )

        price = svc.update("BBAS3")

        assert price is None
        mock_repo.save_price.assert_not_called()

    def test_force_false_dentro_intervalo_usa_cache(self):
        """force=False e preço recente → retorna cache sem chamar fetch."""
        recent = (datetime.now() - timedelta(minutes=10)).isoformat()
        entry = {"ticker": "BBAS3", "price_now": 28.00, "last_updated": recent}
        mock_repo = _make_repo(price=28.00, all_prices={"BBAS3": entry})

        # Cria um client que vai falhar se chamado (não deve ser chamado)
        bad_client = MagicMock()
        bad_client.get.side_effect = AssertionError("fetch não deveria ser chamado")
        bad_client.__enter__ = MagicMock(return_value=bad_client)
        bad_client.__exit__ = MagicMock(return_value=False)

        svc = PriceService(repository=mock_repo, http_client_factory=lambda: bad_client)

        price = svc.update("BBAS3", force=False)

        assert price == 28.00
        mock_repo.save_price.assert_not_called()

    def test_force_true_ignora_cache_e_busca(self):
        """force=True → vai ao Google mesmo que o cache ainda seja recente."""
        recent = (datetime.now() - timedelta(minutes=10)).isoformat()
        entry = {"ticker": "BBAS3", "price_now": 28.00, "last_updated": recent}
        mock_repo = _make_repo(price=28.00, all_prices={"BBAS3": entry})

        html = _make_html("29,50")
        svc = PriceService(
            repository=mock_repo,
            http_client_factory=_make_http_factory(_make_mock_response(text=html)),
        )

        price = svc.update("BBAS3", force=True)

        assert price == 29.50
        mock_repo.save_price.assert_called_once_with("BBAS3", 29.50)

    def test_force_false_fora_do_intervalo_busca(self):
        """force=False mas cache expirado → vai ao Google."""
        old = (datetime.now() - timedelta(hours=PRICE_UPDATE_INTERVAL_HOURS + 2)).isoformat()
        entry = {"ticker": "BBAS3", "price_now": 28.00, "last_updated": old}
        mock_repo = _make_repo(price=28.00, all_prices={"BBAS3": entry})

        html = _make_html("30,10")
        svc = PriceService(
            repository=mock_repo,
            http_client_factory=_make_http_factory(_make_mock_response(text=html)),
        )

        price = svc.update("BBAS3", force=False)

        assert price == 30.10
        mock_repo.save_price.assert_called_once_with("BBAS3", 30.10)

    def test_ticker_normalizado_para_maiusculo_no_save(self):
        """save_price deve receber o ticker em maiúsculo independente da entrada."""
        html = _make_html("10,00")
        mock_repo = _make_repo(all_prices={})
        svc = PriceService(
            repository=mock_repo,
            http_client_factory=_make_http_factory(_make_mock_response(text=html)),
        )

        svc.update("itub4")

        args = mock_repo.save_price.call_args[0]
        assert args[0] == "ITUB4"


# ---------------------------------------------------------------------------
# 5. update_all
# ---------------------------------------------------------------------------

class TestUpdateAll:

    def test_atualiza_lista_fornecida(self):
        """update_all com lista explícita atualiza exatamente os tickers dados."""
        html = _make_html("20,00")
        mock_repo = _make_repo(all_prices={})
        svc = PriceService(
            repository=mock_repo,
            http_client_factory=_make_http_factory(_make_mock_response(text=html)),
        )

        results = svc.update_all(tickers=["BBAS3", "PETR4"], delay=0)

        assert set(results.keys()) == {"BBAS3", "PETR4"}
        assert results["BBAS3"] == 20.0
        assert results["PETR4"] == 20.0
        assert mock_repo.save_price.call_count == 2

    def test_usa_tickers_validos_quando_lista_none(self):
        """Sem lista → usa get_valid_tickers do repositório."""
        html = _make_html("15,00")
        mock_repo = _make_repo(all_prices={}, tickers=["VALE3", "BBAS3"])
        mock_repo.get_valid_tickers.return_value = ["VALE3", "BBAS3"]
        svc = PriceService(
            repository=mock_repo,
            http_client_factory=_make_http_factory(_make_mock_response(text=html)),
        )

        results = svc.update_all(delay=0)

        assert "VALE3" in results
        assert "BBAS3" in results

    def test_falha_parcial_nao_interrompe_lote(self):
        """Se um ticker falha, o lote continua e o resultado é None para ele."""
        responses = iter([
            _make_mock_response(text=_make_html("10,00")),
            _make_mock_response(text="<html>sem preco</html>"),
            _make_mock_response(text=_make_html("20,00")),
        ])

        def rotating_factory():
            resp = next(responses)
            client = MagicMock()
            client.get.return_value = resp
            client.__enter__ = MagicMock(return_value=client)
            client.__exit__ = MagicMock(return_value=False)
            return client

        mock_repo = _make_repo(all_prices={})
        svc = PriceService(repository=mock_repo, http_client_factory=rotating_factory)

        results = svc.update_all(tickers=["BBAS3", "FAIL3", "WEGE3"], delay=0)

        assert results["BBAS3"] == 10.0
        assert results["FAIL3"] is None
        assert results["WEGE3"] == 20.0
