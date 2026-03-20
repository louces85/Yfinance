"""
Thresholds e regras de valuation.
Baseado em Barsi, Bazin, Graham, Greenblatt e Lynch.
"""

# --- Barsi / Bazin ---
# Taxa de retorno mínima esperada via dividendos (6% = compra moderada)
BASIN_BASE    = 0.06   # yield-alvo base (compra moderada)
BASIN_MIN     = 0.05   # yield-alvo mínimo (só monitorar)
BASIN_MAX     = 0.08   # yield-alvo agressivo (compra forte)

DIVIDEND_YIELD_MIN    = 6.0   # DY% mínimo para aprovação
PAYOUT_MIN            = 40.0  # Payout% mínimo saudável (Bazin)
PAYOUT_MAX            = 80.0  # Payout% máximo saudável (Bazin)
DIVIDEND_YEARS_MIN    = 5     # Anos consecutivos mínimos com dividendos

# --- Graham ---
P_L_MAX       = 15.0   # P/L máximo
P_VP_MAX      = 1.5    # P/VP máximo
GRAHAM_COMBO  = 22.5   # P/L × P/VP máximo (regra combinada Graham)
LIQUIDEZ_CORRENTE_MIN = 2.0   # Liquidez corrente mínima (Graham: >= 2.0)

# --- Dívida ---
DL_PL_MAX     = 1.0    # Dívida Líquida / Patrimônio Líquido máximo
DL_EBITDA_MAX = 3.0    # Dívida Líquida / EBITDA máximo
PASSIVO_ATIVO_MAX = 0.65  # Passivo / Ativo máximo (não-financeiras; Graham ~0.6)
FINANCIAL_PL_ATIVO_MAX = 0.20  # Proxy setor financeiro: PL/Ativo <= 20% → banco/seguradora

# --- Rentabilidade ---
MARGEM_EBIT_MIN   = 10.0   # Margem EBIT mínima (%)
MARGEM_LIQ_MIN    = 10.0   # Margem Líquida mínima (%)
ROE_MIN           = 10.0   # ROE mínimo (%)
ROIC_MIN          = 10.0   # ROIC mínimo (%)

# --- Crescimento ---
CAGR_RECEITA_MIN  = 5.0    # CAGR Receita 5 anos mínimo (%)
CAGR_LUCRO_MIN    = 5.0    # CAGR Lucro 5 anos mínimo (%)

# --- Barsi: acumulação silenciosa ---
ACCUMULATION_SCORE_MIN = 50.0  # % mínimo de dias com preço E volume abaixo da média

# --- Lynch (PEG) ---
PEG_MAX       = 1.0    # PEG ajustado por dividendos máximo

# --- Liquidez de mercado ---
LIQUIDEZ_DIARIA_MIN = 200000.0  # R$ 200k/dia mínimo

# --- Score Ponderado ---
# Pesos por critério: qualidade > crescimento > dívida > preço > dividendos > técnico
# Total máximo: 40 pontos → normalizado para 0-100
WEIGHTED_SCORE_WEIGHTS = {
    # Qualidade/Rentabilidade (peso 3) — maior impacto no score
    "roe_ok":                 3.0,
    "roic_ok":                3.0,
    "margem_ebit_ok":         3.0,
    "margem_liq_ok":          3.0,
    # Crescimento (peso 2)
    "cagr_receita_ok":        2.0,
    "cagr_lucro_ok":          2.0,
    "dividendo_crescente_ok": 2.0,
    # Dívida/Segurança (peso 2)
    "dl_pl_ok":               2.0,
    "dl_ebitda_ok":           2.0,
    "passivo_ativo_ok":       2.0,
    "liquidez_corrente_ok":   2.0,
    # Preço/Valuation (peso 1.5)
    "p_l_ok":                 1.5,
    "p_vp_ok":                1.5,
    "graham_combo_ok":        1.5,
    "abaixo_vpa":             1.5,
    # Dividendos/Renda (peso 1.5)
    "dy_ok":                  1.5,
    "abaixo_target_6pct":     1.5,
    "abaixo_target_8pct":     1.5,
    "payout_ok":              1.5,
    # Técnico/Liquidez (peso 1)
    "liquidez_diaria_ok":     1.0,
    "accumulation_ok":        1.0,
}
WEIGHTED_SCORE_MAX = sum(WEIGHTED_SCORE_WEIGHTS.values())  # 40.0

# --- Piotroski F-Score (adaptado) ---
# 9 sinais de saúde financeira — adaptados aos dados disponíveis (sem balanço histórico)
PIOTROSKI_STRONG_MIN          = 7     # >= 7 = empresa financeiramente forte
PIOTROSKI_MODERATE_MIN        = 4     # 4–6 = saúde moderada
PIOTROSKI_ROE_FORTE           = 15.0  # ROE forte (sinal P9): acima do mínimo básico
PIOTROSKI_DL_PL_CONSERVADOR   = 0.5   # Alavancagem conservadora (sinal P4): metade do limite principal
PIOTROSKI_LIQ_CORRENTE_MIN    = 1.5   # Liq. corrente mínima (sinal P5): entre Graham (2.0) e zero
PIOTROSKI_PASSIVO_ATIVO_MAX   = 0.4   # Balanço conservador (sinal P6): abaixo de 40%

# --- Buffett Cashflow (Fase 2) ---
BUFFETT_FCF_QUALITY_MIN = 0.80   # FCF/Lucro mínimo (lucro de alta qualidade)
BUFFETT_CAPEX_MOAT_MAX  = 0.25   # CapEx/Lucro máximo (moat — baixo reinvestimento)

# --- Validade do ticker ---
# Número de falhas consecutivas antes de marcar como inválido
CONSECUTIVE_FAILURES_INVALID = 3
# Intervalo mínimo entre validações (em dias)
VALIDATION_INTERVAL_DAYS = 7
# Intervalo mínimo entre atualizações de preço (em horas)
PRICE_UPDATE_INTERVAL_HOURS = 0.5
# Intervalo mínimo entre atualizações de histórico (em dias)
HISTORY_UPDATE_INTERVAL_DAYS = 7
