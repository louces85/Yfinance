"""
Busca de dados de Fluxo de Caixa para análise Buffett (Fases 2 e 3).

Fase 2 — fetch_cashflow(): CapEx, D&A, FCO, FCF, Owner Earnings (ano mais recente).
Fase 3 — fetch_trends(): tendências históricas de 4 anos para 6 métricas chave.

Chamado por history_fetcher.fetch_history() — não é um pipeline separado.

Nota de sinal: yfinance reporta Capital Expenditure como negativo (saída de caixa).
Todos os cálculos usam abs(capex) para manter o sinal correto.
"""

import math
import sys
import os

import numpy as np

import yfinance

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import rules


def _safe_row(df, name: str):
    """
    Extrai o valor mais recente (.iloc[0]) de uma linha do DataFrame.
    Retorna None se a linha não existe, o valor é NaN ou não é numérico.
    """
    if df is None or df.empty:
        return None
    if name not in df.index:
        return None
    try:
        val = df.loc[name].iloc[0]
        if val is None:
            return None
        f = float(val)
        return None if math.isnan(f) else f
    except (TypeError, ValueError, IndexError):
        return None


def fetch_cashflow(ticker: str) -> dict:
    """
    Busca dados de Fluxo de Caixa e DRE histórica via yfinance.

    Retorna dict com cashflow_available=True e as métricas calculadas,
    ou {"cashflow_available": False} em caso de qualquer falha.

    Campos retornados (quando disponível):
        cashflow_available  : bool
        capex               : float  (negativo — saída de caixa)
        da                  : float  (D&A positivo)
        fco                 : float  (FCO positivo)
        net_income_cf       : float  (Lucro Líquido do DFC — validação cruzada)
        fcf                 : float  (= fco - abs(capex))
        owner_earnings      : float  (= net_income + da - abs(capex))
        fcf_lucro_ratio     : float  (= fcf / net_income; None se net_income <= 0)
        capex_lucro_ratio   : float  (= abs(capex) / net_income; None se net_income <= 0)
        fcf_positivo        : bool
        owner_earnings_positivo : bool
        fcf_quality_ok      : bool   (fcf_lucro_ratio >= BUFFETT_FCF_QUALITY_MIN)
        capex_moat_ok       : bool   (capex_lucro_ratio <= BUFFETT_CAPEX_MOAT_MAX)
    """
    try:
        yft = yfinance.Ticker(f"{ticker.upper()}.SA")
        cf  = yft.cashflow     # DFC anual (até 4 anos)
        inc = yft.income_stmt  # DRE anual (até 4 anos)

        capex      = _safe_row(cf,  "Capital Expenditure")
        da         = _safe_row(cf,  "Depreciation And Amortization")
        fco        = _safe_row(cf,  "Operating Cash Flow")
        net_income = _safe_row(inc, "Net Income")

        # FCF = FCO − |CapEx|
        fcf = None
        if fco is not None and capex is not None:
            fcf = fco - abs(capex)

        # Owner Earnings = Lucro Líquido + D&A − |CapEx|
        owner_earnings = None
        if net_income is not None and da is not None and capex is not None:
            owner_earnings = net_income + da - abs(capex)

        # Ratios — apenas quando lucro líquido é positivo
        fcf_lucro_ratio = None
        if fcf is not None and net_income is not None and net_income > 0:
            fcf_lucro_ratio = round(fcf / net_income, 4)

        capex_lucro_ratio = None
        if capex is not None and net_income is not None and net_income > 0:
            capex_lucro_ratio = round(abs(capex) / net_income, 4)

        return {
            "cashflow_available":       True,
            "capex":                    capex,
            "da":                       da,
            "fco":                      fco,
            "net_income_cf":            net_income,
            "fcf":                      fcf,
            "owner_earnings":           owner_earnings,
            "fcf_lucro_ratio":          fcf_lucro_ratio,
            "capex_lucro_ratio":        capex_lucro_ratio,
            "fcf_positivo":             fcf is not None and fcf > 0,
            "owner_earnings_positivo":  owner_earnings is not None and owner_earnings > 0,
            "fcf_quality_ok":           (
                fcf_lucro_ratio is not None
                and fcf_lucro_ratio >= rules.BUFFETT_FCF_QUALITY_MIN
            ),
            "capex_moat_ok":            (
                capex_lucro_ratio is not None
                and capex_lucro_ratio <= rules.BUFFETT_CAPEX_MOAT_MAX
            ),
        }

    except Exception:
        return {"cashflow_available": False}


# ---------------------------------------------------------------------------
# Fase 3 — Tendências Históricas (4 anos)
# ---------------------------------------------------------------------------

def _safe_series(df, name: str, n: int = 4) -> list:
    """
    Extrai lista com até `n` valores históricos de uma linha do DataFrame.
    Colunas do yfinance são ordenadas do mais recente ao mais antigo.
    Retorna lista de floats ou None por posição; lista vazia se linha ausente.
    """
    if df is None or df.empty or name not in df.index:
        return []
    result = []
    for i in range(min(n, len(df.columns))):
        try:
            val = df.loc[name].iloc[i]
            f = float(val)
            result.append(None if math.isnan(f) else f)
        except (TypeError, ValueError, IndexError):
            result.append(None)
    return result


def _calc_tendencia(valores: list, threshold_rel: float = 0.05) -> str:
    """
    Avalia a direção de uma série temporal (mais recente primeiro) via regressão linear.

    threshold_rel: variação mínima por ano relativa à média para classificar tendência.
                   Default 5% — abaixo disso classifica como ESTAVEL.

    Retorna: CRESCENDO, ESTAVEL ou CAINDO.
    """
    # filtra Nones mantendo posição temporal (mais recente primeiro → inverte para antigo→recente)
    pares = [(i, v) for i, v in enumerate(reversed(valores)) if v is not None]
    if len(pares) < 2:
        return "INDEFINIDO"

    xs = np.array([p[0] for p in pares], dtype=float)
    ys = np.array([p[1] for p in pares], dtype=float)

    slope = np.polyfit(xs, ys, 1)[0]
    mean_abs = np.mean(np.abs(ys))

    if mean_abs == 0:
        return "INDEFINIDO"

    rel_slope = slope / mean_abs

    if rel_slope > threshold_rel:
        return "CRESCENDO"
    if rel_slope < -threshold_rel:
        return "CAINDO"
    return "ESTAVEL"


def _extrair_anos(df, n: int = 4) -> list:
    """Extrai rótulos de ano das colunas do DataFrame (mais recente primeiro)."""
    if df is None or df.empty:
        return []
    anos = []
    for i in range(min(n, len(df.columns))):
        try:
            col = df.columns[i]
            anos.append(str(col.year))
        except (AttributeError, IndexError):
            anos.append(f"Ano{i+1}")
    return anos


def fetch_trends(ticker: str) -> dict:
    """
    Busca tendências históricas (até 4 anos) para análise Buffett Fase 3.

    Métricas calculadas ano a ano:
        margem_bruta      Gross Profit / Total Revenue  (%)
        margem_liquida    Net Income / Total Revenue     (%)
        roe               Net Income / Stockholders Equity (%)
        fcf               Operating Cash Flow - |CapEx|  (R$)
        divida_liquida    Net Debt do balanço            (R$)  [CAINDO = bom]
        capex_receita     |CapEx| / Total Revenue        (%)   [CAINDO = bom]

    Retorna dict com *_hist (lista) e *_trend (CRESCENDO/ESTAVEL/CAINDO/INDEFINIDO)
    mais recente primeiro. Em caso de falha retorna {"trends_available": False}.
    """
    try:
        yft = yfinance.Ticker(f"{ticker.upper()}.SA")
        cf  = yft.cashflow       # DFC anual
        inc = yft.income_stmt    # DRE anual
        bs  = yft.balance_sheet  # Balanço anual

        anos = _extrair_anos(inc)

        # --- séries brutas ---
        gross_profit = _safe_series(inc, "Gross Profit")
        revenue      = _safe_series(inc, "Total Revenue")
        net_income   = _safe_series(inc, "Net Income")
        sga_series   = _safe_series(inc, "Selling General And Administration")
        fco_series   = _safe_series(cf,  "Operating Cash Flow")
        capex_series = _safe_series(cf,  "Capital Expenditure")
        equity       = _safe_series(bs,  "Stockholders Equity")

        # Net Debt: tenta campo direto; fallback para Long Term Debt
        net_debt = _safe_series(bs, "Net Debt")
        if not any(v is not None for v in net_debt):
            net_debt = _safe_series(bs, "Long Term Debt")

        n = min(len(anos), 4)

        def _pct(num, den):
            """num/den * 100, com proteção contra zero e None."""
            if num is None or den is None or den == 0:
                return None
            return round(num / den * 100, 2)

        def _val(lst, i):
            return lst[i] if i < len(lst) else None

        # --- margem bruta ---
        mb_hist = [_pct(_val(gross_profit, i), _val(revenue, i)) for i in range(n)]

        # --- margem líquida ---
        ml_hist = [_pct(_val(net_income, i), _val(revenue, i)) for i in range(n)]

        # --- ROE ---
        roe_hist = [_pct(_val(net_income, i), _val(equity, i)) for i in range(n)]

        # --- FCF ---
        fcf_hist = []
        for i in range(n):
            fco_i   = _val(fco_series, i)
            capex_i = _val(capex_series, i)
            if fco_i is not None and capex_i is not None:
                fcf_hist.append(round(fco_i - abs(capex_i)))
            else:
                fcf_hist.append(None)

        # --- Dívida Líquida ---
        dl_hist = [
            round(_val(net_debt, i)) if _val(net_debt, i) is not None else None
            for i in range(n)
        ]

        # --- CapEx / Receita ---
        cr_hist = []
        for i in range(n):
            cx  = _val(capex_series, i)
            rev = _val(revenue, i)
            cr_hist.append(_pct(abs(cx) if cx is not None else None, rev))

        # --- SG&A / Receita (Buffett: ≤ 30% = moat forte) ---
        sga_hist = [
            _pct(abs(_val(sga_series, i)) if _val(sga_series, i) is not None else None, _val(revenue, i))
            for i in range(n)
        ]

        # --- tendências ---
        mb_trend   = _calc_tendencia(mb_hist)
        ml_trend   = _calc_tendencia(ml_hist)
        roe_trend  = _calc_tendencia(roe_hist)
        fcf_trend  = _calc_tendencia(fcf_hist)
        dl_trend   = _calc_tendencia(dl_hist)   # CAINDO = boa (menos dívida)
        cr_trend   = _calc_tendencia(cr_hist)   # CAINDO = boa (menos reinvestimento)
        sga_trend  = _calc_tendencia(sga_hist)  # CAINDO = boa (menos gasto com vendas/admin)

        if not anos:
            return {"trends_available": False}

        return {
            "trends_available":      True,
            "anos":                  anos,
            "margem_bruta_hist":     mb_hist,
            "margem_bruta_trend":    mb_trend,
            "margem_liquida_hist":   ml_hist,
            "margem_liquida_trend":  ml_trend,
            "roe_hist":              roe_hist,
            "roe_trend":             roe_trend,
            "fcf_hist":              fcf_hist,
            "fcf_trend":             fcf_trend,
            "divida_liq_hist":       dl_hist,
            "divida_trend":          dl_trend,
            "capex_receita_hist":    cr_hist,
            "capex_receita_trend":   cr_trend,
            "sga_receita_hist":      sga_hist,
            "sga_receita_trend":     sga_trend,
        }

    except Exception:
        return {"trends_available": False}
