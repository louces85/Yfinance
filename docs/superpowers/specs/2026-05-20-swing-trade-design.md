# Aba Swing Trade — Design Spec

**Data:** 2026-05-20  
**Branch:** decision-making-improvements  
**Status:** Aprovado

---

## Visão Geral

Nova aba "Swing" na navegação principal (ao lado de Radar), voltada para identificação de oportunidades de swing trade nos ~127 ativos já monitorados pelo Screening. A aba aplica 4 indicadores técnicos sobre o histórico OHLCV existente e exibe os ativos que têm ≥ 2 indicadores disparados simultaneamente como **SETUP**.

Sem rastreamento de trades. Sem watchlist separada. Só identificação de setups.

---

## Estratégia

**Perfil:** Indicadores técnicos puros — sem filtro de fundamentals para elegibilidade.

**Universo:** Todos os ~127 tickers de `decision_stocks.json`. O histórico OHLCV (6 meses) já está disponível via `stock_history.json`.

**Threshold de SETUP:** ≥ 2 dos 4 indicadores disparados ao mesmo tempo.

---

## Indicadores

| # | Indicador | Parâmetros | Sinal = `True` quando |
|---|-----------|-----------|----------------------|
| 1 | RSI | Período 14, sobre fechamentos | RSI < 30 |
| 2 | MACD | EMA 12/26, sinal 9 | Linha MACD cruzou linha de sinal para cima nos últimos 3 dias |
| 3 | Bollinger Bands | Período 20, 2σ | Preço ≤ banda inferior |
| 4 | MA Cross | SMA20 vs SMA50 | SMA20 > SMA50 (Golden Cross ativo) |

---

## Backend

### swing_service.py (novo)

Responsabilidades:
- Lê `stock_history.json` via `stock_repository`
- Para cada ticker, calcula RSI, MACD, BB e MA Cross sobre os fechamentos
- Marca `signals_count` (0–4) e `is_setup = signals_count >= 2`
- Salva resultado em `swing_data.json` via atomic write (`stock_repository`)

Sem dependência de `all_indicators.json` nem `valuation_calculator`. Apenas math sobre séries de preço.

### Integração no scheduler

Em `api_server.py`, o ciclo de 30 min que já chama `decision_service.run()` passa a chamar também `swing_service.run()` na mesma thread.

### Endpoint

```
GET /api/swing
```
Retorna o conteúdo de `swing_data.json` como JSON array.

### Estrutura de swing_data.json

```json
[
  {
    "ticker": "BBAS3",
    "price": 24.50,
    "rsi": 27.4,
    "rsi_signal": true,
    "macd_value": -0.12,
    "macd_signal_line": -0.18,
    "macd_bullish": true,
    "bb_upper": 27.5,
    "bb_middle": 25.0,
    "bb_lower": 22.3,
    "bb_signal": true,
    "ma20": 24.2,
    "ma50": 25.8,
    "ma_signal": false,
    "signals_count": 3,
    "is_setup": true,
    "updated_at": "2026-05-20T10:30:00"
  }
]
```

---

## Frontend

### Navegação

Novo botão de tab adicionado ao `div.tab-group` em `index.html`, após o botão "Radar":

```html
<button class="tab-btn" data-tab="swing">Swing</button>
```

Cor de destaque verde (mesma lógica do tab ativo existente).

### Toolbar

- 3 cards de resumo: **SETUPs ativos** (verde) / **Monitorar** (amarelo, 1 sinal) / **Analisados** (azul, total)
- Toggle "Só SETUPs" — padrão **ligado**, esconde tickers com `signals_count < 2`
- Label de atualização: "Atualizado: HH:MM · próximo em 30 min"

### Tabela

| Coluna | Dado | Ordenável |
|--------|------|-----------|
| Ativo | `ticker` (clicável, abre modal) | sim |
| Preço (R$) | `price` | sim |
| RSI (14) | `rsi` — verde se < 30 | sim |
| MACD | badge `↑ Bull` / `↓ Bear` baseado em `macd_bullish` | não |
| Bollinger | badge `≤ Inf` / `Normal` baseado em `bb_signal` | não |
| MA Cross | badge `Golden` / `Death` baseado em `ma_signal` | não |
| Sinais | barra de 4 dots (verde/cinza) + contador `X/4` | sim (default DESC) |
| Status | badge `SETUP` (verde) ou `–` | não |

**Ordenação padrão:** `signals_count` DESC.

**Linhas de SETUP** recebem fundo verde sutil `rgba(63,185,80,.04)`.

### Clique na linha / ticker

Chama `openDetail(ticker)` — abre o modal existente idêntico ao do Screening e Carteira (gráfico preço+volume, cards de preço, VI, Margem de Segurança, ranking no setor, Buffett Moat). Zero código novo no modal.

---

## Arquivos afetados

| Arquivo | Mudança |
|---------|---------|
| `src/backend/services/swing_service.py` | **novo** |
| `src/backend/data/swing_data.json` | **novo** (gerado pelo serviço) |
| `src/backend/api_server.py` | adicionar endpoint `/api/swing` + chamar `swing_service.run()` no scheduler |
| `src/backend/repositories/stock_repository.py` | adicionar `save_swing_data()` e `load_swing_data()` |
| `src/frontend/index.html` | novo tab button, novo painel, nova tabela, lógica de renderização |

---

## Fora de escopo

- Rastreamento de trades (entrada, saída, resultado)
- Watchlist própria para swing (tickers fora do Screening)
- Backtesting dos indicadores
- Configuração de parâmetros pelo usuário (períodos, thresholds)
- Notificações push quando um setup aparece
