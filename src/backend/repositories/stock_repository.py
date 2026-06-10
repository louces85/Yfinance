"""
Repositório central de acesso aos dados JSON.
Todos os serviços leem e escrevem exclusivamente por aqui.
"""

import json
import os
import tempfile
from datetime import datetime
from typing import List, Optional

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


# ---------------------------------------------------------------------------
# Stocks list
# ---------------------------------------------------------------------------

def get_tickers_list() -> List[str]:
    """Retorna a lista de todos os tickers cadastrados."""
    data = _load(PATHS["stocks_list"])
    return data.get("tickers", [])


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
# stock_prices.json
# ---------------------------------------------------------------------------

def get_price(ticker: str) -> Optional[float]:
    """Retorna o último preço válido do ticker, ou None se não existir."""
    data = _load(PATHS["prices"])
    entry = data.get("stocks", {}).get(ticker.upper())
    if entry:
        return entry.get("price_now")
    return None


def save_price(ticker: str, price: float) -> None:
    """Grava/atualiza o preço atual de um ticker."""
    data = _load(PATHS["prices"])
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
    data = _load(PATHS["prices"])
    return data.get("stocks", {})


def save_prices_batch(updates: dict) -> None:
    """Grava múltiplos preços de uma vez — uma única leitura+escrita no JSON."""
    data = _load(PATHS["prices"])
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
    data = _load(PATHS["history"])
    return data.get("stocks", {}).get(ticker.upper())


def save_history(ticker: str, entry: dict) -> None:
    """
    Grava/atualiza a entrada de histórico de um ticker.
    entry deve conter os campos definidos no schema de stock_history.json.
    """
    data = _load(PATHS["history"])
    if "stocks" not in data:
        data["stocks"] = {}
    entry["ticker"]       = ticker.upper()
    entry["last_updated"] = _now()
    data["stocks"][ticker.upper()] = entry
    data["last_updated"] = _now()
    _save(PATHS["history"], data)


def get_all_history() -> dict:
    data = _load(PATHS["history"])
    return data.get("stocks", {})


# ---------------------------------------------------------------------------
# valuations.json
# ---------------------------------------------------------------------------

def get_valuation(ticker: str) -> Optional[dict]:
    """Retorna o valuation calculado de um ticker."""
    data = _load(PATHS["valuations"])
    return data.get("stocks", {}).get(ticker.upper())


def save_valuation(ticker: str, entry: dict) -> None:
    """Grava/atualiza o valuation de um ticker."""
    data = _load(PATHS["valuations"])
    if "stocks" not in data:
        data["stocks"] = {}
    entry["ticker"]       = ticker.upper()
    entry["last_updated"] = _now()
    data["stocks"][ticker.upper()] = entry
    data["last_updated"] = _now()
    _save(PATHS["valuations"], data)


def get_all_valuations() -> dict:
    data = _load(PATHS["valuations"])
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
    data = _load(PATHS["validity"])
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
    data = _load(PATHS["validity"])
    if "stocks" not in data:
        data["stocks"] = {}
    entry["ticker"]     = ticker.upper()
    entry["last_check"] = _now()
    data["stocks"][ticker.upper()] = entry
    data["last_updated"] = _now()
    _save(PATHS["validity"], data)


def get_valid_tickers() -> List[str]:
    """Retorna apenas os tickers marcados como válidos."""
    data = _load(PATHS["validity"])
    return [
        ticker
        for ticker, entry in data.get("stocks", {}).items()
        if entry.get("is_valid", True)
    ]


def get_invalid_tickers() -> List[str]:
    """Retorna os tickers marcados como inválidos."""
    data = _load(PATHS["validity"])
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
    try:
        data = _load(PATHS["financials_history"])
        return data.get("stocks", {}).get(ticker.upper())
    except FileNotFoundError:
        return None


def save_financials(ticker: str, entry: dict) -> None:
    """
    Grava/atualiza os demonstrativos históricos de um ticker.
    entry deve conter as seções 'dre', 'balanco', 'fluxo_caixa'.
    """
    try:
        data = _load(PATHS["financials_history"])
    except FileNotFoundError:
        data = {
            "_description": (
                "Demonstrativos financeiros históricos por ticker: "
                "DRE + Balanço (StatusInvest, até 10 anos), "
                "Fluxo de Caixa (yfinance, até 4 anos). "
                "Atualizado via financials_fetcher.py."
            ),
            "stocks": {},
        }
    entry["ticker"]       = ticker.upper()
    entry["last_updated"] = _now()
    data.setdefault("stocks", {})[ticker.upper()] = entry
    data["last_updated"] = _now()
    _save(PATHS["financials_history"], data)


def get_all_financials() -> dict:
    """Retorna o mapa completo ticker -> entry de demonstrativos históricos."""
    try:
        return _load(PATHS["financials_history"]).get("stocks", {})
    except FileNotFoundError:
        return {}


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
