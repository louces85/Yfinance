"""
Serviço de coleta de preços atual via Google Finance (scraping).
Lê os preços e persiste em data/stock_prices.json via stock_repository.

Uso direto:
    python price_fetcher.py                  # atualiza todos os tickers válidos
    python price_fetcher.py BBAS3 PETR4      # atualiza tickers específicos
"""

import sys
import os
import re
import time
import httpx
from datetime import datetime, timedelta
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories import stock_repository as repo
from config.rules import PRICE_UPDATE_INTERVAL_HOURS

GOOGLE_FINANCE_URL = "https://www.google.com/finance/quote/{ticker}:BVMF"

HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    ),
    "accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "accept-language": "en-US,en;q=0.9",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "connection": "keep-alive",
}


def fetch_price(ticker: str) -> Optional[float]:
    """
    Busca o preço atual de um ticker no Google Finance.
    Retorna o preço como float ou None em caso de falha.
    """
    url = GOOGLE_FINANCE_URL.format(ticker=ticker.upper())
    try:
        timeout = httpx.Timeout(5.0, read=10.0)
        with httpx.Client(headers=HEADERS, timeout=timeout, follow_redirects=True, http2=True) as client:
            response = client.get(url)

        if response.status_code != 200:
            return None

        # Extrai o preço do bloco YMlKec fxKbKc
        parts = response.text.split("YMlKec fxKbKc")
        if len(parts) < 2:
            return None

        price_block = parts[1][:100]  # os próximos ~100 chars contêm o valor
        # Preços BR usam vírgula como decimal: "R$25,40" ou "25,40"
        match = re.search(r'[\d]+[.,][\d]+', price_block)
        if not match:
            return None

        price_str = match.group(0).replace(",", ".")
        return float(price_str)

    except Exception:
        return None


def _needs_update(ticker: str) -> bool:
    """Retorna True se o preço precisa ser atualizado (respeita intervalo mínimo)."""
    entry = repo.get_price(ticker)
    if entry is None:
        return True
    all_prices = repo.get_all_prices()
    last_entry = all_prices.get(ticker.upper(), {})
    last_updated_str = last_entry.get("last_updated")
    if not last_updated_str:
        return True
    last_updated = datetime.fromisoformat(last_updated_str)
    return datetime.now() - last_updated > timedelta(hours=PRICE_UPDATE_INTERVAL_HOURS)


def update_ticker(ticker: str, force: bool = False) -> Optional[float]:
    """
    Busca e persiste o preço de um ticker.
    Retorna o preço atualizado ou None se inválido / falhou.
    """
    if not repo.is_ticker_valid(ticker):
        return None
    if not force and not _needs_update(ticker):
        existing = repo.get_price(ticker)
        return existing

    price = fetch_price(ticker)
    if price is not None and price > 0:
        repo.save_price(ticker, price)
        return price

    return None


def update_all(tickers: Optional[list] = None, force: bool = False, delay: float = 0.3) -> dict:
    """
    Atualiza preços de uma lista de tickers (ou todos os válidos se None).
    delay: pausa em segundos entre requisições para não sobrecarregar o Google.
    Retorna dict com resultados: {ticker: price_or_None}.
    """
    if tickers is None:
        tickers = repo.get_valid_tickers()
        if not tickers:
            # fallback: usa lista completa se ainda não há validações
            tickers = repo.get_tickers_list()

    results = {}
    total = len(tickers)
    for i, ticker in enumerate(tickers, 1):
        price = update_ticker(ticker, force=force)
        results[ticker] = price
        status = f"R${price:.2f}" if price else "FALHA"
        print(f"[{i:4d}/{total}] {ticker:<12} {status}")
        if delay > 0:
            time.sleep(delay)

    success = sum(1 for v in results.values() if v is not None)
    print(f"\nConcluído: {success}/{total} preços atualizados.")
    return results


if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        tickers_arg = [t.upper() for t in args]
        update_all(tickers=tickers_arg, force=True)
    else:
        update_all()
