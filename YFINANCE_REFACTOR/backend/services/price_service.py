"""
PriceService — classe responsável por:
  1. Buscar o preço atual de um ticker no Google Finance (scraping)
  2. Ler o último preço salvo do JSON (stock_prices.json)
  3. Fazer update: buscar + persistir no JSON
"""

import os
import re
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

import httpx

# Permite importar config/ e repositories/ quando executado diretamente
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.rules import PRICE_UPDATE_INTERVAL_HOURS
from repositories import stock_repository as repo

GOOGLE_FINANCE_URL = "https://www.google.com/finance/quote/{ticker}:BVMF"

_HEADERS = {
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

# Regex para capturar preço BR: aceita tanto ponto quanto vírgula decimal
_PRICE_PATTERN = re.compile(r'[\d]+[.,][\d]+')


class PriceService:
    """
    Serviço de preços de ações.

    Responsabilidades:
      - fetch_from_google(ticker)  → busca preço ao vivo no Google Finance
      - get_from_json(ticker)      → lê o último preço salvo localmente
      - update(ticker, force)      → busca ao vivo e persiste no JSON
      - update_all(tickers, force) → atualiza lote de tickers

    Dependências injetadas (facilitam testes):
      - repository  : objeto com interface de stock_repository (get_price, save_price...)
      - http_client : factory que retorna um httpx.Client (permite mock nos testes)
    """

    def __init__(self, repository=None, http_client_factory=None):
        self._repo = repository or repo
        self._http_client_factory = http_client_factory or self._default_http_client

    # ------------------------------------------------------------------
    # Dependência padrão de HTTP
    # ------------------------------------------------------------------

    @staticmethod
    def _default_http_client() -> httpx.Client:
        timeout = httpx.Timeout(5.0, read=10.0)
        return httpx.Client(
            headers=_HEADERS,
            timeout=timeout,
            follow_redirects=True,
            http2=True,
        )

    # ------------------------------------------------------------------
    # Leitura ao vivo — Google Finance
    # ------------------------------------------------------------------

    def fetch_from_google(self, ticker: str) -> Optional[float]:
        """
        Busca o preço atual de um ticker diretamente no Google Finance.

        Retorna o preço como float ou None em caso de:
          - HTTP != 200
          - Bloco de preço não encontrado no HTML
          - Qualquer exceção de rede/timeout
        """
        url = GOOGLE_FINANCE_URL.format(ticker=ticker.upper())
        try:
            with self._http_client_factory() as client:
                response = client.get(url)

            if response.status_code != 200:
                return None

            # O preço fica logo após o marcador de classe CSS "YMlKec fxKbKc"
            parts = response.text.split("YMlKec fxKbKc")
            if len(parts) < 2:
                return None

            price_block = parts[1][:100]
            match = _PRICE_PATTERN.search(price_block)
            if not match:
                return None

            price_str = match.group(0).replace(",", ".")
            return float(price_str)

        except Exception:
            return None

    # ------------------------------------------------------------------
    # Leitura local — JSON
    # ------------------------------------------------------------------

    def get_from_json(self, ticker: str) -> Optional[float]:
        """
        Retorna o último preço válido salvo localmente para o ticker.
        Retorna None se nunca foi salvo.
        """
        return self._repo.get_price(ticker)

    def get_entry_from_json(self, ticker: str) -> Optional[dict]:
        """
        Retorna a entrada completa (ticker, price_now, last_updated, source)
        do stock_prices.json para o ticker. Útil para inspecionar metadados.
        """
        all_prices = self._repo.get_all_prices()
        return all_prices.get(ticker.upper())

    # ------------------------------------------------------------------
    # Verificação de necessidade de update
    # ------------------------------------------------------------------

    def needs_update(self, ticker: str) -> bool:
        """
        Retorna True se o preço precisa ser atualizado:
          - nunca foi salvo, ou
          - a última atualização foi há mais de PRICE_UPDATE_INTERVAL_HOURS horas
        """
        entry = self.get_entry_from_json(ticker)
        if not entry:
            return True
        last_updated_str = entry.get("last_updated")
        if not last_updated_str:
            return True
        last_updated = datetime.fromisoformat(last_updated_str)
        return datetime.now() - last_updated > timedelta(hours=PRICE_UPDATE_INTERVAL_HOURS)

    # ------------------------------------------------------------------
    # Update: busca + persiste
    # ------------------------------------------------------------------

    def update(self, ticker: str, force: bool = False) -> Optional[float]:
        """
        Busca o preço ao vivo e persiste no JSON.

        Se force=False e o preço ainda está dentro do intervalo mínimo,
        retorna o preço já salvo sem fazer nova requisição.

        Retorna o preço (novo ou cacheado) ou None em caso de falha.
        """
        ticker = ticker.upper()
        if not self._repo.is_ticker_valid(ticker):
            return None
        if not force and not self.needs_update(ticker):
            return self.get_from_json(ticker)

        price = self.fetch_from_google(ticker)
        if price is not None and price > 0:
            self._repo.save_price(ticker, price)
            return price

        return None

    def update_all(
        self,
        tickers: Optional[list] = None,
        force: bool = False,
        delay: float = 0.3,
    ) -> dict:
        """
        Atualiza preços de uma lista de tickers (ou todos os válidos).

        delay: segundos de pausa entre requisições (evita bloqueio do Google).
        Retorna dict {ticker: price_or_None}.
        """
        if tickers is None:
            tickers = self._repo.get_valid_tickers()
            if not tickers:
                tickers = self._repo.get_tickers_list()

        results = {}
        total = len(tickers)

        for i, ticker in enumerate(tickers, 1):
            price = self.update(ticker, force=force)
            results[ticker] = price
            status = f"R${price:.2f}" if price else "FALHA"
            print(f"[{i:4d}/{total}] {ticker:<12} {status}")
            if delay > 0:
                time.sleep(delay)

        success = sum(1 for v in results.values() if v is not None)
        print(f"\nConcluído: {success}/{total} preços atualizados.")
        return results


if __name__ == "__main__":
    import sys
    svc = PriceService()
    args = sys.argv[1:]
    if args:
        svc.update_all(tickers=[t.upper() for t in args], force=True)
    else:
        svc.update_all()
