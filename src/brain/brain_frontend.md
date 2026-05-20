# Brain YFinance — Páginas, Fontes de Dados e Limitações

> Parte 4/4 do brain. Para filosofias → `brain_overview.md`. Para arquitetura/código → `brain_architecture.md`. Para cálculos/fórmulas → `brain_calculations.md`.

---

## 9. Páginas da Aplicação

### 9.0 Header — Barra de Navegação Global

Sempre visível no topo. Da esquerda para a direita:

```
[ ⬡ YFINANCE ]  [ Screening | Carteira | Favoritos | Radar | Swing ]  [ Market Bar ]  [ Atualizado: HH:MM ]  [ 🔔 ]
```

**Market Bar (`#mktBar`)** — exibe 4 índices de mercado atualizados a cada 30 min:

| Índice | Formato | Fonte |
|--------|---------|-------|
| IBOV | `137.420 pts` | `^BVSP` via yfinance |
| USD | `R$ 5,12` | `BRL=X` via yfinance |
| S&P | `5.234 pts` | `^GSPC` via yfinance |
| OURO | `US$ 2.320/oz` | `GC=F` via yfinance |

Cada item mostra: label / valor / variação % do dia (verde se positiva, vermelho se negativa).

**Atualização no frontend:** carregado em `loadDecision()` via `loadMarket() → GET /api/market` e também atualizado no `silentRefresh()` a cada ciclo.

---

### 9.1 Screening — Tela Principal

**Propósito:** Visão completa de todos os ativos monitorados, ranqueados e filtrados.

**Ordenação padrão:** `p_now_p_min` ASC — ações mais próximas do suporte de 6 meses aparecem primeiro.

**Colunas:**

| Coluna | Campo JSON | Descrição |
|--------|-----------|-----------|
| `#` | índice | Posição no ranking |
| `Ativo` | `ticker` | Ticker com ícones de medalhas e selos |
| `Preço (R$)` | `price_now` | Preço atual (Google Finance, cache 30 min) |
| `Alvo Bazin (R$)` | `price_target_6pct` | Preço justo pelo critério Bazin 6% |
| `Potencial (%)` | `gain_pct` | Upside até o alvo Bazin |
| `Mín. 6m (R$)` | `price_min_6m` | Mínimo de preço dos últimos 6 meses |
| `Máx. 6m (R$)` | `price_max_6m` | Máximo de preço dos últimos 6 meses |
| `Dist. Mín.` | `p_now_p_min` | Razão preço atual / mínimo 6m (barra colorida) |
| `Score` | `weighted_score` | Score ponderado 0-100 (21 critérios binários) |
| `BRank` | `unified_rank` | Ranking Unificado Buffett×Barsi×Bazin 0-100 |
| `MOAT` | `buffett_moat_score` | Score Buffett Moat 0-10 |
| `Saúde` | `piotroski_score` | Piotroski F-Score 0-9 |
| `FCF/L` | `fcf_lucro_ratio` | FCF / Lucro Líquido (qualidade) |
| `Acum. 6m (%)` | `accumulation_score` | % dias em acumulação Barsi |
| `Acum. 30d` | `accumulation_30d_days` | Dias de acumulação último mês |
| `Sinal` | `zone` | Badge colorido: COMPRA_FORTE / COMPRA / MONITORAR / CARO |

**Filtros disponíveis:**

| Filtro | Ação |
|--------|-----|
| Por zona | FORTE / COMPRA / AGUARDAR / ACIMA (clique nos cards) |
| Ocultar CARO | Toggle padrão ativo |
| 🥇 Gold Only | Apenas medalha ouro |
| 🥈 Silver Only | Apenas abaixo VPA + alvo |
| 🥉 Bronze Only | Apenas abaixo do alvo (acima VPA) |
| ★ Buffett | Apenas com Selo Buffett |
| BEST | Apenas setores Barsi |

**Barra de resumo:** 10 cards clicáveis (total, zonas, medalhas, BEST).

**Sort:** clique nos headers (`data-col` attribute) → toggle asc/desc. Default: `p_now_p_min ASC`.

---

#### Modal de Detalhe — Cards de Preço (`#priceCards`)

Ao clicar em qualquer ativo no Screening, Carteira ou Favoritos, abre o modal com um grid de cards de preço. Renderizado por `renderPriceCards(dec, val)` em `index.html`.

**Fonte dos dados DCF:** lidos de `val.dcf` (retornado por `/api/valuation/<ticker>`). O cálculo é feito no backend — `_calc_dcf()` em `valuation_calculator.py`. O frontend não recalcula.

| Card | Campo | Cor | Observação |
|------|-------|-----|-----------|
| Preço Atual | `dec.price_now` | neutro | Google Finance, cache 30 min |
| **Valor Intrínseco** | `val.dcf.intrinsic_value` | 🟢 se VI > preço / 🔴 se VI < preço | "—" quando P·L ausente/negativo |
| **Margem de SEG** | `val.dcf.margin_of_safety` | 🟢 ≥20% / 🟡 0–20% / 🔴 negativo | Fórmula: (VI−Preço)/VI×100. Display mínimo: "< −200%" |
| Target 6% | `dec.price_target_6pct` | verde | Bazin/Barsi |
| Target 8% | `dec.price_target_8pct` | amarelo | zona agressiva |
| Potencial | `dec.gain_pct` | verde se ≥0 | upside até Target 6% |
| DY Real | `dec.dy_real` | verde | yield últimos 12m / preço atual |
| Payout | `dec.payout` | 🔴 se >100% | com linha FCF quando disponível |
| Acumulação 6m | `dec.accumulation_score` | gradiente | % pregões Barsi |
| Acumulação 30d | calculado | gradiente | mesmo critério, janela 1 mês |
| Dividendos por Ano | gráfico `canvas#divChart` | — | span full-width |

> **Cards removidos (histórico):** `Mín. 6 meses` (suporte técnico) e `Máx. 6 meses` (resistência técnica) foram removidos do modal em abril/2026 para dar lugar aos cards de VI e Margem de SEG. Os campos `price_min_6m` e `price_max_6m` continuam disponíveis nos dados e exibidos na seção Preços do relatório PDF.

#### Modal de Detalhe — Gráfico Preço & Volume

Renderizado por `renderCharts(chartData, dec, val)`. Períodos: 6m / 3m / 1m (botões no header do modal).

**Linhas do gráfico de preço (`#priceChart`):**

| Linha | Cor | Padrão | Fonte |
|-------|-----|--------|-------|
| Preço | `#58a6ff` azul | contínua (verde quando abaixo da média) | `chartData.closes` |
| Target 6% | `#39d353` verde | `[6,3]` | `dec.price_target_6pct` |
| Target 8% | `#d29922` laranja | `[4,3]` | `dec.price_target_8pct` |
| pMin 6m | `#a371f7` roxo | `[3,3]` | `dec.price_min_6m` |
| Média Preço | `#8b949e` cinza | `[2,4]` | média dos closes do período |
| **VI (DCF)** | `#2dd4bf` teal | `[8,3]` | `val.dcf.intrinsic_value` |

A linha **VI (DCF)** só é exibida quando o backend retorna o campo `dcf` com `intrinsic_value` válido. Ausente quando P·L é negativo ou indisponível.

**Fundo verde nos candles** (`bgAccumul` plugin): pregões onde preço E volume ficam abaixo de suas médias — sinal de acumulação silenciosa Barsi.

#### Modal de Detalhe — Ranking no Setor (`#sectorRankBox`)

Card compacto no rodapé do `#mElemCard` (abaixo do radar), listando os pares do mesmo setor/segmento ordenados por **BRank (`unified_rank`)** desc. Permite comparar o ticker atual com concorrentes diretos.

Renderizado por `_renderSectorRanking(dec)` e `_sectorRankBodyHTML()` em `index.html`. Estado global `_sectorRankState = { peers, currentTicker, page }`.

**Agrupamento (`sectorKey`):** prefere `dec.segmento` (mais específico); fallback para `dec.sector`. Valor `'-'` é tratado como ausente. Só renderiza se houver ≥2 peers no mesmo setor.

**Fonte de dados:** filtra `allData` (carregado de `/api/decision`) pelo mesmo `sectorKey`. Se o ticker atual não estiver em `allData` (caso **FORA_CRITERIOS** — ex.: RECV3, ISAE4), é injetada uma entrada sintética a partir do `dec` com `unified_rank: null`, preservando `zone`.

**Ordenação:** `unified_rank` desc. Tickers com `unified_rank == null` vão para o final.

**Paginação:** páginas de 5 tickers (`_SECTOR_RANK_PAGE_SIZE`). Ao abrir o modal, a página inicial é a que contém o ticker atual (`Math.floor(idx / PAGE_SIZE)`). Navegação via botões `←` / `→` em `_sectorRankNav(delta)`, que atualiza apenas `#sectorRankBox.innerHTML` via `_sectorRankBodyHTML()`.

**Exibição por linha:**

| Elemento | Fonte | Cor |
|----------|-------|-----|
| `#N - TICKER` | índice no array ordenado + 1 | cor do rank (`--green-s` ≥70, `--yellow` ≥45, `--red` <45) |
| `(sinal)` | `zoneShort[p.zone]` — `forte`/`compra`/`aguardar`/`acima`/`s/preço` | cor da zona (`zoneColors`) |
| BRank | `p.unified_rank.toFixed(0)` ou `—` | cor do rank |
| Label `fora` (itálico cinza) | quando `unified_rank == null` | `--muted` |

**Ticker atual (destaque):** fundo laranja `rgba(245,158,24,.28)` + borda `rgba(245,158,24,.7)` + `font-weight:700`. As cores do texto (rank, BRank, sinal) **permanecem as naturais** — o destaque é apenas estrutural, não sobrescreve semântica (ex.: um ROMI3 com BRank 35 continua vermelho mesmo sendo o corrente).

**Clique em peer:** chama `openDetail(ticker)` — reabre o modal para o ticker clicado, substituindo todo o conteúdo.

**Header do card:** `Ranking no setor · <pos>/<total> por BRank`. Quando `pos` é `null` (ticker sem `unified_rank`), mostra `—/<total>`.

---

### 9.2 Carteira — Gestão de Posições

**Propósito:** Acompanhar posições reais com análise integrada.

**Fonte de dados:** Arquivo XLS de custódia exportado da B3 (`data/B3/Custodia*.xls`).

#### Sub-aba Ações

| Coluna | Campo JSON | Descrição |
|--------|-----------|-----------|
| `Ativo` | `ticker` | Ticker |
| `Qtd` | `qtd` | Quantidade de ações |
| `PT %` | calculado | % do portfólio total (valor_atual / total_atual) |
| `PM (R$)` | `preco_medio` | Preço médio de compra |
| `Preço (R$)` | `preco_atual` | Preço atual |
| `Investido (R$)` | `total_investido` | Total investido (Qtd × PM) |
| `Valor (R$)` | `valor_atual` | Valor atual (Qtd × Preço) |
| `Retorno (R$)` | `retorno` | Lucro/prejuízo em R$ |
| `Retorno (%)` | `retorno_pct` | Lucro/prejuízo em % |
| `DY s/PM (%)` | `dy_on_cost` | Dividend Yield sobre o PM |
| `Score` | `weighted_score` | Score de qualidade (pill colorida) |
| `BRank` | `unified_rank` | Ranking Unificado 0-100 (pill colorida) |
| `MOAT` | `buffett_moat_score` | Moat score (pill colorida) |
| `Saúde` | `piotroski_score` | Piotroski (badge colorido) |
| `FCF/L` | `fcf_lucro_ratio` | Qualidade do lucro (✓ ou ❌) |
| `Sinal` | `zone` | Zona de preço atual |

**DY sobre PM:** `avg_dividends_5y / preco_medio * 100` — yield que o investidor realmente recebe sobre o capital investido.

**Recomendações:**
- `AUMENTAR` → COMPRA_FORTE + rank ≥ 12 + p_now_p_min ≤ 1.15
- `COMPRAR_MAIS` → COMPRA ou COMPRA_FORTE + rank ≥ 9
- `AGUARDAR` → MONITORAR ou rank 6–8
- `AVALIAR_VENDA` → rank < 6 ou CARO
- `FORA_CRITERIOS` → ação na custódia que não passou nos filtros obrigatórios

**Sort:** clique nos headers (`data-ptcol` attribute). Default: `retorno_pct ASC`.

#### Cards de Resumo da Carteira (`#portfolioSummary`)

Renderizado por `renderPortfolioSummary(s)` em `index.html`. Exibido acima da tabela, atualizado ao trocar de aba (Ações / FIIs).

| Card | Cálculo | Escopo |
|------|---------|--------|
| Ações / FIIs | `s.count` | label dinâmico conforme aba ativa |
| Total Investido | `s.total_investido` | aba ativa |
| Valor Atual | `s.total_atual` | aba ativa |
| Retorno (R$) | `s.retorno_total` | aba ativa |
| Retorno (%) | `s.retorno_total_pct` | aba ativa |
| **Renda Mensal** | `sum(qtd × div_anual) / 12` — somente da aba ativa | sub: DY s/atual e s/PM em % a.a. |
| **Dividendos Est. Próx 12M** | `sum(qtd × div_anual)` — ações + FIIs combinados | sub: DY s/atual e s/investido |

**Detalhes do cálculo de dividendos:**
- Ações: usa `avg_dividends_5y` (média ponderada por recência, últimos 5 anos)
- FIIs: usa `dividends_sum_12m` (soma real dos últimos 12 meses por cota)
- `_divCalc(list)` reduz a lista somando `qtd × (avg_dividends_5y ?? dividends_sum_12m)`

**Tab-awareness:** `renderPortfolioSummary` detecta a aba ativa via `s === _acoesSummary` (referência). Ações → usa `portfolioData`; FIIs → usa `fiiData`. O card "Dividendos Est. Próx 12M" sempre combina os dois.

#### Sub-aba FIIs

| Coluna | Campo JSON |
|--------|-----------|
| Ativo, Qtd, PT%, PM, Preço, Investido, Valor, Retorno R$, Retorno % | idem Ações |
| `DY Real (%)` | yield sobre preço atual |
| `DY s/PM (%)` | yield sobre preço médio de compra |

---

### 9.3 Favoritos — Lista Personalizada

**Gerenciamento:** ícone ❤️ no Screening adiciona/remove. Persiste em `favoritos.json`.

**Modo Card:** Ticker + badges + Preço + Potencial + Score + **BRank** + DY + Piotroski + MOAT + Setor.

**Modo Tabela:** Colunas: Ticker, Preço, Zona, Score, **BRank**, DY, Ganho, Piotroski, Moat, Setor.

---

### 9.5 Swing Trade — Oportunidades Técnicas

**Propósito:** Identificar setups de swing trade aplicando 4 indicadores técnicos sobre o histórico OHLCV de todos os ~127 tickers do Screening. Exibe somente ativos onde ≥ 2 indicadores disparam simultaneamente.

**Fonte de dados:** `swing_data.json` gerado por `swing_service.py`. Atualizado automaticamente uma vez por dia (scheduler verifica a cada 1h se os dados têm > 23h).

**Endpoint:** `GET /api/swing` → lista completa com todos os indicadores calculados.

**Colunas da tabela:**

| Coluna | Campo JSON | Descrição |
|--------|-----------|-----------|
| `Ativo` | `ticker` | Clicável — abre o mesmo modal de Screening/Carteira |
| `Preço (R$)` | `price` | Último fechamento usado no cálculo |
| `RSI (14)` | `rsi` | Índice de Força Relativa — verde/bold se < 30 |
| `MACD` | `macd_bullish` | Badge `↑ Bull` (verde) ou `↓ Bear` (cinza) |
| `Bollinger` | `bb_signal` | Badge `≤ Inf` (verde) ou `Normal` (cinza) |
| `MA Cross` | `ma_signal` | Badge `Golden` (verde) ou `Death` (cinza) |
| `Sinais` | `signals_count` | Barra de 4 dots + contador `X/4` |
| `Status` | `is_setup` + botão 📈 | Badge `SETUP` (verde) quando `signals_count ≥ 2` + ícone de gráfico |

**Cores dos sinais:**

| `signals_count` | Cor do contador |
|----------------|----------------|
| 3 ou 4 | Verde (`--green`) |
| 2 | Amarelo (`--yellow`) |
| 0 ou 1 | Cinza (`--muted`) |

**Toolbar:**

| Elemento | Comportamento |
|---------|--------------|
| Card `SETUPs` | Total com `is_setup = true` |
| Card `Monitorar` | Total com `signals_count === 1` |
| Card `Analisados` | Total de tickers no JSON |
| Toggle `Só SETUPs` | Padrão **ligado** — esconde tickers com `signals_count < 2` |
| Timestamp | `updated_at` do primeiro item do JSON |

**Ordenação padrão:** `signals_count` DESC. Colunas ordenáveis: `ticker`, `price`, `rsi`, `signals_count`.

**Clique na linha:** chama `openDetail(ticker)` — abre o modal completo existente (gráfico, VI, ranking no setor, Buffett Moat). Zero código novo no modal.

**Clique no ícone 📈 (coluna Status):** `event.stopPropagation()` + `openSwingChart(ticker)` — abre o modal de gráfico de indicadores (não conflita com o clique na linha).

---

#### Modal de Gráfico Swing (`#swingChartModal`)

Abre ao clicar no ícone 📈 de qualquer linha da tabela. Busca dados on-demand via `GET /api/swing/chart/<ticker>` (yfinance direto, ~1–2s de latência).

**3 painéis Chart.js sobrepostos:**

| Painel | Canvas | Conteúdo | Altura |
|--------|--------|---------|--------|
| 1 — Preço | `#swingPriceCanvas` | Linha de preço (azul) + BB Sup/Mid/Inf (cinza pontilhado) + MA20 (amarelo) + MA50 (roxo) | 140px |
| 2 — RSI | `#swingRsiCanvas` | RSI(14) (verde) + linha horizontal em 30 (vermelho pontilhado) + linha em 70 (amarelo pontilhado) | 80px |
| 3 — MACD | `#swingMacdCanvas` | Histograma (barras verde/vermelho) + MACD line (azul) + Signal line (vermelho pontilhado) | 80px |

**Cores dos painéis:**

| Série | Cor |
|-------|-----|
| Preço | `#58a6ff` azul |
| BB bandas | `rgba(139,148,158,.4)` cinza pontilhado |
| MA20 | `#d29922` amarelo |
| MA50 | `#a371f7` roxo |
| RSI(14) | `#3fb950` verde |
| Linha 30 (sobrevenda) | `rgba(248,81,73,.5)` vermelho pontilhado |
| Linha 70 (sobrecompra) | `rgba(210,153,34,.4)` amarelo pontilhado |
| Histograma positivo | `rgba(63,185,80,.45)` verde translúcido |
| Histograma negativo | `rgba(248,81,73,.45)` vermelho translúcido |
| MACD line | `#58a6ff` azul |
| Signal line | `#f85149` vermelho pontilhado |

**Responsividade:** modal tem `max-height: calc(100vh - 32px)` + `overflow-y: auto` — funciona até ~150% de zoom no navegador. Header (ticker + botão fechar) é `position: sticky`.

**Endpoint de dados:**

```
GET /api/swing/chart/<ticker>
```

Retorno: `{ ticker, dates[], closes[], bb_upper[], bb_middle[], bb_lower[], ma20[], ma50[], rsi[], macd_line[], macd_signal[], macd_hist[] }`

Todos os arrays têm o mesmo comprimento (um elemento por fechamento diário). Os primeiros N elementos são `null` onde há dados insuficientes para calcular o indicador (ex: `rsi[0..13] = null`).

**Funções JS:**

| Função | Responsabilidade |
|--------|-----------------|
| `openSwingChart(ticker)` | Fetch → destrói charts anteriores → cria 3 novos Chart.js |
| `closeSwingChart()` | Destrói as 3 instâncias (`_swingChartPrice/Rsi/Macd`) + esconde modal |

**Estado JS:**

```javascript
// Tabela
let _swingData      = [];       // array retornado por /api/swing
let _swingSortCol   = 'signals_count';
let _swingSortAsc   = false;
let _swingOnlySetup = true;
let _swingLoaded    = false;

// Modal de gráfico
let _swingChartPrice = null;    // instância Chart.js — destruída ao fechar
let _swingChartRsi   = null;
let _swingChartMacd  = null;
```

> Para fórmulas e limiares dos indicadores técnicos → `brain_calculations.md` seção 7.12.
> Para as funções de série backend (`calc_rsi_series`, `calc_bb_series`, `calc_ma_series`, `calc_macd_series`) → `swing_service.py`.

---

### 9.4 Radar — Alertas de Preço

**Configuração por ativo:**
- **Alerta Compra (≤):** dispara quando preço cai abaixo do valor configurado
- **Alerta Venda (≥):** dispara quando preço sobe acima do valor configurado

**Endpoints:**
- `GET /api/radar/alerts` → verifica alertas disparados
- `POST /api/radar/dismiss` → silencia por 24h

---

## 11. Fontes de Dados Externas

### 11.1 Google Finance — Preços em Tempo Real

```
URL:    https://www.google.com/finance/quote/{TICKER}:BVMF
Método: Scraping HTML
Extração: CSS class "YMlKec fxKbKc"
Regex:  r'[\d]+[.,][\d]+'
Cache:  30 minutos
Risco:  frágil (classe CSS pode mudar a qualquer momento)
```

### 11.2 Yahoo Finance (yfinance)

Todos os tickers B3 recebem sufixo `.SA`. Ex: `yfinance.Ticker("BBAS3.SA")`

| Método | Dados | Usado em |
|--------|-------|---------|
| `Ticker.history(period="6mo")` | OHLCV 6 meses | history_fetcher, decision_service |
| `Ticker.history(period="1mo")` | OHLCV 1 mês | decision_service (acum. 30d) |
| `Ticker.dividends` | Série histórica | history_fetcher |
| `Ticker.financials["Net Income"]` | Lucro líquido anual | history_fetcher |
| `Ticker.cashflow` | FCO, CapEx, D&A | buffett_fetcher |
| `Ticker.income_stmt` | Receita, EBIT, Net Income 4a | buffett_fetcher (tendências) |
| `Ticker.balance_sheet` | Dívida, PL, Ativos 4a | buffett_fetcher (tendências) |

### 11.3 StatusInvest — API Não Oficial

| Endpoint | Dados | Rate Limit |
|----------|-------|-----------|
| `/acao/payoutresult?code={t}` | Payout ratio atual | 1.5s |
| `/acao/getdre?code={t}&range.min={y}&range.max={y}` | DRE 10 anos | 1.5s |
| `/acao/getativos?code={t}&range.min={y}&range.max={y}` | Balanço 10 anos | 1.5s |
| `/acao/getfluxocaixa?code={t}&range.min={y}&range.max={y}` | Cashflow 10 anos | 1.5s |

**Headers obrigatórios:**
```python
headers = {
    "User-Agent": "Mozilla/5.0 ...",
    "Accept": "application/json",
    "Referer": "https://statusinvest.com.br/"
}
```

**`all_indicators.json`:** exportado manualmente do StatusInvest, ~615 tickers B3, 36+ indicadores por ação. **Atualização manual periódica.**

### 11.4 B3 — Arquivo de Custódia

```
Local: data/B3/Custodia*.xls
Leitura: xlrd (Python)
Campos: ticker, quantidade, preço médio, total investido
Atualização: manual (download do portal B3)
```

---

## 12. Limitações e Considerações Conhecidas

### 11.5 Alertas Visuais no Modal de Tendências Históricas

O modal de Buffett Moat (seção "TENDÊNCIAS HISTÓRICAS") exibe dois tipos de alertas automáticos baseados nos dados do `buffett_moat.trends_values`:

#### Badge de Dados Desatualizados (⚠ vermelho)

Aparece quando o último ano disponível na DRE do StatusInvest (`ext_anos`) está defasado em relação ao ano atual.

```javascript
// Lógica frontend (index.html)
const _anoAtual     = new Date().getFullYear();
const _ultimoAno    = parseInt(anosExib[anosExib.length - 1]);  // último ano disponível
const anosFaltantes = [];
for (let y = _ultimoAno + 1; y < _anoAtual; y++) anosFaltantes.push(String(y));
const dataDesatualizada = anosFaltantes.length > 0;
```

**Threshold:** `ano_atual - ultimo_ano >= 2` — em 2026, dados até 2024 disparam o alerta.

**Visual:**
- Badge vermelho acima da tabela listando os anos faltantes
- Colunas extras no cabeçalho da tabela com o ano em vermelho
- Células das linhas (MB, ML, ROE) preenchidas com `--%` em vermelho/bold
- **Somente** a tabela StatusInvest (MB/ML/ROE) recebe as colunas extras — a tabela "CAIXA/DÍVIDA (yfinance)" **não** é afetada (tem dados próprios e atualizados)

**Como resolver:** `python financials_fetcher.py TICKER --force` + `python valuation_calculator.py TICKER`  
Ou em lote: `python financials_fetcher.py --update` + `python valuation_calculator.py`

**Implementação:** `_buildRowMissing()` — variante de `_buildRow()` que appenda células `--% ` vermelhas para os `anosFaltantes`. As linhas da tabela principal usam `_buildRowMissing()`; as da tabela de caixa usam `_buildRow()` normal.

---

#### Badge de Resultado Não Recorrente (⚠ amarelo)

Aparece quando `buffett_moat.trends_values.resultado_nao_recorrente === true`.

```javascript
const naoRecorrente = tv.resultado_nao_recorrente === true;
```

**Visual:** Badge amarelo com texto explicativo abaixo do título da seção, antes da tabela. Alerta que a margem líquida do último ano é ≥ 1,8× a média dos 4 anos anteriores com receita estagnada, e orienta a verificar eventos tributários/extraordinários.

**Fórmula de detecção:** ver `brain_calculations.md` seção 7.11.

**O que significa na prática:** scores como Piotroski 8/9 e Buffett Moat FORTE podem estar inflados por um único evento irrepetível. O alerta não altera os scores — é informacional para que o usuário investigue antes de tomar decisão.

---

### 12.1 CapEx Total vs. Manutenção

A aplicação usa o **CapEx total** para calcular FCF e Owner Earnings. Para empresas em forte fase de crescimento (ex: WEGE3), o CapEx de expansão é alto — isso **sub-estima** o Owner Earnings e pode gerar score de qualidade injustamente baixo.

**Impacto estimado:** até 17% de distorção negativa em empresas de alto crescimento.

### 12.2 Moat por Proxies Financeiros

O Buffett Moat Score mede **sintomas financeiros de moat** (altas margens, ROE elevado), mas não a causa estrutural. Os verdadeiros moats (switching costs, network effects, intangibles, cost advantages) não são capturados.

### 12.3 Fonte Única de Dados Fundamentalistas

`all_indicators.json` vem exclusivamente do StatusInvest. Sem cross-validação. Verificar valores outliers no Screening.

### 12.4 Setores Financeiros — Critérios Diferentes

Bancos e seguradoras têm alta alavancagem estrutural. Dois critérios são isentos:
- `liquidez_corrente_ok`: inaplicável (depósitos > ativo circulante por design)
- `passivo_ativo_ok`: inaplicável (alavancagem 10-20x é normal e regulada)

**Identificação:** `FINANCIAL_PL_ATIVO_MAX = 0.20` — se PL/Ativo ≤ 20%, tratado como financeira.

### 12.5 Sem Testes sobre Lógica de Negócio

Existe `test_price_service.py`, mas **não há testes cobrindo:**
- Cálculo dos 21 critérios
- Buffett Moat Score
- Piotroski F-Score
- Lógica de medalhas

Mudanças em `valuation_calculator.py` podem introduzir regressões silenciosas.

### 12.6 Frágil Dependência do Google Finance

O scraping depende da CSS class `YMlKec fxKbKc` que pode mudar sem aviso. Se mudar, a coleta de preços para completamente. Verificar logs do `PriceService` regularmente.
