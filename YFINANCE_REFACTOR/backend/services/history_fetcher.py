"""
Serviço de coleta de histórico via yfinance + StatusInvest.
Persiste em data/stock_history.json via stock_repository.

Para cada ticker válido (conforme stock_validity.json) busca:
  - Preço mínimo e máximo dos últimos 6 meses          (yfinance)
  - Dividendos pagos por ano nos últimos 5 anos         (yfinance)
  - Flag se pagou dividendos em TODOS os 5 últimos anos (yfinance)
  - Média de dividendos anuais (base para price_target) (yfinance)
  - Lucro líquido por ano nos últimos 5 anos            (yfinance)
  - Flag se teve lucro positivo em TODOS os 5 anos      (yfinance)
  - Payout ratio mais recente                           (StatusInvest)

A execução respeita HISTORY_UPDATE_INTERVAL_DAYS — rode quando quiser
que o intervalo controla o que realmente precisa ser atualizado.

Uso direto:
    python history_fetcher.py                  # atualiza tickers válidos (respeita intervalo)
    python history_fetcher.py BBAS3 PETR4      # tickers específicos (respeita intervalo)
    python history_fetcher.py --force          # força reprocessamento de todos os válidos
    python history_fetcher.py BBAS3 --force    # força ticker específico
"""

import math
import sys
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx
import yfinance

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories import stock_repository as repo
from config.rules import HISTORY_UPDATE_INTERVAL_DAYS, DIVIDEND_YEARS_MIN
from services.buffett_fetcher import fetch_cashflow, fetch_trends

_STATUSINVEST_PAYOUT_URL = "https://statusinvest.com.br/acao/payoutresult?code={ticker}"
_STATUSINVEST_HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/134.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "referer": "https://statusinvest.com.br/",
}


def _needs_update(ticker: str) -> bool:
    entry = repo.get_history(ticker)
    if entry is None:
        return True
    last_updated_str = entry.get("last_updated")
    if not last_updated_str:
        return True
    last_updated = datetime.fromisoformat(last_updated_str)
    return datetime.now() - last_updated > timedelta(days=HISTORY_UPDATE_INTERVAL_DAYS)


def fetch_payout(ticker: str) -> Optional[float]:
    """
    Busca o payout ratio mais recente do StatusInvest.
    Equivalente ao get_payout() do sistema antigo, mas usando httpx ao invés de curl.

    O endpoint retorna uma lista de objetos; o campo 'actual' do primeiro
    item é o payout do período mais recente.

    Retorna o payout como float (ex: 65.4) ou None em caso de falha.
    """
    url = _STATUSINVEST_PAYOUT_URL.format(ticker=ticker.lower())
    try:
        timeout = httpx.Timeout(5.0, read=10.0)
        with httpx.Client(headers=_STATUSINVEST_HEADERS, timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)

        if response.status_code != 200:
            return None

        data = response.json()
        if not data or not isinstance(data, dict):
            return None

        # O campo "actual" é o payout do período mais recente
        actual = data.get("actual")

        if actual is None:
            return None

        value = float(actual)
        return round(value, 2) if value > 0 else None

    except Exception:
        return None


def fetch_history(ticker: str) -> Optional[dict]:
    """
    Busca histórico completo de um ticker:
      - min/max de preço nos últimos 6 meses       (yfinance)
      - dividendos por ano nos últimos 5 anos       (yfinance)
      - lucro líquido por ano nos últimos 5 anos    (yfinance)
      - payout ratio mais recente                   (StatusInvest)

    Retorna dict com os dados ou None se dados de preço indisponíveis.
    """
    yf_ticker_str = f"{ticker.upper()}.SA"
    current_year = datetime.now().year
    target_years = [str(current_year - i) for i in range(1, DIVIDEND_YEARS_MIN + 1)]

    try:
        yf_ticker = yfinance.Ticker(yf_ticker_str)

        # --- Preço: min/max 6 meses ---
        hist_price = yf_ticker.history(period="6mo")
        if hist_price.empty:
            return None

        low_series  = hist_price["Low"].dropna()
        high_series = hist_price["High"].dropna()
        low_series  = low_series[low_series > 0]
        high_series = high_series[high_series > 0]

        if low_series.empty or high_series.empty:
            return None

        price_max_6m = float(high_series.max())
        if math.isnan(price_max_6m) or price_max_6m <= 0:
            return None

        # Remove outliers: yfinance insere valores ínfimos em dias sem negociação
        # Descarta tudo abaixo de 5% do máximo
        threshold = price_max_6m * 0.05
        low_series = low_series[low_series >= threshold]
        if low_series.empty:
            return None

        price_min_6m = float(low_series.min())
        if math.isnan(price_min_6m):
            return None

        # --- Score de acumulação silenciosa (Barsi) ---
        # % de dias em que preço de fechamento E volume estão ambos abaixo da
        # respectiva média dos 6 meses — sinal de compra discreta/institucional.
        close_avg  = float(hist_price["Close"].mean())
        volume_col = hist_price["Volume"] if "Volume" in hist_price.columns else None
        if volume_col is not None and not volume_col.empty:
            # Filtra dias com volume == 0 (bug Yahoo Finance pós-pregão)
            vol_nonzero = volume_col[volume_col > 0]
            volume_avg = float(vol_nonzero.mean()) if not vol_nonzero.empty else 0.0
            if volume_avg > 0:
                cond = (hist_price["Close"] < close_avg) & (volume_col < volume_avg)
                accumulation_score = round(float(cond.sum()) / len(hist_price) * 100, 1)
            else:
                accumulation_score = None
        else:
            volume_avg = 0.0
            accumulation_score = None

        # --- Dividendos: últimos 5 anos ---
        dividends = yf_ticker.dividends
        dividends_per_year: Dict[str, float] = {}
        years_with_dividends = 0

        for year in target_years:
            year_divs = dividends[dividends.index.year == int(year)].dropna()
            year_divs = year_divs[year_divs > 0]
            year_total = float(year_divs.sum()) if not year_divs.empty else 0.0
            if math.isnan(year_total):
                year_total = 0.0
            dividends_per_year[year] = round(year_total, 4)
            if year_total > 0:
                years_with_dividends += 1

        paid_dividends_5_years = years_with_dividends == DIVIDEND_YEARS_MIN

        # Divide sempre por DIVIDEND_YEARS_MIN (não por len dos anos com dividendo)
        # para evitar inflar o price_target quando algum ano não pagou dividendo
        avg_dividends_5y = round(
            sum(v for v in dividends_per_year.values() if not math.isnan(v)) / DIVIDEND_YEARS_MIN, 4
        )

        # --- Soma de dividendos dos últimos 12 meses (yield real Barsi) ---
        # Usa comparação por ano/mês para evitar problema de timezone do yfinance
        one_year_ago = datetime.now() - timedelta(days=365)
        recent_divs = dividends[
            (dividends.index.year > one_year_ago.year) |
            ((dividends.index.year == one_year_ago.year) & (dividends.index.month >= one_year_ago.month))
        ].dropna()
        dividends_sum_12m = round(float(recent_divs[recent_divs > 0].sum()), 4)

        # Dividendo crescente (Barsi): tendência estrutural — tolerância de 10% na queda pontual.
        # Empresa que cresceu dividendo por 4 anos e caiu 5% no último não perde o critério.
        # Evita penalizar tendência de longo prazo por variação de um único ano.
        _years_sorted = sorted(dividends_per_year.keys())
        _newest_div = dividends_per_year.get(_years_sorted[-1], 0)
        _prior_max  = max((dividends_per_year.get(y, 0) for y in _years_sorted[:-1]), default=0)
        dividend_growing = _newest_div > 0 and _newest_div >= _prior_max * 0.90

        # --- Lucro líquido: últimos 5 anos ---
        net_income_per_year: Dict[str, Optional[float]] = {}
        years_with_positive_income = 0

        try:
            financials = yf_ticker.financials
            for year in target_years:
                year_int = int(year)
                matching = [col for col in financials.columns if col.year == year_int]
                if matching and "Net Income" in financials.index:
                    value = financials.loc["Net Income", matching[0]]
                    if value is not None and not math.isnan(float(value)):
                        net_income = round(float(value), 2)
                        net_income_per_year[year] = net_income
                        if net_income > 0:
                            years_with_positive_income += 1
                    else:
                        net_income_per_year[year] = None
                else:
                    net_income_per_year[year] = None
        except Exception:
            net_income_per_year = {year: None for year in target_years}

        years_with_data = sum(1 for v in net_income_per_year.values() if v is not None)
        positive_income_5_years = (
            years_with_positive_income == years_with_data
            and years_with_data >= DIVIDEND_YEARS_MIN - 1
        )

        # --- Payout: StatusInvest ---
        payout = fetch_payout(ticker)

        # --- Buffett Cashflow (Fase 2): FCF, Owner Earnings, CapEx ---
        buffett_cf = fetch_cashflow(ticker)

        # --- Buffett Trends (Fase 3): tendências históricas 4 anos ---
        buffett_tr = fetch_trends(ticker)

        return {
            "price_min_6m":               round(price_min_6m, 2),
            "price_max_6m":               round(price_max_6m, 2),
            "close_avg_6m":               round(close_avg, 2),
            "volume_avg_6m":              round(volume_avg, 0),
            "accumulation_score":         accumulation_score,
            "dividends_per_year":         dividends_per_year,
            "years_with_dividends":       years_with_dividends,
            "paid_dividends_5_years":     paid_dividends_5_years,
            "avg_dividends_5y":           avg_dividends_5y,
            "dividends_sum_12m":          dividends_sum_12m,
            "dividend_growing":           dividend_growing,
            "net_income_per_year":        net_income_per_year,
            "years_with_positive_income": years_with_positive_income,
            "positive_income_5_years":    positive_income_5_years,
            "payout":                     payout,
            "buffett_cashflow":           buffett_cf,
            "buffett_trends":             buffett_tr,
        }

    except Exception:
        return None


def update_ticker(ticker: str, force: bool = False) -> Optional[dict]:
    """
    Busca e persiste o histórico de um ticker.
    Retorna o dict de dados ou None se inválido / falhou.
    """
    if not repo.is_ticker_valid(ticker):
        return None
    if not force and not _needs_update(ticker):
        return repo.get_history(ticker)

    data = fetch_history(ticker)
    if data is not None:
        repo.save_history(ticker, data)
    return data


def update_all(tickers: Optional[List[str]] = None, force: bool = False, delay: float = 0.5) -> dict:
    """
    Atualiza histórico dos tickers válidos (ou lista fornecida).
    O intervalo HISTORY_UPDATE_INTERVAL_DAYS controla o que realmente é refetchado.
    Retorna dict {ticker: entry_or_None}.
    """
    if tickers is None:
        tickers = repo.get_valid_tickers()
        if not tickers:
            tickers = repo.get_tickers_list()

    results = {}
    total = len(tickers)
    for i, ticker in enumerate(tickers, 1):
        entry = update_ticker(ticker, force=force)
        results[ticker] = entry
        if entry:
            div_years   = entry.get("years_with_dividends", 0)
            avg_div     = entry.get("avg_dividends_5y", 0.0)
            inc_years   = entry.get("years_with_positive_income", 0)
            inc_data    = sum(1 for v in entry.get("net_income_per_year", {}).values() if v is not None)
            payout      = entry.get("payout")
            payout_str  = f"{payout:.1f}%" if payout is not None else "N/A"
            print(
                f"[{i:4d}/{total}] {ticker:<12} "
                f"min={entry['price_min_6m']:6.2f}  max={entry['price_max_6m']:6.2f}  "
                f"div={div_years}/{DIVIDEND_YEARS_MIN} avg=R${avg_div:.4f}  "
                f"income={inc_years}/{inc_data}(req≥{DIVIDEND_YEARS_MIN-1})  payout={payout_str}"
            )
        else:
            print(f"[{i:4d}/{total}] {ticker:<12} FALHA")
        if delay > 0:
            time.sleep(delay)

    success = sum(1 for v in results.values() if v is not None)
    print(f"\nConcluído: {success}/{total} históricos atualizados.")
    return results


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv

    tickers_arg = [t.upper() for t in args] if args else None
    update_all(tickers=tickers_arg, force=force)
