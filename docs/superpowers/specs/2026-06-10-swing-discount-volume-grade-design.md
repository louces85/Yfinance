# Swing — Desconto vs. médias e volume crescente na nota A/B/C

**Data:** 2026-06-10
**Objetivo:** tornar a nota A/B/C da aba Swing mais assertiva, pontuando setups em que o
preço está descontado em relação às médias de 1m/3m/6m e em que há volume crescente
(acumulação). Decisão do usuário: os fatores agem **apenas como peso na nota** — não são
gate, não criam colunas novas e não alteram detecção/níveis de risco.

## Contexto

Hoje (`swing_service.py`) o score da nota pondera: tendência (30/12/0), motivos de
gatilho (8 × cap 3), volume do dia (`vol_confirm`, 15) e R:R (20/10) — máx. 89. Não há
nenhum fator de "preço descontado". O modal de detalhe já exibe média 6m
(`close_avg_6m` via `history_fetcher.py`), o que motivou o pedido; no swing o cálculo é
feito localmente, pois o serviço já baixa 1 ano de OHLCV diário.

## Mudanças

### 1. `build_context()` — novos indicadores

- `avg_1m` = `calc_sma(closes, PRICE_AVG_SHORT_DAYS)` (21 pregões)
- `avg_3m` = `calc_sma(closes, PRICE_AVG_MID_DAYS)` (63 pregões)
- `avg_6m` = `calc_sma(closes, PRICE_AVG_LONG_DAYS)` (126 pregões)
- `below_avg_count` (int 0–3): quantas das médias **disponíveis** o último fechamento
  está estritamente abaixo. O universo exige ≥ 60 closes, então 1m/3m sempre existem;
  se `avg_6m` for `None` (histórico curto), ela simplesmente não conta — sem penalidade.
- `vol_rising` (bool): `calc_avg_volume(volumes, 21) > calc_avg_volume(volumes, 63)`.
  `None`-safe: qualquer média indisponível ⇒ `False`.

### 2. `rules.py` — constantes novas (nunca hardcode)

| Constante | Valor | Significado |
|-----------|-------|-------------|
| `PRICE_AVG_SHORT_DAYS` | 21 | média de 1 mês em pregões |
| `PRICE_AVG_MID_DAYS` | 63 | média de 3 meses em pregões |
| `PRICE_AVG_LONG_DAYS` | 126 | média de 6 meses em pregões |
| `W_BELOW_AVG_PER` | 4 | pontos por média que o preço está abaixo (máx. 12) |
| `W_VOL_RISING` | 8 | pontos se volume médio 1m > volume médio 3m |

### 3. `grade_setup()` — novos pesos

- Assinatura muda para `grade_setup(setup, levels, ctx)` — `trend`, `below_avg_count`
  e `vol_rising` saem do `ctx` (testes existentes da função são ajustados).
- **Desconto** (`below_avg_count × W_BELOW_AVG_PER`): aplica-se **somente** a
  `PULLBACK` e `REVERSAL`. `BREAKOUT` não recebe — rompimento está acima das médias
  por natureza do setup e seria punido injustamente.
- **Volume crescente** (`W_VOL_RISING`): aplica-se a **todos** os setups — acumulação
  também confirma rompimento.
- Score continua clampado em 100. Cortes `GRADE_A = 70` / `GRADE_B = 50` **mantidos**:
  hoje nenhum setup alcança A, então os fatores novos criam diferenciação real, não
  inflação. Recalibração dos cortes fica para quando houver feedback de acerto.

### 4. Schema `swing_data.json`

Dois campos novos em **toda** entrada (com ou sem setup), como `rsi`/`vol_confirm`:

- `below_avgs` (int 0–3)
- `vol_rising` (bool)

Frontend não muda nesta entrega; os campos ficam disponíveis para uso futuro
(coluna/tooltip).

### 5. Fora do escopo (intocados)

Detectores, `calc_levels` (stop/alvo/R:R), `RR_MIN`, piso de volatilidade
(`ATR_PCT_MIN`), precedência `_pick_best_setup`, frontend, diário de operações.

## Testes

- `below_avg_count`: 0, parcial, 3; histórico < 126 closes (6m indisponível não conta).
- `vol_rising`: crescente, decrescente, volume insuficiente (`None` ⇒ `False`).
- `grade_setup`: pullback/reversão recebem desconto, breakout não; `vol_rising`
  pontua em todos; clamp em 100; notas A/B/C nos novos limiares de score.
- Regerar `swing_data.json` ao final e conferir os campos novos no JSON.

## Documentação

Atualizar `src/brain/brain_calculations.md`: §7.12.1 (indicadores base), §7.12.5
(nota), §7.12.7 (schema) e a tabela "Swing Trade — Setups, Risco e Nota".

## Efeito esperado (dados de 2026-06-10)

ABEV3/GOAU3 (Pullback B, score 64–66) sobem para A (≥ 70) se descontados e com volume
crescente; CLSC4/UGPA3 (Reversão C, 48) podem chegar a B. Nenhum sinal some — só a
classificação muda.

## Restrições técnicas

- Python 3.8 (sem walrus, sem f-string complexa).
- Persistência sempre via `stock_repository.py` (já é o caso — `save_swing_data`).
