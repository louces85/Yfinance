"""
Serviço de cálculo de valuation por ticker.
Combina dados de:
  - all_indicators.json (indicadores fundamentalistas)
  - stock_history.json  (min/max 6m + dividendos 4a)
  - stock_prices.json   (preço atual)

Calcula e persiste em data/valuations.json via stock_repository.

Critérios implementados (baseados em Barsi, Bazin, Graham, Greenblatt, Lynch):
  1.  DY real >= 6%
  2.  Preço abaixo do price_target_6pct (Bazin/Barsi)
  3.  Preço abaixo do price_target_8pct (zona agressiva Barsi)
  4.  P/VP <= 1.5
  5.  Preço <= VPA
  6.  P/L <= 15
  7.  Graham combinado: P/L × P/VP <= 22.5
  8.  Dívida Líq./PL <= 1
  9.  Dívida Líq./EBITDA <= 3
  10. Liquidez Corrente >= 2 (Graham)
  11. Margem EBIT >= 10%
  12. Margem Líquida >= 10%
  13. ROE >= 10%
  14. ROIC >= 10%
  15. CAGR Receita 5a >= 5%
  16. CAGR Lucro 5a >= 5%
  17. Payout entre 40% e 80% (Bazin)
  18. Pagou dividendos nos últimos 4 anos
  19. Liquidez diária >= R$200k
  20. Passivo/Ativo <= 1
  21. Score de acumulação silenciosa >= 50% (Barsi)

Rank máximo: 21 pontos.

Uso direto:
    python valuation_calculator.py                  # calcula todos os válidos
    python valuation_calculator.py BBAS3 PETR4      # calcula tickers específicos
"""

import sys
import os
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories import stock_repository as repo
from config import rules


def _safe_float(value, default=None) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _calc_zone(price_now: float, target_6: float, target_8: float, target_5: float) -> str:
    """
    Determina a zona de preço do ativo:
      COMPRA_FORTE : preço <= target_8pct (yield real >= 8%)
      COMPRA       : preço <= target_6pct (yield real >= 6%)
      MONITORAR    : preço <= target_5pct (yield real >= 5%)
      CARO         : preço > target_5pct
    """
    if target_8 and price_now <= target_8:
        return "COMPRA_FORTE"
    if target_6 and price_now <= target_6:
        return "COMPRA"
    if target_5 and price_now <= target_5:
        return "MONITORAR"
    return "CARO"


def _calc_weighted_score(flags: dict) -> dict:
    """
    Score ponderado (0-100) baseado nos 21 critérios com pesos diferenciados.

    Grupos e pesos (ver rules.WEIGHTED_SCORE_WEIGHTS):
      Qualidade/Rentabilidade : peso 3  (ROE, ROIC, margens)
      Crescimento             : peso 2  (CAGR receita/lucro, dividendo crescente)
      Dívida/Segurança        : peso 2  (DL/PL, DL/EBITDA, passivo/ativo, liq. corrente)
      Preço/Valuation         : peso 1.5 (P/L, P/VP, Graham, abaixo VPA)
      Dividendos/Renda        : peso 1.5 (DY, targets 6%/8%, payout)
      Técnico/Liquidez        : peso 1  (liq. diária, acumulação)

    Retorna dict com score (0-100), pontos ganhos e máximo possível.
    """
    earned = sum(
        rules.WEIGHTED_SCORE_WEIGHTS.get(flag, 0.0)
        for flag, val in flags.items()
        if val
    )
    score = round((earned / rules.WEIGHTED_SCORE_MAX) * 100, 1)
    return {
        "score":          score,
        "score_max":      100,
        "earned_points":  round(earned, 1),
        "max_points":     rules.WEIGHTED_SCORE_MAX,
    }


def _calc_buffett_moat_score(indicators_raw: dict, history: dict) -> dict:
    """
    Buffett Moat Score (0-10) — Fase 1 do plano Warren Buffett.
    Usa apenas dados já disponíveis em all_indicators.json e stock_history.json.

    Critérios e pesos:
      Margem Bruta >= 40%     : peso 2 (pricing power — critério principal)
      Margem Líquida >= 20%   : peso 1 (Buffett vs. 10% atual)
      ROE >= 20%              : peso 2 (eficiência — critério principal)
      ROIC >= 15%             : peso 1 (Buffett vs. 10% atual)
      DL/PL <= 0.5            : peso 1 (dívida muito baixa)
      CAGR Lucro 5a >= 10%    : peso 1 (crescimento acima da inflação)
      CAGR Receita 5a >= 5%   : peso 1 (crescimento real de receita)
      Dividendo crescente     : peso 1 (sinal de saúde do negócio)

    Score: 0–10 pontos
      >= 7 → FORTE    (vantagem competitiva durável provável)
       4–6 → MODERADO (moat parcial ou em desenvolvimento)
      <= 3 → FRACO    (sem evidência de moat)
    """
    score = 0
    flags = {}

    # Margem Bruta >= 40% (peso 2 — critério principal de pricing power)
    mb = indicators_raw.get("margem_bruta")
    flags["moat_margem_bruta"] = mb is not None and mb >= 40
    if flags["moat_margem_bruta"]: score += 2

    # Margem Líquida >= 20% (Buffett — mais exigente que o limiar padrão de 10%)
    ml = indicators_raw.get("margem_liq")
    flags["moat_margem_liquida"] = ml is not None and ml >= 20
    if flags["moat_margem_liquida"]: score += 1

    # ROE >= 20% (peso 2 — Buffett: eficiência na conversão de capital em lucro)
    roe = indicators_raw.get("roe")
    flags["moat_roe"] = roe is not None and roe >= 20
    if flags["moat_roe"]: score += 2

    # ROIC >= 15% (Buffett — mais exigente que o limiar padrão de 10%)
    roic = indicators_raw.get("roic")
    flags["moat_roic"] = roic is not None and roic >= 15
    if flags["moat_roic"]: score += 1

    # DL/PL <= 0.5 (empresas com moat real não precisam de muita dívida)
    dl_pl = indicators_raw.get("dl_pl")
    flags["moat_baixa_divida"] = dl_pl is not None and dl_pl <= 0.5
    if flags["moat_baixa_divida"]: score += 1

    # CAGR Lucro 5a >= 10% (crescimento real acima da inflação)
    cagr_l = indicators_raw.get("cagr_lucro")
    flags["moat_lucro_crescendo"] = cagr_l is not None and cagr_l >= 10
    if flags["moat_lucro_crescendo"]: score += 1

    # CAGR Receita 5a >= 5% (crescimento consistente de receita)
    cagr_r = indicators_raw.get("cagr_receita")
    flags["moat_receita_crescendo"] = cagr_r is not None and cagr_r >= 5
    if flags["moat_receita_crescendo"]: score += 1

    # Dividendo crescente (sinal de geração de caixa sustentável)
    flags["moat_div_crescente"] = history.get("dividend_growing", False)
    if flags["moat_div_crescente"]: score += 1

    # --- Critérios de Fluxo de Caixa (Fase 2) — informacionais, não afetam o score ---
    cf = history.get("buffett_cashflow") or {}
    flags["cashflow_available"]        = cf.get("cashflow_available", False)
    flags["moat_fcf_positivo"]         = cf.get("fcf_positivo", False)
    flags["moat_fcf_quality"]          = cf.get("fcf_quality_ok", False)
    flags["moat_capex_moat"]           = cf.get("capex_moat_ok", False)
    flags["moat_owner_earnings_ok"]    = cf.get("owner_earnings_positivo", False)

    if score >= 7:
        label = "FORTE"
    elif score >= 4:
        label = "MODERADO"
    else:
        label = "FRACO"

    cashflow_values = {
        "fcf":              cf.get("fcf"),
        "owner_earnings":   cf.get("owner_earnings"),
        "net_income_cf":    cf.get("net_income_cf"),
        "fcf_lucro_ratio":  cf.get("fcf_lucro_ratio"),
        "capex_lucro_ratio": cf.get("capex_lucro_ratio"),
        "capex":            cf.get("capex"),
        "da":               cf.get("da"),
    }

    return {
        "score":            score,
        "score_max":        10,
        "label":            label,
        "flags":            flags,
        "cashflow_values":  cashflow_values,
    }


def _calc_piotroski(indicators: dict, history: dict) -> dict:
    """
    Piotroski F-Score adaptado (9 pontos) com os dados disponíveis.

    Profitabilidade (3 sinais):
      P1 — Lucro Líquido positivo no ano mais recente
      P2 — Margem EBIT > 0  (proxy de CF Operacional positivo)
      P3 — Lucro crescendo  (ano mais recente > ano anterior)

    Alavancagem / Liquidez (3 sinais):
      P4 — DL/PL <= 0.5  (alavancagem conservadora; metade do limite do filtro principal)
      P5 — Liq. Corrente >= 1.5  (cobertura de curto prazo sólida)
      P6 — Passivo/Ativo <= 0.4  (balanço conservador)

    Eficiência / Qualidade (3 sinais):
      P7 — CAGR Lucro > CAGR Receita  (margens se expandindo)
      P8 — CAGR Receita > 0  (crescimento real de receita)
      P9 — ROE >= 15%  (rentabilidade forte, acima do mínimo básico de 10%)

    Score: 0–9 pontos
      >= 7 → FORTE    (empresa financeiramente saudável)
       4–6 → MODERADO
      <= 3 → FRACO
    """
    net_income_per_year = history.get("net_income_per_year", {})
    years_sorted = sorted(net_income_per_year.keys())

    latest_income = net_income_per_year.get(years_sorted[-1]) if len(years_sorted) >= 1 else None
    prior_income  = net_income_per_year.get(years_sorted[-2]) if len(years_sorted) >= 2 else None

    dl_pl        = indicators.get("dl_pl")
    passivo_ativo = indicators.get("passivo_ativo")
    liq_corrente = indicators.get("liquidez_corrente")
    m_ebit       = indicators.get("margem_ebit")
    roe          = indicators.get("roe")
    cagr_r       = indicators.get("cagr_receita")
    cagr_l       = indicators.get("cagr_lucro")

    # --- Profitabilidade ---
    p1 = latest_income is not None and latest_income > 0
    p2 = m_ebit is not None and m_ebit > 0
    p3 = (latest_income is not None and prior_income is not None
          and latest_income > prior_income)

    # --- Alavancagem / Liquidez ---
    p4 = dl_pl is not None and dl_pl <= rules.PIOTROSKI_DL_PL_CONSERVADOR
    p5 = liq_corrente is not None and liq_corrente >= rules.PIOTROSKI_LIQ_CORRENTE_MIN
    p6 = passivo_ativo is not None and passivo_ativo <= rules.PIOTROSKI_PASSIVO_ATIVO_MAX

    # --- Eficiência / Qualidade ---
    p7 = (cagr_l is not None and cagr_r is not None and cagr_l > cagr_r)
    p8 = cagr_r is not None and cagr_r > 0
    p9 = roe is not None and roe >= rules.PIOTROSKI_ROE_FORTE

    score = sum([p1, p2, p3, p4, p5, p6, p7, p8, p9])

    if score >= rules.PIOTROSKI_STRONG_MIN:
        label = "FORTE"
    elif score >= rules.PIOTROSKI_MODERATE_MIN:
        label = "MODERADO"
    else:
        label = "FRACO"

    return {
        "score":     score,
        "score_max": 9,
        "label":     label,
        "flags": {
            "p1_lucro_positivo":      p1,
            "p2_ebit_positivo":       p2,
            "p3_lucro_crescendo":     p3,
            "p4_baixa_alavancagem":   p4,
            "p5_liq_corrente":        p5,
            "p6_passivo_ativo":       p6,
            "p7_margens_expandindo":  p7,
            "p8_receita_crescendo":   p8,
            "p9_roe_forte":           p9,
        },
    }


def calculate(ticker: str, force: bool = False) -> Optional[dict]:
    """
    Calcula o valuation completo de um ticker.
    Retorna o dict de valuation ou None se dados insuficientes.

    force=True: ignora os filtros de pré-qualificação (usado para ativos
    da carteira que não passaram no screening, mas precisam de análise).
    O resultado terá "fora_criterios_pre": True nesses casos.
    """
    ticker = ticker.upper()

    # --- Fontes de dados ---
    indicators = repo.get_indicators_by_ticker(ticker)
    history    = repo.get_history(ticker)
    price_now  = repo.get_price(ticker)

    if indicators is None:
        return None
    if history is None:
        return None
    # price_now é opcional: sem ele calcula targets mas não zona/rank por preço

    # --- Filtros obrigatórios (pré-qualificação) ---
    # Só calcula valuation para tickers que atendam os critérios mínimos:
    #   1. Pagou dividendos em todos os últimos 5 anos
    #   2. Teve lucro líquido positivo em todos os últimos 5 anos
    #   3. Liquidez diária mínima de R$200k (dado do all_indicators.json)
    #   4. P/L positivo (P/L negativo indica prejuízo no período)
    pre_qual_failed = []
    if not history.get("paid_dividends_5_years", False):
        pre_qual_failed.append("dividendos_5_anos")
        if not force:
            return None
    if not history.get("positive_income_5_years", False):
        pre_qual_failed.append("lucro_5_anos")
        if not force:
            return None
    liq_diaria_raw = _safe_float(indicators.get("liquidezmediadiaria"), 0)
    if liq_diaria_raw < rules.LIQUIDEZ_DIARIA_MIN:
        pre_qual_failed.append("liquidez_diaria")
        if not force:
            return None
    p_l_raw = _safe_float(indicators.get("p_l"))
    if p_l_raw is None or p_l_raw <= 0:
        pre_qual_failed.append("p_l_positivo")
        if not force:
            return None

    # --- Indicadores fundamentalistas ---
    dy          = _safe_float(indicators.get("dy"))
    p_l         = _safe_float(indicators.get("p_l"))
    p_vp        = _safe_float(indicators.get("p_vp"))
    vpa         = _safe_float(indicators.get("vpa"))
    dl_pl       = _safe_float(indicators.get("dividaliquidapatrimonioliquido"))
    dl_ebitda   = _safe_float(indicators.get("dividaliquidaebit"))
    passivo_ativo = _safe_float(indicators.get("passivo_ativo"))
    liq_corrente  = _safe_float(indicators.get("liquidezcorrente"))
    pl_ativo      = _safe_float(indicators.get("pl_ativo"))

    # Setor financeiro: identificado por estrutura de balanço (pl_ativo muito baixo é
    # estrutural em bancos e seguradoras — depósitos de clientes são passivo circulante).
    # Esses setores ficam isentos dos filtros de liquidez_corrente e passivo_ativo.
    _is_financial = pl_ativo is not None and pl_ativo <= rules.FINANCIAL_PL_ATIVO_MAX
    m_bruta     = _safe_float(indicators.get("margembruta"))
    m_ebit      = _safe_float(indicators.get("margemebit"))
    m_liq       = _safe_float(indicators.get("margemliquida"))
    roe         = _safe_float(indicators.get("roe"))
    roic        = _safe_float(indicators.get("roic"))
    cagr_r      = _safe_float(indicators.get("receitas_cagr5"))
    cagr_l      = _safe_float(indicators.get("lucros_cagr5"))
    liq_diaria  = _safe_float(indicators.get("liquidezmediadiaria"), 0)
    sector      = indicators.get("sectorname", "-")
    segment     = indicators.get("segmentname", "-")

    # --- Histórico ---
    price_min_6m   = _safe_float(history.get("price_min_6m"))
    price_max_6m   = _safe_float(history.get("price_max_6m"))
    avg_div_4y         = _safe_float(history.get("avg_dividends_5y"), 0)
    div_sum_12m        = _safe_float(history.get("dividends_sum_12m"), 0)
    div_growing        = history.get("dividend_growing", False)
    accumulation_score = _safe_float(history.get("accumulation_score"))

    # --- Preços-alvo Bazin/Barsi ---
    price_target_6 = round(avg_div_4y / rules.BASIN_BASE, 2) if avg_div_4y > 0 else None
    price_target_8 = round(avg_div_4y / rules.BASIN_MAX,  2) if avg_div_4y > 0 else None
    price_target_5 = round(avg_div_4y / rules.BASIN_MIN,  2) if avg_div_4y > 0 else None

    # --- Métricas calculadas (dependem do preço atual quando disponível) ---
    has_price   = price_now is not None and price_now > 0
    # Usa soma real dos últimos 12 meses (sinal Barsi); fallback p/ média 4a se ainda sem pagamento recente
    _dy_num = div_sum_12m if div_sum_12m and div_sum_12m > 0 else avg_div_4y
    dy_real     = round((_dy_num / price_now) * 100, 2) if has_price and _dy_num > 0 else None
    p_now_p_min = round(price_now / price_min_6m, 4) if has_price and price_min_6m and price_min_6m > 0 else None
    gain_pct    = round(((price_target_6 - price_now) / price_now) * 100, 2) if has_price and price_target_6 else None
    p_l_x_p_vp  = round(p_l * p_vp, 2) if p_l and p_vp else None
    liq_diaria_m = round(liq_diaria / 1_000_000, 2) if liq_diaria else None

    # --- Payout: StatusInvest (fonte real) ---
    payout = _safe_float(history.get("payout"))

    # --- Flags de critérios ---
    flags = {
        # Critérios independentes do preço atual
        "dl_pl_ok":            dl_pl is not None and dl_pl <= rules.DL_PL_MAX,
        "dl_ebitda_ok":        dl_ebitda is not None and dl_ebitda <= rules.DL_EBITDA_MAX,
        "passivo_ativo_ok":    _is_financial or (passivo_ativo is not None and passivo_ativo <= rules.PASSIVO_ATIVO_MAX),
        "liquidez_corrente_ok":_is_financial or (liq_corrente is not None and liq_corrente >= rules.LIQUIDEZ_CORRENTE_MIN),
        "margem_ebit_ok":      m_ebit is not None and m_ebit >= rules.MARGEM_EBIT_MIN,
        "margem_liq_ok":       m_liq is not None and m_liq >= rules.MARGEM_LIQ_MIN,
        "roe_ok":              roe is not None and roe >= rules.ROE_MIN,
        "roic_ok":             roic is not None and roic >= rules.ROIC_MIN,
        "cagr_receita_ok":     cagr_r is not None and cagr_r >= rules.CAGR_RECEITA_MIN,
        "cagr_lucro_ok":       cagr_l is not None and cagr_l >= rules.CAGR_LUCRO_MIN,
        "payout_ok":           payout is not None and rules.PAYOUT_MIN <= payout <= rules.PAYOUT_MAX,
        "dividendo_crescente_ok": div_growing,
        "liquidez_diaria_ok":  liq_diaria is not None and liq_diaria >= rules.LIQUIDEZ_DIARIA_MIN,
        "p_l_ok":              p_l is not None and 0 < p_l <= rules.P_L_MAX,
        "p_vp_ok":             p_vp is not None and p_vp <= rules.P_VP_MAX,
        "graham_combo_ok":     p_l_x_p_vp is not None and p_l_x_p_vp <= rules.GRAHAM_COMBO,
        # Critérios que dependem do preço atual (None quando sem preço)
        "dy_ok":               dy_real is not None and dy_real >= rules.DIVIDEND_YIELD_MIN,
        "abaixo_vpa":          has_price and vpa is not None and price_now <= vpa,
        "abaixo_target_6pct":  has_price and price_target_6 is not None and price_now < price_target_6,
        "abaixo_target_8pct":  has_price and price_target_8 is not None and price_now < price_target_8,
        # Acumulação silenciosa (Barsi): % de dias com preço E volume abaixo da média
        "accumulation_ok":     accumulation_score is not None and accumulation_score >= rules.ACCUMULATION_SCORE_MIN,
    }

    rank = sum(1 for v in flags.values() if v)
    rank_max = len(flags)

    weighted_score = _calc_weighted_score(flags)

    # Piotroski e Buffett Moat usam indicadores brutos (floats) e histórico de lucros
    _indicators_raw = {
        "dl_pl":            dl_pl,
        "passivo_ativo":    passivo_ativo,
        "liquidez_corrente": liq_corrente,
        "margem_bruta":     m_bruta,
        "margem_ebit":      m_ebit,
        "margem_liq":       m_liq,
        "roe":              roe,
        "roic":             roic,
        "cagr_receita":     cagr_r,
        "cagr_lucro":       cagr_l,
    }
    piotroski = _calc_piotroski(_indicators_raw, history)
    buffett_moat = _calc_buffett_moat_score(_indicators_raw, history)

    zone = _calc_zone(
        price_now or 0,
        price_target_6 or 0,
        price_target_8 or 0,
        price_target_5 or 0,
    ) if has_price else "SEM_PRECO"

    result = {
        "price_now":          round(price_now, 2) if price_now else None,
        "price_min_6m":       price_min_6m,
        "price_max_6m":       price_max_6m,
        "avg_dividends_5y":   avg_div_4y,
        "price_target_6pct":  price_target_6,
        "price_target_8pct":  price_target_8,
        "price_target_5pct":  price_target_5,
        "dy_real":            dy_real,
        "payout":             payout,
        "accumulation_score": accumulation_score,
        "p_now_p_min":        p_now_p_min,
        "gain_pct_to_target": gain_pct,
        "rank":               rank,
        "rank_max":           rank_max,
        "zone":               zone,
        "weighted_score":     weighted_score,
        "piotroski":          piotroski,
        "buffett_moat":       buffett_moat,
        "flags":              flags,
        "indicators": {
            "margem_bruta":         m_bruta,
            "dy":                   dy,
            "p_l":                  p_l,
            "p_vp":                 p_vp,
            "vpa":                  vpa,
            "p_l_x_p_vp":          p_l_x_p_vp,
            "dl_pl":                dl_pl,
            "dl_ebitda":            dl_ebitda,
            "passivo_ativo":        passivo_ativo,
            "liquidez_corrente":    liq_corrente,
            "margem_ebit":          m_ebit,
            "margem_liq":           m_liq,
            "roe":                  roe,
            "roic":                 roic,
            "cagr_receita":         cagr_r,
            "cagr_lucro":           cagr_l,
            "liquidez_diaria_milhoes": liq_diaria_m,
            "sector":               sector,
            "segment":              segment,
        },
    }
    if pre_qual_failed:
        result["fora_criterios_pre"] = True
        result["pre_qual_reprovado"] = pre_qual_failed
    return result


def update_ticker(ticker: str) -> Optional[dict]:
    """Calcula e persiste o valuation de um ticker. Retorna o dict ou None."""
    if not repo.is_ticker_valid(ticker):
        return None
    result = calculate(ticker)
    if result is not None:
        repo.save_valuation(ticker, result)
    return result


def update_all(tickers: Optional[list] = None) -> dict:
    """
    Calcula valuation de todos os tickers (ou lista fornecida).
    Requer que stock_prices.json e stock_history.json já estejam populados.
    Retorna dict {ticker: entry_or_None}.
    """
    if tickers is None:
        tickers = repo.get_valid_tickers()
        if not tickers:
            tickers = repo.get_tickers_list()

    results = {}
    monitoring = []
    total = len(tickers)

    for i, ticker in enumerate(tickers, 1):
        entry = update_ticker(ticker)
        results[ticker] = entry
        if entry:
            monitoring.append({
                "ticker":              ticker,
                "rank":                entry["rank"],
                "rank_max":            entry["rank_max"],
                "weighted_score":      entry["weighted_score"]["score"],
                "piotroski_score":     entry["piotroski"]["score"],
                "piotroski_label":     entry["piotroski"]["label"],
                "buffett_moat_score":  entry["buffett_moat"]["score"],
                "buffett_moat_label":  entry["buffett_moat"]["label"],
                "zone":                entry["zone"],
                "price_now":           entry["price_now"],
                "price_target_6pct":   entry["price_target_6pct"],
                "price_target_8pct":   entry["price_target_8pct"],
                "dy_real":             entry["dy_real"],
                "avg_dividends_5y":    entry["avg_dividends_5y"],
                "payout":              entry["payout"],
                "sector":              entry["indicators"]["sector"],
            })
            print(
                f"[{i:4d}/{total}] {ticker:<12} "
                f"rank={entry['rank']:2d}/{entry['rank_max']}  "
                f"wscore={entry['weighted_score']['score']:5.1f}  "
                f"piotr={entry['piotroski']['score']}/{entry['piotroski']['score_max']}({entry['piotroski']['label']:<8})  "
                f"zone={entry['zone']:<14}  "
                f"dy={entry['dy_real'] or '-':>6}%"
            )

    # Ordena por weighted_score decrescente (substitui rank simples)
    monitoring.sort(key=lambda x: x["weighted_score"], reverse=True)
    repo.save_monitoring_stocks(monitoring)

    success = len(monitoring)
    print(f"\nConcluído: {success}/{total} tickers qualificados → monitoring_stocks.json atualizado.")
    return results


if __name__ == "__main__":
    args = sys.argv[1:]
    if args:
        tickers_arg = [t.upper() for t in args]
        update_all(tickers=tickers_arg)
    else:
        update_all()
