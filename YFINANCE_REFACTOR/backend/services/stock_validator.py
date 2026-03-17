"""
Serviço de validação de tickers.
Verifica periodicamente se cada ticker ainda está ativo e com dados disponíveis.

Um ticker é marcado como INVÁLIDO quando ocorre qualquer das condições:
  - yfinance não retorna histórico de preço nos últimos 6 meses (sem negociação)
  - yfinance retorna objeto vazio / ticker inexistente
  - Google Finance não retorna preço por N tentativas consecutivas

A validação respeita VALIDATION_INTERVAL_DAYS para não re-validar o que foi
checado recentemente.

Uso direto:
    python stock_validator.py                  # valida todos os tickers da lista
    python stock_validator.py BBAS3 PETR4      # valida tickers específicos
    python stock_validator.py --report         # exibe relatório de inválidos
"""

import sys
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple

import yfinance

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories import stock_repository as repo
from config.rules import VALIDATION_INTERVAL_DAYS


def _needs_check(ticker: str) -> bool:
    """Retorna True se o ticker precisa ser re-validado."""
    entry = repo.get_validity(ticker)
    if entry is None:
        return True
    last_check_str = entry.get("last_check")
    if not last_check_str:
        return True
    last_check = datetime.fromisoformat(last_check_str)
    return datetime.now() - last_check > timedelta(days=VALIDATION_INTERVAL_DAYS)


def _check_ticker_yfinance(ticker: str) -> Tuple[bool, str]:
    """
    Verifica via yfinance se o ticker tem dados válidos.
    Retorna (is_valid, reason_if_invalid).
    """
    yf_ticker_str = f"{ticker.upper()}.SA"
    try:
        yf = yfinance.Ticker(yf_ticker_str)

        # Tenta obter histórico dos últimos 6 meses
        hist = yf.history(period="6mo")
        if hist.empty:
            return False, "no_price_6_months"

        # Verifica se há pelo menos 10 dias de negociação (evita dados espúrios)
        if len(hist) < 10:
            return False, "insufficient_trading_days"

        # Verifica se o último preço não é zero
        last_close = hist["Close"].iloc[-1]
        if last_close <= 0:
            return False, "zero_price"

        return True, ""

    except Exception as e:
        error_msg = str(e).lower()
        if "delisted" in error_msg or "no data" in error_msg:
            return False, "delisted"
        return False, "yfinance_error"


def validate_ticker(ticker: str, force: bool = False) -> dict:
    """
    Valida um ticker e persiste o resultado em stock_validity.json.
    Retorna o dict de validade atualizado.
    """
    ticker = ticker.upper()

    existing = repo.get_validity(ticker)

    if not force and not _needs_check(ticker):
        return existing or {"ticker": ticker, "is_valid": True}

    is_valid, reason = _check_ticker_yfinance(ticker)

    # Calcula falhas consecutivas
    prev_failures = 0
    if existing:
        prev_failures = existing.get("consecutive_failures", 0)

    if is_valid:
        consecutive_failures = 0
    else:
        consecutive_failures = prev_failures + 1

    # 1 falha = inválido. Se voltar a passar, marca válido novamente.
    final_is_valid = is_valid

    check_count = (existing.get("check_count", 0) if existing else 0) + 1

    entry = {
        "is_valid":             final_is_valid,
        "last_valid":           datetime.now().isoformat() if is_valid else (
                                    existing.get("last_valid") if existing else None
                                ),
        "check_count":          check_count,
        "consecutive_failures": consecutive_failures,
        "validation_source":    "yfinance",
        "reason_invalid":       reason if not final_is_valid else None,
    }

    repo.save_validity(ticker, entry)
    return entry


def validate_all(tickers: Optional[list] = None, force: bool = False, delay: float = 0.5) -> dict:
    """
    Valida todos os tickers (ou lista fornecida).
    Retorna dict {ticker: entry}.
    """
    if tickers is None:
        tickers = repo.get_tickers_list()

    results = {}
    total = len(tickers)
    valid_count = 0
    invalid_count = 0

    for i, ticker in enumerate(tickers, 1):
        entry = validate_ticker(ticker, force=force)
        results[ticker] = entry

        is_valid = entry.get("is_valid", True)
        if is_valid:
            valid_count += 1
            status = "✓ válido"
        else:
            invalid_count += 1
            reason = entry.get("reason_invalid", "?")
            failures = entry.get("consecutive_failures", 0)
            status = f"✗ INVÁLIDO [{reason}] falhas={failures}"

        print(f"[{i:4d}/{total}] {ticker:<12} {status}")
        if delay > 0:
            time.sleep(delay)

    print(f"\nConcluído: {valid_count} válidos, {invalid_count} inválidos de {total} tickers.")
    return results


def print_report() -> None:
    """Exibe relatório dos tickers inválidos e válidos."""
    invalid = repo.get_invalid_tickers()
    valid   = repo.get_valid_tickers()

    print(f"{'='*50}")
    print(f"RELATÓRIO DE VALIDADE DE TICKERS")
    print(f"{'='*50}")
    print(f"Válidos  : {len(valid)}")
    print(f"Inválidos: {len(invalid)}")
    print(f"{'='*50}")

    if invalid:
        print("\nTickers INVÁLIDOS:")
        for ticker in sorted(invalid):
            entry = repo.get_validity(ticker)
            reason  = entry.get("reason_invalid", "?") if entry else "?"
            failures = entry.get("consecutive_failures", 0) if entry else 0
            last_valid = entry.get("last_valid", "nunca") if entry else "nunca"
            print(f"  {ticker:<12} motivo={reason:<30} falhas={failures} último_válido={last_valid}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    if "--report" in sys.argv:
        print_report()
    else:
        tickers_arg = [t.upper() for t in args] if args else None
        validate_all(tickers=tickers_arg, force=force)
