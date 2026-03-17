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
DIVIDEND_YEARS_MIN    = 4     # Anos consecutivos mínimos com dividendos

# --- Graham ---
P_L_MAX       = 15.0   # P/L máximo
P_VP_MAX      = 1.5    # P/VP máximo
GRAHAM_COMBO  = 22.5   # P/L × P/VP máximo (regra combinada Graham)
LIQUIDEZ_CORRENTE_MIN = 2.0   # Liquidez corrente mínima (Graham: >= 2.0)

# --- Dívida ---
DL_PL_MAX     = 1.0    # Dívida Líquida / Patrimônio Líquido máximo
DL_EBITDA_MAX = 3.0    # Dívida Líquida / EBITDA máximo
PASSIVO_ATIVO_MAX = 1.0  # Passivo / Ativo máximo

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

# --- Validade do ticker ---
# Número de falhas consecutivas antes de marcar como inválido
CONSECUTIVE_FAILURES_INVALID = 3
# Intervalo mínimo entre validações (em dias)
VALIDATION_INTERVAL_DAYS = 7
# Intervalo mínimo entre atualizações de preço (em horas)
PRICE_UPDATE_INTERVAL_HOURS = 0.5
# Intervalo mínimo entre atualizações de histórico (em dias)
HISTORY_UPDATE_INTERVAL_DAYS = 7
