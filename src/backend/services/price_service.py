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
import yfinance

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

# Regex para extrair preço no formato novo do Google Finance beta (ex: "R$47.52" ou "47,52")
_PRICE_BRL_PATTERN = re.compile(r'R\$?([\d]{1,3}(?:[,.][\d]{3})*(?:[.,][\d]{1,2}))')


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

    def fetch_from_google(self, ticker: str, retries: int = 3, retry_delay: float = 1.0) -> Optional[float]:
        """
        Busca o preço atual de um ticker diretamente no Google Finance.
        Em caso de falha, tenta novamente até `retries` vezes com pausa de `retry_delay` segundos.

        Retorna o preço como float ou None se todas as tentativas falharem.
        """
        url = GOOGLE_FINANCE_URL.format(ticker=ticker.upper())
        last_error = ""
        for attempt in range(1, retries + 1):
            try:
                with self._http_client_factory() as client:
                    response = client.get(url)

                if response.status_code != 200:
                    raise ValueError(f"HTTP {response.status_code}")

                text = response.text

                # Google Finance beta: preço em class="N6SYTe" > span[jsname="Pdsbrc"] > span > R$XX.XX
                parts_beta = text.split('class="N6SYTe"')
                if len(parts_beta) >= 2:
                    price_block = parts_beta[1][:200]
                    match = _PRICE_BRL_PATTERN.search(price_block)
                    if match:
                        raw = match.group(1)
                        # Normaliza: remove separador de milhar, troca vírgula decimal por ponto
                        if raw.count(',') == 1 and raw.count('.') == 0:
                            raw = raw.replace(',', '.')
                        else:
                            raw = raw.replace(',', '')
                        return float(raw)

                # Google Finance clássico (legado): preço após "YMlKec fxKbKc"
                parts_classic = text.split("YMlKec fxKbKc")
                if len(parts_classic) >= 2:
                    price_block = parts_classic[1][:100]
                    match = _PRICE_PATTERN.search(price_block)
                    if match:
                        price_str = match.group(0).replace(",", ".")
                        return float(price_str)

                raise ValueError("price block not found")

            except Exception as e:
                last_error = str(e)
                if attempt < retries:
                    print(f"          [{ticker}] tentativa {attempt}/{retries} falhou ({last_error}) — aguardando {retry_delay}s")
                    time.sleep(retry_delay)

        print(f"          [{ticker}] todas as {retries} tentativas falharam ({last_error})")
        return None

    def fetch_from_yfinance(self, ticker: str) -> Optional[float]:
        """
        Busca o preço atual via yfinance (TICKER.SA) como fallback do Google Finance.
        Usa o último fechamento disponível no histórico de 5 dias.
        """
        try:
            yf_ticker = yfinance.Ticker(f"{ticker.upper()}.SA")
            hist = yf_ticker.history(period="5d")
            if hist.empty:
                return None
            close_series = hist["Close"].dropna()
            close_series = close_series[close_series > 0]
            if close_series.empty:
                return None
            return float(close_series.iloc[-1])
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

        # Google falhou — tenta yfinance
        print(f"          [{ticker}] tentando yfinance como fallback")
        price = self.fetch_from_yfinance(ticker)
        if price is not None and price > 0:
            print(f"          [{ticker}] yfinance OK: R${price:.2f}")
            self._repo.save_price(ticker, price)
            return price

        # yfinance também falhou — usa preço cacheado
        cached = self.get_from_json(ticker)
        if cached is not None and cached > 0:
            print(f"          [{ticker}] usando preço cacheado R${cached:.2f}")
        return cached

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
