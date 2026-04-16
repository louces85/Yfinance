"""
Market service — busca índices de mercado via yfinance e salva em market_data.json.

Índices:
    IBOV  → ^BVSP    (Ibovespa — pontos)
    USD   → BRL=X    (Dólar / Real)
    SP500 → ^GSPC    (S&P 500)
    OURO  → GC=F     (Ouro — USD/oz)
"""

import json
import os
import tempfile
from datetime import datetime
from typing import Optional

import yfinance as yf

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_MARKET_PATH = os.path.join(_DATA_DIR, "market_data.json")

_SYMBOLS = {
    "IBOV":  "^BVSP",
    "USD":   "BRL=X",
    "SP500": "^GSPC",
    "OURO":  "GC=F",
}


def _fetch_one(symbol: str) -> dict:
    try:
        fi = yf.Ticker(symbol).fast_info
        price = fi.last_price
        prev  = fi.previous_close
        change_pct = round((price - prev) / prev * 100, 2) if prev else None
        return {"price": round(price, 2) if price else None, "change_pct": change_pct}
    except Exception:
        return {"price": None, "change_pct": None}


def fetch() -> dict:
    """Busca todos os índices e persiste em market_data.json. Retorna o dict salvo."""
    data = {name: _fetch_one(sym) for name, sym in _SYMBOLS.items()}
    payload = {"last_updated": datetime.now().isoformat(), "data": data}

    # Atomic write
    tmp = tempfile.NamedTemporaryFile("w", dir=_DATA_DIR, delete=False,
                                     suffix=".tmp", encoding="utf-8")
    try:
        json.dump(payload, tmp, ensure_ascii=False)
        tmp.close()
        os.replace(tmp.name, _MARKET_PATH)
    except Exception:
        tmp.close()
        try:
            os.unlink(tmp.name)
        except OSError:
            pass

    return payload


def load() -> Optional[dict]:
    """Carrega market_data.json do disco. Retorna None se não existir."""
    try:
        with open(_MARKET_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
