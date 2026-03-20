"""
Portfolio service — lê o arquivo de custódia B3 (XLS) e cruza com
valuations.json para gerar recomendações por ativo.

Apenas ativos presentes em valuations.json são incluídos.
FIIs e outros ativos sem cobertura são ignorados silenciosamente.
"""

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import xlrd

from repositories import stock_repository as repo
from services.price_service import PriceService
from services import valuation_calculator

B3_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "B3")


def _find_b3_file() -> Optional[str]:
    """Retorna o primeiro arquivo .xls/.xlsx encontrado na pasta B3."""
    try:
        for fname in os.listdir(B3_DIR):
            if fname.lower().endswith(".xls") or fname.lower().endswith(".xlsx"):
                return os.path.join(B3_DIR, fname)
    except FileNotFoundError:
        pass
    return None


def _recommend(val: dict) -> str:
    zone        = val.get("zone", "")
    rank        = val.get("rank") or 0
    p_now_p_min = val.get("p_now_p_min") or 9999

    if zone == "COMPRA_FORTE" and rank >= 12 and p_now_p_min <= 1.15:
        return "AUMENTAR"
    if zone in ("COMPRA", "COMPRA_FORTE") and rank >= 9:
        return "COMPRAR_MAIS"
    if zone == "MONITORAR" or 6 <= rank <= 8:
        return "AGUARDAR"
    return "AVALIAR_VENDA"


def load() -> dict:
    """
    Lê o arquivo de custódia B3, cruza com valuations e retorna
    { summary: {...}, positions: [...] }.

    - Ativo em valuations.json       → dados completos + recomendação
    - Ativo em stocks_list mas não em valuations → incluído como "FORA_CRITERIOS"
    - Ativo desconhecido (FII, etc.) → ignorado silenciosamente
    """
    b3_file = _find_b3_file()
    if not b3_file:
        return {"summary": {}, "positions": [], "error": "Arquivo B3 não encontrado"}

    try:
        wb = xlrd.open_workbook(b3_file)
        sh = wb.sheet_by_index(0)
    except Exception as e:
        return {"summary": {}, "positions": [], "error": str(e)}

    known_tickers = set(repo.get_tickers_list())
    price_svc     = PriceService()

    # ── Pré-carregar dados do disco uma única vez ──────────────────
    all_valuations = repo.get_all_valuations()   # evita 25+ leituras de valuations.json
    all_prices     = repo.get_all_prices()        # evita N leituras de stock_prices.json

    # ── Ler linhas válidas da planilha ─────────────────────────────
    rows = []
    for i in range(1, sh.nrows):
        row = sh.row_values(i)
        try:
            ticker      = str(row[2]).strip().upper()
            qtd         = int(float(row[3]))
            preco_medio = float(row[4])
            total_inv   = float(row[5])
            retorno     = float(row[6])
        except (ValueError, IndexError):
            continue
        if not ticker or qtd <= 0:
            continue
        val = all_valuations.get(ticker)
        if val is None and ticker not in known_tickers:
            continue  # FII / Tesouro — ignora
        rows.append((ticker, qtd, preco_medio, total_inv, retorno, val))

    # ── Verificar staleness em memória (sem leitura de disco) ─────
    tickers_needed = [r[0] for r in rows]
    stale_tickers  = [t for t in tickers_needed if price_svc.needs_update(t)]

    if stale_tickers:
        # Busca HTTP em paralelo — sem salvar dentro da thread (evita race condition no JSON)
        def _fetch(ticker):
            return ticker, price_svc.fetch_from_google(ticker)

        with ThreadPoolExecutor(max_workers=10) as pool:
            fetched = dict(pool.map(_fetch, stale_tickers))

        # Um único write em disco com todos os preços novos
        repo.save_prices_batch(fetched)

        # Atualiza cache local para não reler o arquivo
        for t, p in fetched.items():
            if p and p > 0:
                all_prices[t] = {"price_now": p}

    # ── Preços finais — do cache em memória (zero I/O adicional) ──
    prices_cache = {t: (all_prices.get(t) or {}).get("price_now") for t in tickers_needed}

    positions       = []
    total_investido = 0.0
    total_atual     = 0.0

    for (ticker, qtd, preco_medio, total_inv, retorno, val) in rows:
        preco_atual = prices_cache.get(ticker)
        if preco_atual and preco_atual > 0:
            valor_atual = preco_atual * qtd
        else:
            # Fallback para o cálculo do XLS se ainda não há preço disponível
            valor_atual = total_inv + retorno
            preco_atual = (valor_atual / qtd) if qtd else None

        retorno_rs  = valor_atual - total_inv
        retorno_pct = ((retorno_rs / total_inv) * 100) if total_inv else None

        if val is not None:
            avg_div    = val.get("avg_dividends_5y")
            dy_on_cost = ((avg_div / preco_medio) * 100) if (avg_div and preco_medio) else None
            position = {
                "ticker":            ticker,
                "qtd":               qtd,
                "preco_medio":       round(preco_medio, 2),
                "preco_atual":       round(preco_atual, 2)   if preco_atual  is not None else None,
                "total_investido":   round(total_inv, 2),
                "valor_atual":       round(valor_atual, 2),
                "retorno":           round(retorno_rs, 2),
                "retorno_pct":       round(retorno_pct, 2)   if retorno_pct  is not None else None,
                "dy_on_cost":        round(dy_on_cost, 2)    if dy_on_cost   is not None else None,
                "zone":              val.get("zone"),
                "rank":              val.get("rank"),
                "rank_max":          val.get("rank_max"),
                "weighted_score":    (val.get("weighted_score") or {}).get("score"),
                "piotroski_score":   (val.get("piotroski") or {}).get("score"),
                "piotroski_label":   (val.get("piotroski") or {}).get("label"),
                "buffett_moat_score":(val.get("buffett_moat") or {}).get("score"),
                "buffett_moat_label":(val.get("buffett_moat") or {}).get("label"),
                "dy_real":           val.get("dy_real"),
                "p_now_p_min":       val.get("p_now_p_min"),
                "gain_pct":          val.get("gain_pct_to_target"),
                "price_target_6pct": val.get("price_target_6pct"),
                "recommendation":    _recommend(val),
            }
        else:
            # Ação conhecida que falhou nos filtros obrigatórios
            # Tenta calcular análise completa sem restrições de pré-qualificação
            forced_val = valuation_calculator.calculate(ticker, force=True)
            if forced_val and preco_atual and preco_atual > 0:
                # Recalcula price_now com preço atualizado do cache
                forced_val["price_now"] = round(preco_atual, 2)
                avg_div_f = forced_val.get("avg_dividends_5y") or 0
                dy_on_cost_f = round((avg_div_f / preco_medio) * 100, 2) if avg_div_f and preco_medio else None
            else:
                dy_on_cost_f = None
            position = {
                "ticker":            ticker,
                "qtd":               qtd,
                "preco_medio":       round(preco_medio, 2),
                "preco_atual":       round(preco_atual, 2)   if preco_atual  is not None else None,
                "total_investido":   round(total_inv, 2),
                "valor_atual":       round(valor_atual, 2),
                "retorno":           round(retorno_rs, 2),
                "retorno_pct":       round(retorno_pct, 2)   if retorno_pct  is not None else None,
                "dy_on_cost":        dy_on_cost_f,
                "zone":              forced_val.get("zone")                                     if forced_val else None,
                "rank":              forced_val.get("rank")                                     if forced_val else None,
                "rank_max":          forced_val.get("rank_max")                                 if forced_val else None,
                "weighted_score":    (forced_val.get("weighted_score") or {}).get("score")      if forced_val else None,
                "piotroski_score":   (forced_val.get("piotroski") or {}).get("score")           if forced_val else None,
                "piotroski_label":   (forced_val.get("piotroski") or {}).get("label")           if forced_val else None,
                "buffett_moat_score":(forced_val.get("buffett_moat") or {}).get("score")        if forced_val else None,
                "buffett_moat_label":(forced_val.get("buffett_moat") or {}).get("label")        if forced_val else None,
                "dy_real":           forced_val.get("dy_real")                                  if forced_val else None,
                "p_now_p_min":       forced_val.get("p_now_p_min")                              if forced_val else None,
                "gain_pct":          forced_val.get("gain_pct_to_target")                       if forced_val else None,
                "price_target_6pct": forced_val.get("price_target_6pct")                        if forced_val else None,
                "recommendation":    "FORA_CRITERIOS",
            }

        positions.append(position)
        total_investido += total_inv
        total_atual     += valor_atual  # já recalculado com preço do cache

    retorno_total     = total_atual - total_investido
    retorno_total_pct = ((retorno_total / total_investido) * 100) if total_investido else 0.0

    summary = {
        "total_investido":   round(total_investido, 2),
        "total_atual":       round(total_atual, 2),
        "retorno_total":     round(retorno_total, 2),
        "retorno_total_pct": round(retorno_total_pct, 2),
        "count":             len(positions),
    }

    return {"summary": summary, "positions": positions}
