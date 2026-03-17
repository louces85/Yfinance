"""
Serviço de decisão de compra.

Lê os ativos qualificados de monitoring_stocks.json, atualiza o preço via
Google Finance, correlaciona com o histórico de 6 meses e calcula métricas
de entrada. Persiste em data/decision_stocks.json.

Campos no JSON de saída (ordenados por p_now_p_min ASC):
  ticker, price_now, price_target_6pct, price_target_8pct, price_target_5pct,
  gain_pct, price_min_6m, price_max_6m, p_now_p_min,
  rank, rank_max, zone, dy_real, payout, accumulation_score, sector,
  dividend_growing, is_below_vpa_target, is_gold

Uso direto:
    python decision_service.py                # processa todos os monitorados
    python decision_service.py BBAS3 PETR4   # tickers específicos
    python decision_service.py --force        # força novo fetch de preço
"""

import sys
import os
import time
from typing import Optional, List

import yfinance

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories import stock_repository as repo
from services.price_service import PriceService


def _safe_float(value, default=None) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _calc_accumulation_recent(ticker: str, close_avg: float, volume_avg: float) -> dict:
    """
    Busca os últimos 5 pregões via yfinance (period='5d') e conta quantos dias
    tiveram preço de fechamento E volume ambos abaixo da média dos 6 meses.

    Filtra dias com volume == 0 para evitar o bug do Yahoo Finance que zera o
    volume do dia corrente quando consultado fora do horário do pregão.

    Retorna:
      accumulation_recent_days  — int: dias com sinal de acumulação (ex: 3)
      accumulation_recent_total — int: total de pregões válidos no período (ex: 5)
    """
    empty = {"accumulation_recent_days": None, "accumulation_recent_total": None}
    if not close_avg or not volume_avg:
        return empty
    try:
        df = yfinance.Ticker(f"{ticker}.SA").history(period="5d")
        # Remove dias sem negociação (bug Yahoo: volume zerado fora do pregão)
        df = df[df["Volume"] > 0].dropna(subset=["Close", "Volume"])
        if df.empty:
            return empty
        cond  = (df["Close"] < close_avg) & (df["Volume"] < volume_avg)
        return {
            "accumulation_recent_days":  int(cond.sum()),
            "accumulation_recent_total": len(df),
        }
    except Exception:
        return empty


def _build_entry(ticker: str, price_now: float, valuation: dict, history: dict) -> dict:
    """Constrói a entrada de decisão para um ticker."""
    target_6 = _safe_float(valuation.get("price_target_6pct"))
    target_8 = _safe_float(valuation.get("price_target_8pct"))
    target_5 = _safe_float(valuation.get("price_target_5pct"))
    price_min = _safe_float(history.get("price_min_6m"))
    price_max = _safe_float(history.get("price_max_6m"))
    avg_div   = _safe_float(valuation.get("avg_dividends_4y"), 0)

    # pNow/pMin: quanto o preço atual está acima do mínimo de 6m
    # Valor < 1.10 = ótima entrada; > 1.50 = caro em relação ao fundo
    p_now_p_min = round(price_now / price_min, 4) if price_min and price_min > 0 else None

    # Ganho potencial em % até o price_target_6pct
    gain_pct = round(((target_6 - price_now) / price_now) * 100, 2) if target_6 else None

    # DY real com preço atualizado
    dy_real = round((avg_div / price_now) * 100, 2) if avg_div and avg_div > 0 else None

    # Score de acumulação silenciosa histórico (6 meses, calculado no history_fetcher)
    accumulation_score = _safe_float(history.get("accumulation_score"))

    # Acumulação recente (última semana): consulta 5d ao yfinance com médias do histórico
    close_avg_6m  = _safe_float(history.get("close_avg_6m"))
    volume_avg_6m = _safe_float(history.get("volume_avg_6m"))
    recent = _calc_accumulation_recent(ticker, close_avg_6m, volume_avg_6m)

    # is_below_vpa_target: abaixo do VPA e do target de 6% simultaneamente
    vpa = _safe_float(valuation.get("indicators", {}).get("vpa"))
    below_vpa    = vpa is not None and price_now <= vpa
    below_target = target_6 is not None and price_now <= target_6
    is_below_vpa_target = below_vpa and below_target

    # dividend_growing: dividendo do último ano >= máximo dos anos anteriores (Barsi)
    dividend_growing = history.get("dividend_growing", False)

    # is_gold: abaixo VPA + abaixo target 6% + dividendo crescente
    is_gold = is_below_vpa_target and dividend_growing

    indicators = valuation.get("indicators", {})

    return {
        "ticker":               ticker.upper(),
        "price_now":            round(price_now, 2),
        "price_target_6pct":    target_6,
        "price_target_8pct":    target_8,
        "price_target_5pct":    target_5,
        "gain_pct":             gain_pct,
        "price_min_6m":         price_min,
        "price_max_6m":         price_max,
        "p_now_p_min":          p_now_p_min,
        "rank":                 valuation.get("rank"),
        "rank_max":             valuation.get("rank_max"),
        "zone":                 valuation.get("zone"),
        "dy_real":              dy_real,
        "avg_dividends_4y":     avg_div,
        "payout":               valuation.get("payout"),
        "accumulation_score":        accumulation_score,
        "accumulation_recent_days":  recent["accumulation_recent_days"],
        "accumulation_recent_total": recent["accumulation_recent_total"],
        "sector":               indicators.get("sector", "-"),
        "dividend_growing":     dividend_growing,
        "is_below_vpa_target":  is_below_vpa_target,
        "is_gold":              is_gold,
    }


def run(tickers: Optional[List[str]] = None, force: bool = False, delay: float = 0.3) -> List[dict]:
    """
    Processa os tickers qualificados e gera decision_stocks.json.

    tickers: lista específica ou None para usar todos de monitoring_stocks.json
    force:   força novo fetch de preço mesmo que esteja dentro do intervalo
    Retorna a lista de entradas gerada.
    """
    svc = PriceService()

    # Fonte de tickers: argumento ou monitoring_stocks.json
    if tickers is None:
        monitoring = repo.get_monitoring_stocks()
        tickers = [m["ticker"] for m in monitoring]

    if not tickers:
        print("Nenhum ticker em monitoring_stocks.json. Rode valuation_calculator.py primeiro.")
        return []

    entries = []
    total = len(tickers)

    for i, ticker in enumerate(tickers, 1):
        ticker = ticker.upper()

        # 1. Preço atual via Google Finance (com cache)
        price_now = svc.update(ticker, force=force)
        if price_now is None or price_now <= 0:
            print(f"[{i:4d}/{total}] {ticker:<12} FALHA (sem preço)")
            if delay > 0:
                time.sleep(delay)
            continue

        # 2. Valuation (já calculado pelo valuation_calculator)
        valuation = repo.get_valuation(ticker)
        if valuation is None:
            print(f"[{i:4d}/{total}] {ticker:<12} FALHA (sem valuation)")
            if delay > 0:
                time.sleep(delay)
            continue

        # 3. Histórico: min/max 6m
        history = repo.get_history(ticker)
        if history is None:
            print(f"[{i:4d}/{total}] {ticker:<12} FALHA (sem histórico)")
            if delay > 0:
                time.sleep(delay)
            continue

        entry = _build_entry(ticker, price_now, valuation, history)
        entries.append(entry)

        rd = entry["accumulation_recent_days"]
        rt = entry["accumulation_recent_total"]
        recent_str = f"{rd}/{rt}d" if rd is not None else "-"
        print(
            f"[{i:4d}/{total}] {ticker:<12} "
            f"R${price_now:6.2f}  "
            f"pNow/pMin={entry['p_now_p_min'] or '-':>7}  "
            f"gain={entry['gain_pct'] or '-':>7}%  "
            f"zone={entry['zone'] or '-':<14}  "
            f"acum={entry['accumulation_score'] or '-':>5}%  "
            f"recente={recent_str}"
        )

        if delay > 0:
            time.sleep(delay)

    # Ordena por p_now_p_min ASC (menor ratio = preço mais próximo do fundo)
    # Tickers sem p_now_p_min vão para o final
    entries.sort(key=lambda x: (x["p_now_p_min"] is None, x["p_now_p_min"] or 9999))

    # Persiste
    _save_decision_stocks(entries)

    success = len(entries)
    print(f"\nConcluído: {success}/{total} tickers processados → decision_stocks.json atualizado.")
    return entries


def _save_decision_stocks(entries: List[dict]) -> None:
    from datetime import datetime
    import json

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(BASE_DIR, "data", "decision_stocks.json")

    data = {
        "last_updated": datetime.now().isoformat(),
        "total": len(entries),
        "stocks": entries,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv

    tickers_arg = [t.upper() for t in args] if args else None
    run(tickers=tickers_arg, force=force)
