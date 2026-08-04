"""
Testes do auto-seed dos JSONs base no stock_repository.

Cobertura:
  1. stocks_list.json (semente data/seed_stocks/stocks_file_2026)
     - recria quando ausente, vazio (0 bytes), com JSON inválido
       ou com a lista de tickers vazia
     - normalização da semente: maiúsculas, sem duplicatas, sem linhas vazias
       ou comentários, ordenado
     - formato gravado igual ao template (description/source/last_updated/count/tickers)
     - arquivo válido existente é preservado (não recria)
     - erro claro quando nem o JSON nem a semente existem
  2. JSONs indexados por ticker — stock_validity, stock_history, stock_prices,
     financials_history e valuations (esqueleto embutido em SKELETONS)
     - recria vazio quando ausente, vazio (0 bytes), corrompido ou sem "stocks"
     - leitura e escrita funcionam com o arquivo ausente (casos reais do
       stock_validator, history_fetcher, price_service, financials_fetcher
       e valuation_calculator)
     - arquivo íntegro é preservado, inclusive sem nenhum ticker
"""

import json
import os

import pytest

from repositories import stock_repository as repo


SEED_CONTENT = "PETR4\nBBAS3\nabev3\n\n# comentário\nVALE3\nPETR4\n"
SEED_EXPECTED = ["ABEV3", "BBAS3", "PETR4", "VALE3"]

VALIDITY_ENTRIES = {
    "PETR4": {"ticker": "PETR4", "is_valid": True,  "check_count": 3},
    "OSXB3": {"ticker": "OSXB3", "is_valid": False, "reason_invalid": "delisted"},
}


@pytest.fixture
def paths(tmp_path, monkeypatch):
    """Aponta os arquivos base e a semente para um diretório temporário."""
    seed_dir = tmp_path / "seed_stocks"
    seed_dir.mkdir()
    seed_file = seed_dir / "stocks_file_2026"
    seed_file.write_text(SEED_CONTENT, encoding="utf-8")

    patched = dict(repo.PATHS)
    patched["stocks_list"] = str(tmp_path / "stocks_list.json")
    patched["stocks_seed"] = str(seed_file)
    patched["validity"]    = str(tmp_path / "stock_validity.json")
    patched["history"]     = str(tmp_path / "stock_history.json")
    patched["prices"]      = str(tmp_path / "stock_prices.json")
    patched["financials_history"] = str(tmp_path / "financials_history.json")
    patched["valuations"]  = str(tmp_path / "valuations.json")
    monkeypatch.setattr(repo, "PATHS", patched)
    return patched


def _write(paths, key, content):
    with open(paths[key], "w", encoding="utf-8") as f:
        f.write(content)


def _write_list(paths, content):
    _write(paths, "stocks_list", content)


def _write_validity(paths, content):
    _write(paths, "validity", content)


# ---------------------------------------------------------------------------
# Recriação
# ---------------------------------------------------------------------------

def test_recria_quando_arquivo_ausente(paths):
    assert not os.path.exists(paths["stocks_list"])

    assert repo.get_tickers_list() == SEED_EXPECTED
    assert os.path.exists(paths["stocks_list"])


def test_recria_quando_arquivo_vazio(paths):
    _write_list(paths, "")

    assert repo.get_tickers_list() == SEED_EXPECTED


def test_recria_quando_json_invalido(paths):
    _write_list(paths, "{ isso não é json")

    assert repo.get_tickers_list() == SEED_EXPECTED


def test_recria_quando_lista_de_tickers_vazia(paths):
    _write_list(paths, json.dumps({"description": "x", "count": 0, "tickers": []}))

    assert repo.get_tickers_list() == SEED_EXPECTED


def test_recria_quando_chave_tickers_ausente(paths):
    _write_list(paths, json.dumps({"description": "x"}))

    assert repo.get_tickers_list() == SEED_EXPECTED


# ---------------------------------------------------------------------------
# Formato gravado
# ---------------------------------------------------------------------------

def test_arquivo_recriado_segue_o_template(paths):
    repo.get_tickers_list()

    with open(paths["stocks_list"], encoding="utf-8") as f:
        data = json.load(f)

    assert sorted(data.keys()) == sorted(
        ["description", "source", "last_updated", "count", "tickers"]
    )
    assert data["description"] == repo.SEED_DESCRIPTION
    assert data["source"] == repo.SEED_SOURCE
    assert data["count"] == len(data["tickers"]) == len(SEED_EXPECTED)
    assert data["tickers"] == SEED_EXPECTED
    assert data["last_updated"]  # isoformat gravado


def test_semente_normalizada_sem_duplicatas_e_ordenada(paths):
    tickers = repo.get_tickers_list()

    assert tickers == sorted(tickers)
    assert len(tickers) == len(set(tickers))
    assert all(t == t.upper() for t in tickers)


# ---------------------------------------------------------------------------
# Preservação e erro
# ---------------------------------------------------------------------------

def test_nao_recria_quando_arquivo_valido(paths):
    original = json.dumps({"description": "manual", "count": 1, "tickers": ["XPTO3"]})
    _write_list(paths, original)

    assert repo.get_tickers_list() == ["XPTO3"]

    with open(paths["stocks_list"], encoding="utf-8") as f:
        assert json.load(f)["description"] == "manual"


def test_erro_quando_semente_tambem_ausente(paths):
    os.remove(paths["stocks_seed"])

    with pytest.raises(FileNotFoundError):
        repo.get_tickers_list()


def test_rebuild_forca_recriacao_mesmo_com_arquivo_valido(paths):
    _write_list(paths, json.dumps({"tickers": ["XPTO3"]}))

    data = repo.rebuild_stocks_list()

    assert data["tickers"] == SEED_EXPECTED
    assert repo.get_tickers_list() == SEED_EXPECTED


# ---------------------------------------------------------------------------
# stock_validity.json / stock_history.json — esqueleto embutido (SKELETONS)
# ---------------------------------------------------------------------------

TICKER_FILES = ["validity", "history", "prices", "financials_history", "valuations"]

# leitura pública que dispara o auto-seed de cada arquivo
READERS = {
    "validity": lambda: repo.get_validity("PETR4"),
    "history":  lambda: repo.get_history("PETR4"),
    "prices":   lambda: repo.get_price("PETR4"),
    "financials_history": lambda: repo.get_financials("PETR4"),
    "valuations": lambda: repo.get_valuation("PETR4"),
}

CONTEUDOS_INVALIDOS = [
    "",                                          # 0 bytes
    "{ isso não é json",                         # corrompido
    json.dumps({"last_updated": "2026-01-01"}),  # sem a chave stocks
    json.dumps({"stocks": []}),                  # stocks com tipo errado
]


@pytest.mark.parametrize("key", TICKER_FILES)
def test_ticker_file_recria_quando_ausente(paths, key):
    assert not os.path.exists(paths[key])

    assert READERS[key]() is None  # arquivo novo não tem tickers
    assert os.path.exists(paths[key])


@pytest.mark.parametrize("key", TICKER_FILES)
@pytest.mark.parametrize("conteudo", CONTEUDOS_INVALIDOS)
def test_ticker_file_recria_quando_vazio_ou_invalido(paths, key, conteudo):
    _write(paths, key, conteudo)

    assert READERS[key]() is None

    with open(paths[key], encoding="utf-8") as f:
        assert json.load(f)["stocks"] == {}


@pytest.mark.parametrize("key", TICKER_FILES)
def test_ticker_file_recriado_segue_o_esqueleto(paths, key):
    READERS[key]()

    with open(paths[key], encoding="utf-8") as f:
        data = json.load(f)

    esqueleto = repo.SKELETONS[key]
    assert sorted(data.keys()) == sorted(list(esqueleto) + ["last_updated", "stocks"])
    for campo, valor in esqueleto.items():   # _description e, quando existe, _schema
        assert data[campo] == valor
    assert data["stocks"] == {}
    assert data["last_updated"]


@pytest.mark.parametrize("key", TICKER_FILES)
def test_ticker_file_preserva_arquivo_integro_sem_tickers(paths, key):
    """Arquivo recém-criado (stocks vazio) é legítimo — não pode ser reescrito
    a cada leitura, senão o fetcher regrava o JSON 600+ vezes por rodada."""
    _write(paths, key, json.dumps({"marcador": 1, "stocks": {}}))

    assert READERS[key]() is None

    with open(paths[key], encoding="utf-8") as f:
        assert json.load(f)["marcador"] == 1


# ---------------------------------------------------------------------------
# stock_validity.json — API específica
# ---------------------------------------------------------------------------

def test_validity_nao_recria_quando_arquivo_valido(paths):
    _write_validity(paths, json.dumps({"stocks": {"XPTO3": {"is_valid": False}}}))

    assert repo.get_validity("XPTO3") == {"is_valid": False}


def test_save_validity_funciona_com_arquivo_ausente(paths):
    """Caso real do stock_validator.py: primeiro acesso sem o JSON no disco."""
    repo.save_validity("WEGE3", {"is_valid": True, "check_count": 1})

    with open(paths["validity"], encoding="utf-8") as f:
        data = json.load(f)

    assert data["stocks"]["WEGE3"]["ticker"] == "WEGE3"
    assert data["stocks"]["WEGE3"]["last_check"]
    assert data["_schema"] == repo.SKELETONS["validity"]["_schema"]


def test_valid_e_invalid_tickers_com_arquivo_ausente(paths):
    assert repo.get_valid_tickers() == []
    assert repo.get_invalid_tickers() == []


def test_valid_e_invalid_tickers_apos_popular(paths):
    for ticker, entry in VALIDITY_ENTRIES.items():
        repo.save_validity(ticker, dict(entry))

    assert repo.get_valid_tickers() == ["PETR4"]
    assert repo.get_invalid_tickers() == ["OSXB3"]


def test_is_ticker_valid_com_arquivo_ausente(paths):
    assert repo.is_ticker_valid("QUALQUER3") is True  # nunca validado


# ---------------------------------------------------------------------------
# stock_history.json — API específica
# ---------------------------------------------------------------------------

def test_history_nao_recria_quando_arquivo_valido(paths):
    _write(paths, "history", json.dumps({"stocks": {"XPTO3": {"price_min_6m": 1.5}}}))

    assert repo.get_history("XPTO3") == {"price_min_6m": 1.5}


def test_save_history_funciona_com_arquivo_ausente(paths):
    """Caso real do history_fetcher.py: primeiro acesso sem o JSON no disco."""
    repo.save_history("WEGE3", {"price_min_6m": 30.0, "price_max_6m": 55.0})

    with open(paths["history"], encoding="utf-8") as f:
        data = json.load(f)

    assert data["stocks"]["WEGE3"]["ticker"] == "WEGE3"
    assert data["stocks"]["WEGE3"]["last_updated"]
    assert data["_schema"] == repo.SKELETONS["history"]["_schema"]


def test_get_all_history_com_arquivo_ausente(paths):
    assert repo.get_all_history() == {}

    repo.save_history("WEGE3", {"price_min_6m": 30.0})
    assert list(repo.get_all_history()) == ["WEGE3"]


# ---------------------------------------------------------------------------
# stock_prices.json — API específica
# ---------------------------------------------------------------------------

def test_prices_nao_recria_quando_arquivo_valido(paths):
    _write(paths, "prices", json.dumps({"stocks": {"XPTO3": {"price_now": 9.9}}}))

    assert repo.get_price("XPTO3") == 9.9


def test_save_price_funciona_com_arquivo_ausente(paths):
    """Caso real do price_service.py: primeiro acesso sem o JSON no disco."""
    repo.save_price("WEGE3", 42.5)

    with open(paths["prices"], encoding="utf-8") as f:
        data = json.load(f)

    assert data["stocks"]["WEGE3"]["price_now"] == 42.5
    assert data["stocks"]["WEGE3"]["source"] == "google_finance"
    assert data["_schema"] == repo.SKELETONS["prices"]["_schema"]


def test_save_prices_batch_com_arquivo_ausente(paths):
    repo.save_prices_batch({"WEGE3": 42.5, "BBAS3": 21.0, "RUIM3": None, "ZERO3": 0})

    assert sorted(repo.get_all_prices()) == ["BBAS3", "WEGE3"]  # None e 0 descartados
    assert repo.get_price("BBAS3") == 21.0


def test_get_all_prices_com_arquivo_ausente(paths):
    assert repo.get_all_prices() == {}


# ---------------------------------------------------------------------------
# financials_history.json — API específica
# ---------------------------------------------------------------------------

def test_financials_nao_recria_quando_arquivo_valido(paths):
    _write(paths, "financials_history",
           json.dumps({"stocks": {"XPTO3": {"dre": {"receita_liquida": {"2025": 1.0}}}}}))

    assert repo.get_financials("XPTO3") == {"dre": {"receita_liquida": {"2025": 1.0}}}


def test_save_financials_funciona_com_arquivo_ausente(paths):
    """Caso real do financials_fetcher.py: primeiro acesso sem o JSON no disco."""
    repo.save_financials("WEGE3", {"dre": {}, "balanco": {}, "fluxo_caixa": {}})

    with open(paths["financials_history"], encoding="utf-8") as f:
        data = json.load(f)

    assert data["stocks"]["WEGE3"]["ticker"] == "WEGE3"
    assert data["stocks"]["WEGE3"]["last_updated"]
    assert data["_description"] == repo.SKELETONS["financials_history"]["_description"]


def test_financials_recriado_nao_tem_schema(paths):
    """financials_history.json nunca teve _schema — o esqueleto respeita isso."""
    repo.get_financials("PETR4")

    with open(paths["financials_history"], encoding="utf-8") as f:
        data = json.load(f)

    assert sorted(data.keys()) == ["_description", "last_updated", "stocks"]


def test_get_all_financials_com_arquivo_ausente(paths):
    assert repo.get_all_financials() == {}

    repo.save_financials("WEGE3", {"dre": {}})
    assert list(repo.get_all_financials()) == ["WEGE3"]


# ---------------------------------------------------------------------------
# valuations.json — API específica
# ---------------------------------------------------------------------------

def test_valuations_nao_recria_quando_arquivo_valido(paths):
    _write(paths, "valuations", json.dumps({"stocks": {"XPTO3": {"rank": 18}}}))

    assert repo.get_valuation("XPTO3") == {"rank": 18}


def test_save_valuation_funciona_com_arquivo_ausente(paths):
    """Caso real do valuation_calculator.py: primeiro acesso sem o JSON no disco."""
    repo.save_valuation("WEGE3", {"rank": 15, "zone": "COMPRA"})

    with open(paths["valuations"], encoding="utf-8") as f:
        data = json.load(f)

    assert data["stocks"]["WEGE3"]["ticker"] == "WEGE3"
    assert data["stocks"]["WEGE3"]["last_updated"]
    assert data["_schema"] == repo.SKELETONS["valuations"]["_schema"]


def test_get_all_valuations_com_arquivo_ausente(paths):
    assert repo.get_all_valuations() == {}

    repo.save_valuation("WEGE3", {"rank": 15})
    assert list(repo.get_all_valuations()) == ["WEGE3"]


def test_get_ranked_valuations_com_arquivo_ausente(paths):
    assert repo.get_ranked_valuations() == []
