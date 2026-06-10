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

# --- Buffett Moat: modificadores de tendência (Fase 3) ---
MOAT_TREND_PENALTY = -0.5  # critério aprovado + tendência CAINDO (moat erodindo)
MOAT_TREND_BONUS   =  0.5  # critério reprovado + tendência CRESCENDO (moat se construindo)

# --- Validade do ticker ---
# Número de falhas consecutivas antes de marcar como inválido
CONSECUTIVE_FAILURES_INVALID = 3
# Intervalo mínimo entre validações (em dias)
VALIDATION_INTERVAL_DAYS = 7
# Intervalo mínimo entre atualizações de preço (em horas)
PRICE_UPDATE_INTERVAL_HOURS = 0.5
# Intervalo mínimo entre atualizações de histórico (em dias)
HISTORY_UPDATE_INTERVAL_DAYS = 7

# --- Histórico de proventos (Carteira → Histórico) ---
DIVIDEND_MILESTONE_STEP      = 10000.0  # cada marco de proventos acumulados (R$)
FORECAST_WINDOW_SHORT_MONTHS = 6        # janela "otimista" p/ prever próximo marco
FORECAST_WINDOW_LONG_MONTHS  = 12       # janela "conservadora"

# --- DCF Buffett ---
DCF_DISCOUNT_RATE    = 0.10   # taxa mínima Buffett (independe da Selic)
DCF_TERMINAL_GROWTH  = 0.035  # crescimento perpétuo terminal (inflação + PIB longo prazo)
DCF_PROJECTION_YEARS = 10     # horizonte de projeção em anos
DCF_MOAT_CAP_FORTE    = 0.15  # crescimento máx. fase 1 — moat FORTE
DCF_MOAT_CAP_MODERADO = 0.10  # crescimento máx. fase 1 — moat MODERADO
DCF_MOAT_CAP_FRACO    = 0.05  # crescimento máx. fase 1 — moat FRACO

# --- Demonstrativos Financeiros Históricos ---
# Intervalo mínimo entre atualizações (demonstrativos são anuais — 30 dias é suficiente)
FINANCIALS_UPDATE_INTERVAL_DAYS = 30
# Quantidade de anos de histórico a buscar no StatusInvest
FINANCIALS_YEARS = 10

# --- Swing Trade: indicadores e setups ---
RSI_OVERSOLD             = 30     # RSI abaixo disso = sobrevenda (reversão)
PULLBACK_RSI_LO          = 35     # faixa de recuo saudável (pullback) — mínimo
PULLBACK_RSI_HI          = 50     # faixa de recuo saudável (pullback) — máximo
PULLBACK_RECENT_LOOKBACK = 5      # janela p/ detectar recuo/gatilho do pullback
REVERSAL_RECENT_LOOKBACK = 3      # janela p/ sobrevenda + reconquista (reversão)
BREAKOUT_LOOKBACK        = 20     # nº de pregões da resistência rompida
SWING_LOW_LOOKBACK       = 10     # fundo recente p/ stop estrutural
PULLBACK_TARGET_LOOKBACK = 30     # máxima anterior usada como alvo do pullback
MA50_SLOPE_LOOKBACK      = 10     # pregões p/ medir inclinação da MA50
PRICE_AVG_SHORT_DAYS     = 21     # média de preço/volume de 1 mês (pregões)
PRICE_AVG_MID_DAYS       = 63     # média de preço/volume de 3 meses (pregões)
PRICE_AVG_LONG_DAYS      = 126    # média de preço de 6 meses (pregões)
VOL_SURGE_MULT           = 1.5    # volume > mult × média(20) = confirmação
RR_MIN                   = 1.5    # R:R mínimo p/ qualificar como setup
RR_STRONG                = 2.0    # R:R a partir do qual a nota ganha bônus cheio
ATR_STOP_MIN             = 1.0    # distância mínima do stop em múltiplos de ATR
ATR_STOP_MAX             = 3.0    # distância máxima do stop em múltiplos de ATR
ATR_TARGET_MAX           = 3.0    # teto do alvo em múltiplos de ATR
ATR_PCT_MIN              = 0.005  # piso de volatilidade: ATR/preço mínimo (0,5%) p/ o
                                  # setup ser tradável — descarta papéis quase-planos/ilíquidos
# Pesos do score de qualidade (0–100) e cortes de nota
W_TREND_ALTA             = 30
W_TREND_LATERAL          = 12
W_TRIGGER_PER            = 8      # por motivo de gatilho (cap 3)
W_VOLUME                 = 15
W_RR_HIGH                = 20     # R:R >= RR_STRONG
W_RR_OK                  = 10     # RR_MIN <= R:R < RR_STRONG
W_BELOW_AVG_PER          = 4      # por média (1m/3m/6m) que o preço está abaixo — máx. 12;
                                  # só Pullback/Reversão (Rompimento está acima por natureza)
W_VOL_RISING             = 8      # volume médio 1m > volume médio 3m (acumulação) — todos os setups
GRADE_A                  = 70     # score >= 70 → nota A
GRADE_B                  = 50     # score >= 50 → nota B (senão C)

# --- Diário de operações de swing: controle de DARF ---
# Swing trade comum (mercado à vista): vendas de ações até este limite no mês
# são ISENTAS de IR. Acima disso, o lucro é tributado em 15%.
SWING_DARF_MONTHLY_LIMIT = 20000.0  # limite de isenção mensal (R$)
SWING_DARF_WARN_RATIO    = 0.9      # alerta a partir de 90% do limite (R$ 18.000)
