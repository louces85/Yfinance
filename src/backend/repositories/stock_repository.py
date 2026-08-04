"""
Repositório central de acesso aos dados JSON.
Todos os serviços leem e escrevem exclusivamente por aqui.
"""

import copy
import json
import os
import sys
import tempfile
from datetime import datetime
from typing import List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import rules

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "data")

PATHS = {
    "indicators":         os.path.join(DATA_DIR, "all_indicators.json"),
    "stocks_list":        os.path.join(DATA_DIR, "stocks_list.json"),
    "history":            os.path.join(DATA_DIR, "stock_history.json"),
    "prices":             os.path.join(DATA_DIR, "stock_prices.json"),
    "valuations":         os.path.join(DATA_DIR, "valuations.json"),
    "validity":           os.path.join(DATA_DIR, "stock_validity.json"),
    "monitoring_stocks":  os.path.join(DATA_DIR, "monitoring_stocks.json"),
    "financials_history": os.path.join(DATA_DIR, "financials_history.json"),
    "swing":              os.path.join(DATA_DIR, "swing_data.json"),
    "swing_positions":    os.path.join(DATA_DIR, "swing_positions.json"),
    "stocks_seed":        os.path.join(DATA_DIR, "seed_stocks", "stocks_file_2026"),
}

# Metadados gravados ao recriar stocks_list.json a partir da semente
SEED_DESCRIPTION = "Lista de tickers B3 para análise (2026)"
SEED_SOURCE      = "data/seed_stocks/stocks_file_2026"

# Estrutura mínima dos JSONs indexados por ticker. Quando um desses arquivos
# some ou é corrompido, ele é recriado vazio a partir daqui — o conteúdo é
# repopulado pelo fetcher correspondente.
SKELETONS = {
    "validity": {
        "_description": (
            "Status de validade de cada ticker. Um ticker é inválido quando o yfinance ou "
            "Google Finance não conseguem mais dados consistentes (delisting, troca de ticker, "
            "suspensão). Atualizado via stock_validator.py."
        ),
        "_schema": {
            "last_updated": "ISO8601 datetime da última validação geral",
            "stocks": {
                "<TICKER>": {
                    "ticker":               "string",
                    "is_valid":             "bool - true se o ticker está ativo e com dados disponíveis",
                    "last_check":           "ISO8601 datetime da última verificação",
                    "last_valid":           "ISO8601 datetime da última vez que foi válido",
                    "check_count":          "int - total de verificações realizadas",
                    "consecutive_failures": "int - falhas consecutivas atuais (>= 3 = inválido)",
                    "validation_source":    "string - fonte usada para validar (yfinance | google_finance)",
                    "reason_invalid":       ("string | null - motivo da invalidação se is_valid=false "
                                             "(ex: 'no_data', 'delisted', 'no_price_6_months')"),
                }
            },
        },
    },
    "history": {
        "_description": (
            "Histórico de preços (mín/máx 6 meses) e dividendos (4 anos) por ticker. "
            "Atualizado semanalmente via history_fetcher.py."
        ),
        "_schema": {
            "last_updated": "ISO8601 datetime da última atualização geral",
            "stocks": {},
        },
    },
    "prices": {
        "_description": (
            "Último preço válido de cada ticker lido do Google Finance. "
            "Atualizado diariamente via price_service.py."
        ),
        "_schema": {
            "last_updated": "ISO8601 datetime da última atualização geral",
            "stocks": {
                "<TICKER>": {
                    "ticker":       "string - código do ticker (ex: BBAS3)",
                    "price_now":    "float - último preço válido lido",
                    "last_updated": "ISO8601 datetime da última leitura bem-sucedida",
                    "source":       "string - fonte do preço (google_finance)",
                }
            },
        },
    },
    "financials_history": {
        "_description": (
            "Demonstrativos financeiros históricos por ticker: "
            "DRE + Balanço (StatusInvest, até 10 anos), "
            "Fluxo de Caixa (yfinance, até 4 anos). "
            "Atualizado via financials_fetcher.py."
        ),
    },
    "valuations": {
        "_description": (
            "Valuation calculado por ticker: preço-alvo, ranking, zonas Barsi, "
            "flags de critérios. Atualizado via valuation_calculator.py."
        ),
        "_schema": {
            "last_updated": "ISO8601 datetime da última atualização geral",
            "stocks": {},
        },
    },
}


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save(path: str, data: dict) -> None:
    """Escrita atômica: grava em arquivo temporário e substitui com os.replace.
    Garante que leitores concorrentes nunca vejam JSON incompleto/corrompido."""
    dir_name = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)  # atômico no Linux — sem janela de arquivo vazio
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _now() -> str:
    return datetime.now().isoformat()


def _load_or_none(path: str) -> Optional[dict]:
    """Carrega um JSON e devolve o dict, ou None se o arquivo estiver ausente,
    ilegível, vazio ou com conteúdo inválido."""
    try:
        data = _load(path)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _ensure_dir(path: str) -> None:
    """Garante que o diretório do arquivo existe (necessário para o write atômico)."""
    dir_name = os.path.dirname(path)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)


def rebuild_ticker_file(key: str) -> dict:
    """(Re)cria vazio um dos JSONs indexados por ticker (ver SKELETONS),
    mantendo apenas os metadados de estrutura. Retorna o dict gravado."""
    data = copy.deepcopy(SKELETONS[key])
    data["stocks"]       = {}
    data["last_updated"] = _now()

    _ensure_dir(PATHS[key])
    _save(PATHS[key], data)
    return data


def _load_ticker_file(key: str) -> dict:
    """Lê um dos JSONs indexados por ticker, recriando-o vazio quando estiver
    ausente, vazio (0 bytes), corrompido ou sem a estrutura esperada.
    Um arquivo íntegro ainda sem tickers é preservado — o fetcher o preenche
    à medida que processa cada ticker."""
    data = _load_or_none(PATHS[key])
    if data is None or not isinstance(data.get("stocks"), dict):
        data = rebuild_ticker_file(key)
    return data


# ---------------------------------------------------------------------------
# Stocks list
# ---------------------------------------------------------------------------

def _read_seed_tickers() -> List[str]:
    """Lê os tickers do arquivo semente (um por linha), normaliza para maiúsculas
    e remove duplicatas, linhas vazias e comentários (#)."""
    with open(PATHS["stocks_seed"], encoding="utf-8") as f:
        lines = [line.strip().upper() for line in f]

    seen = set()
    tickers = []
    for ticker in lines:
        if not ticker or ticker.startswith("#") or ticker in seen:
            continue
        seen.add(ticker)
        tickers.append(ticker)
    return sorted(tickers)


def rebuild_stocks_list() -> dict:
    """Recria stocks_list.json a partir da semente, no mesmo formato do template
    (description / source / last_updated / count / tickers). Retorna o dict gravado."""
    seed_path = PATHS["stocks_seed"]
    if not os.path.exists(seed_path):
        raise FileNotFoundError(
            "stocks_list.json ausente ou vazio e semente não encontrada em " + seed_path
        )

    tickers = _read_seed_tickers()
    data = {
        "description":  SEED_DESCRIPTION,
        "source":       SEED_SOURCE,
        "last_updated": _now(),
        "count":        len(tickers),
        "tickers":      tickers,
    }

    _ensure_dir(PATHS["stocks_list"])
    _save(PATHS["stocks_list"], data)
    return data


def get_tickers_list() -> List[str]:
    """Retorna a lista de todos os tickers cadastrados.

    Se stocks_list.json não existir, estiver vazio/corrompido ou sem tickers,
    o arquivo é recriado automaticamente a partir de
    data/seed_stocks/stocks_file_2026."""
    data = _load_or_none(PATHS["stocks_list"])
    tickers = data.get("tickers") if data else None
    if not tickers:
        tickers = rebuild_stocks_list()["tickers"]
    return tickers


# ---------------------------------------------------------------------------
# all_indicators.json (somente leitura — fonte externa do StatusInvest)
# ---------------------------------------------------------------------------

def get_all_indicators() -> List[dict]:
    """Retorna todos os registros de indicadores fundamentalistas."""
    return _load(PATHS["indicators"])


def get_indicators_by_ticker(ticker: str) -> Optional[dict]:
    """Retorna o dicionário de indicadores de um ticker específico."""
    for item in get_all_indicators():
        if item.get("ticker", "").upper() == ticker.upper():
            return item
    return None


# ---------------------------------------------------------------------------
# Classificação setorial — derivada do all_indicators.json
# ---------------------------------------------------------------------------

def _fix_sector_name(name: Optional[str]) -> str:
    """Normaliza o nome vindo do export do StatusInvest (ver rules.SECTOR_NAME_FIXES)."""
    if not name:
        return ""
    return rules.SECTOR_NAME_FIXES.get(name, name)


def _sector_from_indicator(item: dict) -> dict:
    """Extrai {setor, subsetor, segmento} de um registro do all_indicators.json."""
    return {
        "setor":    _fix_sector_name(item.get("sectorname")),
        "subsetor": _fix_sector_name(item.get("subsectorname")),
        "segmento": _fix_sector_name(item.get("segmentname")),
    }


def get_all_sectors() -> dict:
    """Retorna o mapa ticker -> {setor, subsetor, segmento} de todos os tickers.

    A classificação vem do próprio all_indicators.json (export do StatusInvest),
    então a cobertura é total por construção: um ticker sem registro de
    indicadores é descartado pelo valuation antes de chegar ao ranking."""
    sectors = {}
    for item in get_all_indicators():
        ticker = (item.get("ticker") or "").upper()
        if ticker:
            sectors[ticker] = _sector_from_indicator(item)
    return sectors


def get_sector(ticker: str) -> dict:
    """Retorna {setor, subsetor, segmento} de um ticker, ou {} se não houver registro."""
    item = get_indicators_by_ticker(ticker)
    return _sector_from_indicator(item) if item else {}


# ---------------------------------------------------------------------------
# stock_prices.json
# ---------------------------------------------------------------------------

def get_price(ticker: str) -> Optional[float]:
    """Retorna o último preço válido do ticker, ou None se não existir."""
    data = _load_ticker_file("prices")
    entry = data.get("stocks", {}).get(ticker.upper())
    if entry:
        return entry.get("price_now")
    return None


def save_price(ticker: str, price: float) -> None:
    """Grava/atualiza o preço atual de um ticker."""
    data = _load_ticker_file("prices")
    if "stocks" not in data:
        data["stocks"] = {}
    data["stocks"][ticker.upper()] = {
        "ticker":       ticker.upper(),
        "price_now":    price,
        "last_updated": _now(),
        "source":       "google_finance",
    }
    data["last_updated"] = _now()
    _save(PATHS["prices"], data)


def get_all_prices() -> dict:
    """Retorna o mapa completo ticker -> entry de preços."""
    data = _load_ticker_file("prices")
    return data.get("stocks", {})


def save_prices_batch(updates: dict) -> None:
    """Grava múltiplos preços de uma vez — uma única leitura+escrita no JSON."""
    data = _load_ticker_file("prices")
    stocks = data.setdefault("stocks", {})
    now = _now()
    for ticker, price in updates.items():
        if price is not None and price > 0:
            stocks[ticker.upper()] = {
                "ticker":       ticker.upper(),
                "price_now":    price,
                "last_updated": now,
                "source":       "google_finance",
            }
    data["last_updated"] = now
    _save(PATHS["prices"], data)


# ---------------------------------------------------------------------------
# stock_history.json
# ---------------------------------------------------------------------------

def get_history(ticker: str) -> Optional[dict]:
    """Retorna a entrada de histórico (min/max 6m + dividendos) de um ticker."""
    data = _load_ticker_file("history")
    return data.get("stocks", {}).get(ticker.upper())


def save_history(ticker: str, entry: dict) -> None:
    """
    Grava/atualiza a entrada de histórico de um ticker.
    entry deve conter os campos definidos no schema de stock_history.json.
    """
    data = _load_ticker_file("history")
    if "stocks" not in data:
        data["stocks"] = {}
    entry["ticker"]       = ticker.upper()
    entry["last_updated"] = _now()
    data["stocks"][ticker.upper()] = entry
    data["last_updated"] = _now()
    _save(PATHS["history"], data)


def get_all_history() -> dict:
    data = _load_ticker_file("history")
    return data.get("stocks", {})


# ---------------------------------------------------------------------------
# valuations.json
# ---------------------------------------------------------------------------

def get_valuation(ticker: str) -> Optional[dict]:
    """Retorna o valuation calculado de um ticker."""
    data = _load_ticker_file("valuations")
    return data.get("stocks", {}).get(ticker.upper())


def save_valuation(ticker: str, entry: dict) -> None:
    """Grava/atualiza o valuation de um ticker."""
    data = _load_ticker_file("valuations")
    if "stocks" not in data:
        data["stocks"] = {}
    entry["ticker"]       = ticker.upper()
    entry["last_updated"] = _now()
    data["stocks"][ticker.upper()] = entry
    data["last_updated"] = _now()
    _save(PATHS["valuations"], data)


def get_all_valuations() -> dict:
    data = _load_ticker_file("valuations")
    return data.get("stocks", {})


def get_ranked_valuations(min_rank: int = 0) -> List[dict]:
    """
    Retorna todos os valuations com rank >= min_rank,
    ordenados por rank DESC e p_now_p_min ASC.
    """
    stocks = list(get_all_valuations().values())
    filtered = [s for s in stocks if s.get("rank", 0) >= min_rank]
    filtered.sort(key=lambda s: (-s.get("rank", 0), s.get("p_now_p_min", 9999)))
    return filtered


# ---------------------------------------------------------------------------
# stock_validity.json
# ---------------------------------------------------------------------------

def get_validity(ticker: str) -> Optional[dict]:
    """Retorna o status de validade de um ticker."""
    data = _load_ticker_file("validity")
    return data.get("stocks", {}).get(ticker.upper())


def is_ticker_valid(ticker: str) -> bool:
    """
    Retorna True se o ticker está marcado como válido em stock_validity.json.
    Tickers sem entrada no JSON são tratados como válidos (ainda não validados).
    """
    entry = get_validity(ticker)
    if entry is None:
        return True  # nunca validado — deixa tentar
    return bool(entry.get("is_valid", True))


def save_validity(ticker: str, entry: dict) -> None:
    """Grava/atualiza o status de validade de um ticker."""
    data = _load_ticker_file("validity")
    if "stocks" not in data:
        data["stocks"] = {}
    entry["ticker"]     = ticker.upper()
    entry["last_check"] = _now()
    data["stocks"][ticker.upper()] = entry
    data["last_updated"] = _now()
    _save(PATHS["validity"], data)


def get_valid_tickers() -> List[str]:
    """Retorna apenas os tickers marcados como válidos."""
    data = _load_ticker_file("validity")
    return [
        ticker
        for ticker, entry in data.get("stocks", {}).items()
        if entry.get("is_valid", True)
    ]


def get_invalid_tickers() -> List[str]:
    """Retorna os tickers marcados como inválidos."""
    data = _load_ticker_file("validity")
    return [
        ticker
        for ticker, entry in data.get("stocks", {}).items()
        if not entry.get("is_valid", True)
    ]


# ---------------------------------------------------------------------------
# Monitoring stocks
# ---------------------------------------------------------------------------

def save_monitoring_stocks(entries: List[dict]) -> None:
    """
    Grava/substitui o monitoring_stocks.json com os tickers que passaram
    nos filtros de pré-qualificação do valuation_calculator.
    """
    data = {
        "last_updated": _now(),
        "total": len(entries),
        "stocks": entries,
    }
    _save(PATHS["monitoring_stocks"], data)


def get_monitoring_stocks() -> List[dict]:
    """Retorna a lista de stocks monitoradas."""
    try:
        data = _load(PATHS["monitoring_stocks"])
        return data.get("stocks", [])
    except FileNotFoundError:
        return []


# ---------------------------------------------------------------------------
# financials_history.json
# ---------------------------------------------------------------------------

def get_financials(ticker: str) -> Optional[dict]:
    """Retorna o bloco de demonstrativos históricos de um ticker, ou None."""
    data = _load_ticker_file("financials_history")
    return data.get("stocks", {}).get(ticker.upper())


def save_financials(ticker: str, entry: dict) -> None:
    """
    Grava/atualiza os demonstrativos históricos de um ticker.
    entry deve conter as seções 'dre', 'balanco', 'fluxo_caixa'.
    """
    data = _load_ticker_file("financials_history")
    entry["ticker"]       = ticker.upper()
    entry["last_updated"] = _now()
    data["stocks"][ticker.upper()] = entry
    data["last_updated"] = _now()
    _save(PATHS["financials_history"], data)


def get_all_financials() -> dict:
    """Retorna o mapa completo ticker -> entry de demonstrativos históricos."""
    return _load_ticker_file("financials_history").get("stocks", {})


# ---------------------------------------------------------------------------
# Swing data
# ---------------------------------------------------------------------------

def save_swing_data(entries):
    """Salva lista de dicts com indicadores técnicos de swing trade."""
    _save(PATHS["swing"], entries)


def load_swing_data():
    """Retorna lista de swing_data ou [] se o arquivo não existir."""
    path = PATHS["swing"]
    if not os.path.exists(path):
        return []
    return _load(path)


# ---------------------------------------------------------------------------
# Swing positions (diário de operações: compras/vendas manuais do usuário)
# ---------------------------------------------------------------------------

def save_swing_positions(positions):
    """Salva a lista de operações de swing (abertas e fechadas) — escrita atômica."""
    _save(PATHS["swing_positions"], positions)


def load_swing_positions():
    """Retorna a lista de operações de swing ou [] se o arquivo não existir."""
    path = PATHS["swing_positions"]
    if not os.path.exists(path):
        return []
    return _load(path)
