# Swing Tab Rework — Design Spec

**Data:** 2026-06-01
**Status:** Aprovado (pendente revisão final do usuário)
**Substitui:** a lógica de score do swing descrita em `2026-05-20-swing-trade-design.md` e `brain_calculations.md §7.12`.

## Problema

A aba de swing atual soma 4 indicadores booleanos (RSI<30, MACD bullish, preço ≤ banda inferior, MA20>MA50) e marca `is_setup` quando `signals_count ≥ 2`.

O defeito central: os 4 indicadores pertencem a **duas escolas opostas** —
RSI<30 e banda inferior são sinais de **reversão** (preço caindo); MACD>signal e MA20>MA50 são sinais de **tendência** (preço subindo). Um ativo quase nunca tem os 4 juntos, então quase todo "SETUP" é exatamente 2 sinais que caem num de dois baldes incompatíveis:

- `{RSI<30 + banda inferior}` → ativo em queda, momento bearish → **pegar faca caindo**
- `{MACD bull + MA20>MA50}` → ativo em alta sem pullback → **compra esticado**

Ambos marcam "SETUP" idêntico, mas são situações opostas e medíocres. Somar dilui o sinal. Além disso o modelo só mede **estado** (nunca gatilho/virada), não tem filtro de tendência maior, não tem moldura de risco (entrada/stop/alvo/R:R), ignora volume, e nunca foi validado.

## Objetivo

Tornar a aba mais **acertiva** (maior taxa de acerto, menos falsos positivos) e **acionável**: cada oportunidade vira um setup nomeado, com gatilho real, filtrado por tendência, com níveis de risco e nota de qualidade.

Escopo: **long-only** (coerente com o perfil fundamentalista Barsi/Bazin/Graham do projeto).

## Dados de base

- Fetch estende de `6mo` → **`1y`** por ticker (mesmo universo: ~127 de `monitoring_stocks.json`).
- Passa a guardar **High / Low / Volume** (hoje só usa Close), necessários para ATR e confirmação de volume.
- Por pregão calcula-se: RSI(14), MACD(12,26,9) com histograma, BB(20,2σ), SMA20/50/**200**, **ATR(14)**, média de volume(20).

### Contexto de tendência (gate dos setups)

- `tendência = ALTA` se `close > MA50 > MA200` **e** MA50 subindo (`MA50_hoje > MA50_há_~10_pregões`)
- `tendência = BAIXA` se `close < MA200` **e** MA50 caindo
- `tendência = LATERAL` caso contrário
- `vol_confirm = volume_hoje > VOL_SURGE_MULT × média_vol(20)` (default 1,5)

## Os 3 setups (long-only)

### 1. Pullback em tendência de alta *(maior confiabilidade)*
- **Filtro:** tendência = ALTA
- **Recuo:** RSI esteve na faixa `PULLBACK_RSI_LO`–`PULLBACK_RSI_HI` (default 35–50) nos últimos ~5 pregões, **ou** preço tocou MA20 / banda-média
- **Gatilho (virada):** RSI virando pra cima (`rsi[-1] > rsi[-2]`) **ou** histograma MACD subindo (`hist[-1] > hist[-2]`) **ou** candle repicando do suporte (`close[-1] > close[-2]` após o recuo)
- Sem gatilho de virada → **não dispara** (não compra "ainda caindo")

### 2. Reversão de sobrevenda *(menor probabilidade)*
- **Gate:** tendência ≠ BAIXA (evita faca caindo em downtrend estrutural)
- **Condição:** RSI esteve `< RSI_OVERSOLD` (default 30) nos últimos ~3 pregões **e** virando pra cima
- **Confirmação:** preço **reconquistou** a banda inferior (`close[-1] > bb_lower` após ter tocado/rompido recentemente)
- `vol_confirm` eleva a nota (não é obrigatório)

### 3. Rompimento / continuação
- **Filtro:** `close > MA50` (não bearish)
- **Condição:** fechamento rompe a máxima dos últimos `BREAKOUT_LOOKBACK` (default 20) pregões (resistência da consolidação)
- **Confirmação de volume obrigatória** (`vol_confirm`) — rompimento sem volume = armadilha → **não dispara**

### Precedência
Quando um ticker casa em mais de um setup: fica com a **maior nota**; empate segue ordem de confiabilidade **Pullback → Rompimento → Reversão**. **Um setup por ticker.**

## Modelo de risco (híbrido estrutura + ATR)

Entrada = fechamento atual.

**Stop** — fundo da estrutura com piso/teto de ATR:
- Base: menor mínima dos últimos `SWING_LOW_LOOKBACK` (default 10) pregões.
- Clamp: stop fica **no mínimo `ATR_STOP_MIN`×ATR** (default 1,0) e **no máximo `ATR_STOP_MAX`×ATR** (default 3,0) abaixo da entrada.

**Alvo** — por tipo de setup:
| Setup | Alvo |
|-------|------|
| Pullback | máxima anterior ao recuo (retomada da tendência) |
| Reversão | banda-média ou MA50, o que vier antes |
| Rompimento | *measured move*: entrada + altura da consolidação rompida (teto de `ATR_TARGET_MAX`×ATR, default 3,0) |

**R:R** = `(alvo − entrada) / (entrada − stop)`

**Gate de qualificação:** um ticker que casa um setup mas tem `rr < RR_MIN` (default 1,5) **não** vira setup — recebe `setup_type` preenchido mas `is_setup = false` e entra na contagem **"Monitorar"** (casou a forma, faltou risco/retorno). Tickers que não casam nenhum setup ficam fora (nem Monitorar).

## Nota A / B / C

Score composto (0–100) ponderando fatores que aumentam a taxa de acerto:

| Fator | Peso | Racional |
|-------|------|----------|
| Alinhamento de tendência (ALTA plena) | alto | setup a favor da tendência maior acerta mais |
| Frescor do gatilho (virada/cruzamento nos últimos 1–2 pregões) | alto | evento recente > estado antigo |
| Confirmação por volume | médio | reversão/rompimento com volume é mais confiável |
| Magnitude do R:R (≥2 melhor) | médio | retorno assimétrico |
| Profundidade/qualidade do sinal (ex.: RSI 18 vs 29) | baixo | desempate |

Mapeamento → **A** (`score ≥ GRADE_A`), **B** (`score ≥ GRADE_B`), **C** (qualificou no limite). Pesos e cortes em `rules.py`.

**Ordenação da tabela:** por `score` desc; `rr` como desempate.

## Thresholds (todos em `config/rules.py`)

Nenhum valor hardcoded em `swing_service.py`. Constantes nomeadas, ex.:
`RSI_OVERSOLD=30`, `PULLBACK_RSI_LO=35`, `PULLBACK_RSI_HI=50`, `BREAKOUT_LOOKBACK=20`,
`SWING_LOW_LOOKBACK=10`, `VOL_SURGE_MULT=1.5`, `RR_MIN=1.5`,
`ATR_STOP_MIN=1.0`, `ATR_STOP_MAX=3.0`, `ATR_TARGET_MAX=3.0`,
`MA50_SLOPE_LOOKBACK=10`, `GRADE_A`, `GRADE_B`, pesos do score.

## Schema do `swing_data.json` (novo)

```json
{
  "ticker":      "PRIO3",
  "price":       38.20,
  "setup_type":  "PULLBACK",
  "grade":       "A",
  "score":       82,
  "trend":       "ALTA",
  "trigger":     "RSI virando + repique MA20",
  "entry":       38.20,
  "stop":        35.90,
  "target":      43.00,
  "rr":          2.1,
  "vol_confirm": true,
  "is_setup":    true,
  "rsi":         41.3,
  "updated_at":  "2026-06-01T18:00:00"
}
```

- `setup_type`: `PULLBACK | REVERSAL | BREAKOUT | null`
- `grade`: `A | B | C` quando `is_setup`; `null` quando apenas Monitorar (casou setup mas `rr < RR_MIN`)
- `trend`: `ALTA | LATERAL | BAIXA`
- `is_setup`: casou um setup **e** `rr ≥ RR_MIN`. Quando `false` mas `setup_type != null` → conta como "Monitorar"
- Indicadores crus completos (MACD/BB/MAs/séries) **saem do JSON da tabela**; continuam disponíveis ao vivo via `GET /api/swing/chart/<ticker>` (modal de gráfico — inalterado).

## Backend — `swing_service.py`

Mantém o estilo "funções puras `calc_*` + `run()`". Acrescenta:
- `calc_atr(highs, lows, closes, period=14)` — True Range / Wilder smoothing
- `calc_ma(closes, 200)` e helper de inclinação da MA50
- `classify_trend(...)` → ALTA/LATERAL/BAIXA
- `detect_pullback(...)`, `detect_reversal(...)`, `detect_breakout(...)` — cada um retorna match + trigger text + vol_confirm
- `calc_levels(setup_type, ...)` → entry/stop/target/rr (com clamps de ATR)
- `grade_setup(...)` → score + grade
- `run()` orquestra: baixa 1y (High/Low/Close/Volume), calcula indicadores, roda os 3 detectores, escolhe o melhor setup por ticker (precedência), filtra `rr ≥ RR_MIN`, ordena por score desc, salva via `repo.save_swing_data`.

`stock_repository.save_swing_data` / `get_swing_data` não mudam de assinatura (continuam salvando/lendo a lista de dicts).

## Frontend — `index.html`

**Tabela** (`renderSwingTable()`) → colunas acionáveis:

`Ativo | Preço | Setup | Nota | Gatilho | Entrada | Stop | Alvo | R:R`

- **Setup:** badge por tipo (Pullback↑ / Reversão / Rompimento), clicável → `openSwingChart()` com `event.stopPropagation()` (mantém padrão atual).
- **Nota:** A/B/C com cor (A verde, B amarelo, C cinza).
- Ordenável por `score`, `rr`, `price` (reusa `_swingSort`).
- Linha clicável abre o detalhe da ação (inalterado).

**Cards do toolbar:** `Setups (A/B)` · `Monitorar` · `Analisados`. Filtro "Só SETUPs" mantido.

**Modal de gráfico:** estrutura inalterada; ganha uma faixa no topo com setup/nota/entrada/stop/alvo/R:R.

## Testes (TDD — funções puras)

Séries sintéticas, no padrão do plano original de swing (Task 2):
- `calc_atr` em série conhecida
- Cada detector: caso que dispara + caso de borda que **não** dispara (pullback sem virada; rompimento sem volume; reversão em downtrend)
- `calc_levels`: clamp do stop por ATR, R:R correto
- `grade_setup`: A/B/C nos cortes
- `classify_trend`: ALTA/LATERAL/BAIXA

Sem teste de rede (yfinance fora; `run()` via smoke manual).

## Documentação

Atualizar `brain_calculations.md §7.12` (nova lógica de setups, risco e nota) e `brain_frontend.md §9.5` (novas colunas e cards). Atualizar o schema documentado do `swing_data.json`.

## Fora de escopo (follow-up recomendado)

**Backtest de validação** — medir hit-rate / R médio dos setups sobre o histórico já baixado. É o único caminho para *comprovar* a assertividade com números, e fica como próximo passo após o rework.
