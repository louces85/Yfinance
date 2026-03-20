"""
Busca de dados de Fluxo de Caixa para análise Buffett (Fase 2).

Obtém CapEx, D&A, FCO e Lucro Líquido via yfinance.cashflow e income_stmt,
calculando FCF, Owner Earnings e métricas de qualidade do caixa.

Chamado por history_fetcher.fetch_history() — não é um pipeline separado.

Nota de sinal: yfinance reporta Capital Expenditure como negativo (saída de caixa).
Todos os cálculos usam abs(capex) para manter o sinal correto.
"""

import math
import sys
import os

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
