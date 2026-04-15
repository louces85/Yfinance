# Brain YFinance — Documentação Completa da Aplicação

> **Última atualização:** Abril de 2026  
> Este documento é o "cérebro" da aplicação YFINANCE_REFACTOR. Cobre filosofia, arquitetura, pipeline, classes, APIs externas, cálculos, páginas e todos os indicadores.

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Filosofias de Investimento Implementadas](#2-filosofias-de-investimento-implementadas)
3. [Arquitetura Geral e Fluxo de Dados](#3-arquitetura-geral-e-fluxo-de-dados)
4. [Árvore de Arquivos do Backend](#4-árvore-de-arquivos-do-backend)
5. [Descrição das Classes e Arquivos Principais](#5-descrição-das-classes-e-arquivos-principais)
6. [Diagramas de Sequência](#6-diagramas-de-sequência)
7. [Cálculos e Métricas Detalhadas](#7-cálculos-e-métricas-detalhadas)
8. [Sistema de Medalhas e Selos](#8-sistema-de-medalhas-e-selos)
9. [Páginas da Aplicação](#9-páginas-da-aplicação)
10. [Tabela de Referência — Todos os Limiares](#10-tabela-de-referência--todos-os-limiares)
11. [Fontes de Dados Externas](#11-fontes-de-dados-externas)
12. [Limitações e Considerações Conhecidas](#12-limitações-e-considerações-conhecidas)

---

## 1. Visão Geral

### O que é

Uma aplicação de **screening e gestão de investimentos em ações da B3**, construída como ferramenta pessoal para auxiliar na tomada de decisão com base em múltiplas filosofias de investimento em renda variável.

A aplicação combina, em tempo real, dados fundamentalistas, histórico de dividendos, análise técnica simplificada e critérios de qualidade para **rankear e classificar ações brasileiras**, destacando as melhores oportunidades de entrada.

### O que faz

- **Screening**: exibe todas as ações monitoradas com pontuação, zona de compra, potencial de valorização e distância do suporte
- **Carteira**: acompanha posições reais com retorno, DY sobre preço médio e análise fundamentalista integrada
- **Favoritos**: lista personalizada de ativos com visualização rápida em cards ou tabela
- **Radar**: alertas de preço configuráveis por ativo (compra e venda)

### Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.8 |
| API | Flask (REST) |
| Dados de mercado | yfinance (Yahoo Finance), Google Finance (scraping) |
| Dados fundamentalistas | StatusInvest (API não oficial) |
| Custódia | B3 XLS (xlrd) |
| Cálculos numéricos | numpy (regressão linear para tendências) |
| Persistência | JSON com atomic writes (sem banco de dados) |
| Frontend | HTML + JavaScript vanilla (sem framework) |
| Agendamento | Daemon thread Flask |

### Filosofia Híbrida

A aplicação não segue uma única filosofia. Ela combina:

```
Barsi   → Quando comprar (yield, setor, acumulação silenciosa)
Bazin   → Quanto vale (preço justo via dividendo médio / 6%)
Graham  → Margem de segurança (P/L, P/VP, VPA, liquidez, dívida)
Buffett → Qualidade do negócio (moat, FCF, owner earnings)
```

---

## 2. Filosofias de Investimento Implementadas

### 2.1 Luiz Barsi Filho — "A Galinha dos Ovos de Ouro"

**Filosofia central:** Comprar empresas como quem compra um negócio. O objetivo é acumular renda, não especular com preço. *"Compre a galinha, não o ovo."*

O que mais importa para Barsi:
- A empresa **paga dividendos consistentemente** há no mínimo 5 anos
- O **preço atual está abaixo do preço que entrega pelo menos 6% de yield**
- A empresa opera em **setores essenciais e defensivos** (BEST: Bancos, Elétricas, Seguros, Saneamento, Transmissão)
- **Comprar quando ninguém quer**: quando preço E volume estão abaixo da média, é sinal de acumulação silenciosa — o momento ideal de entrar

**O que foi implementado da filosofia Barsi:**
- ✅ DY ≥ 6% (critério de compra)
- ✅ Preço abaixo do alvo 6% (Bazin)
- ✅ Três zonas de preço: 5% (monitorar), 6% (compra), 8% (compra forte)
- ✅ Acumulação silenciosa: score de dias com preço E volume abaixo da média 6m
- ✅ Filtro BEST por setor
- ✅ Consistência de dividendos (5 anos)
- ✅ Dividendo crescente (flag)

---

### 2.2 Décio Bazin — "Faça Fortuna com Ações" (1992)

**Filosofia central:** Ações são pedaços de um negócio. O preço justo é determinado pela renda que o negócio gera. Se o dividendo é consistente, o preço justo pode ser calculado matematicamente.

**Fórmula do Preço Justo (Bazin):**
```
Preço Justo = Média de Dividendos (últimos 5 anos, ponderado) / 0.06
```

**6 Critérios de Bazin:**

| # | Critério | Limiar | Implementado |
|---|---------|--------|-------------|
| 1 | Dividend Yield | ≥ 6% | ✅ |
| 2 | Consistência de dividendos | ≥ 5 anos sem interrupção | ✅ |
| 3 | Payout Ratio | 40% a 80% | ✅ |
| 4 | Dívida Líq./PL | ≤ 1.0 | ✅ |
| 5 | Liquidez diária | ≥ R$200k/dia | ✅ |
| 6 | Setores defensivos | Utilities, bancos | ✅ (filtro BEST) |

**Detalhe crítico do Payout:**
- Payout **< 40%**: empresa retém demais (má alocação ou problema escondido)
- Payout **> 80%**: dividendo insustentável (paga mais do que ganha)
- Faixa saudável: **40% a 80%**

---

### 2.3 Benjamin Graham — "O Investidor Inteligente"

**Filosofia:** Comprar com margem de segurança. O mercado é Mr. Market — um sócio maníaco-depressivo. Compre quando ele está deprimido.

**Critérios do Investidor Defensivo implementados:**

| # | Critério | Limiar Graham | Implementado |
|---|---------|--------------|-------------|
| 1 | P/L moderado | ≤ 15 (média 3 anos) | ✅ |
| 2 | P/VP moderado | ≤ 1.5 | ✅ |
| 3 | Regra combinada | P/L × P/VP ≤ 22.5 | ✅ |
| 4 | Preço ≤ VPA | Preço ≤ Valor Patrimonial por Ação | ✅ (flags de medalha) |
| 5 | Liquidez corrente | ≥ 2.0 | ✅ |
| 6 | Dívida/Ativos | ≤ 65% | ✅ |
| 7 | Crescimento de EPS | ≥ 5% CAGR 5a | ✅ |

**Regra Combinada de Graham:**
```
P/L × P/VP ≤ 22.5

Exemplo: P/L = 12 e P/VP = 1.8 → 12 × 1.8 = 21.6  ✅ (aprovado)
Exemplo: P/L = 15 e P/VP = 1.6 → 15 × 1.6 = 24.0  ❌ (reprovado)
```
Esta regra permite que uma empresa com P/VP alto (premium de qualidade) ainda passe se o P/L for baixo.

---

### 2.4 Warren Buffett — Moat, FCF e Owner Earnings

**Filosofia:** "É muito melhor comprar uma empresa maravilhosa a um preço justo do que uma empresa justa a um preço maravilhoso."

Buffett busca **vantagens competitivas duráveis (moat)** que protejam os lucros no longo prazo.

**O que foi implementado da filosofia Buffett:**

**Buffett Moat Score (0-10)** — mede a durabilidade da vantagem competitiva:
- Margem Bruta ≥ 40% → **pricing power** (peso 2)
- ROE ≥ 20% → **eficiência de capital** (peso 2)
- Margem Líquida ≥ 20% → lucro real após todos os custos
- ROIC ≥ 15% → retorno sobre capital investido
- DL/PL ≤ 0.5 → empresa com moat não precisa de muita dívida
- CAGR Lucro ≥ 10% e CAGR Receita ≥ 5% → crescimento consistente
- Dividendo crescente → sinal de geração de caixa sustentável

**FCF (Free Cash Flow):** `FCO - |CapEx|`  
> Filtro de qualidade de lucro: lucro contábil vs. caixa real gerado

**Owner Earnings (Buffett's true profit):** `Lucro Líquido + D&A - |CapEx|`  
> O verdadeiro lucro disponível para o dono do negócio

**FCF/Lucro ≥ 80%:** se menos de 80% do lucro vira caixa real, há risco de manipulação contábil ou consumo excessivo de capital de giro.

**Tendências históricas (4-10 anos):** Margem Bruta, ROE e FCF em queda sugerem que o moat está se deteriorando — penalidade no score.

---

## 3. Arquitetura Geral e Fluxo de Dados

### Pipeline Completo

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FONTES DE DADOS                              │
│                                                                     │
│  Google Finance   Yahoo Finance (yfinance)   StatusInvest   B3 XLS │
│  (scraping)       (lib Python)               (API não-oficial)     │
└───────┬───────────────────┬─────────────────────┬──────────────────┘
        │                   │                     │
        ▼                   ▼                     ▼
┌───────────────┐  ┌────────────────────┐  ┌────────────────────────┐
│ stock_prices  │  │  stock_history     │  │  financials_history    │
│ .json         │  │  .json             │  │  .json                 │
│               │  │                   │  │                        │
│ Preço atual   │  │ 6m: min/max preço  │  │ 10 anos:               │
│ Cache 30 min  │  │ 5a: dividendos     │  │  DRE (receita, EBIT,  │
│               │  │ 5a: lucro líquido  │  │  EBITDA, lucro, ROE)  │
│               │  │ payout ratio       │  │  Balanço (ativos,     │
│               │  │ Buffett FCF/Owner  │  │  passivos, PL)        │
│               │  │ Tendências 4a      │  │  Fluxo de Caixa       │
└───────┬───────┘  └────────┬───────────┘  └────────────┬───────────┘
        │                   │                            │
        └───────────────────┼────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │     all_indicators.json     │
              │  (StatusInvest exportado)   │
              │                             │
              │ P/L, P/VP, ROE, ROIC,       │
              │ margens, dívidas, CAGR,     │
              │ VPA, LPA, EV/EBIT, PEG...  │
              └─────────────┬───────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │   valuation_calculator.py   │
              │                             │
              │  21 critérios binários      │
              │  Score Ponderado (0-100)    │
              │  Piotroski F-Score (0-9)    │
              │  Buffett Moat Score (0-10)  │
              │  Zonas de preço             │
              └─────────────┬───────────────┘
                            │
              ┌─────────────┴────────────┐
              ▼                          ▼
    ┌─────────────────┐       ┌────────────────────┐
    │ valuations.json │       │ monitoring_stocks  │
    │                 │       │ .json              │
    │ Valuation       │       │                    │
    │ completo por    │       │ ~127 tickers        │
    │ ticker          │       │ pré-qualificados   │
    └────────┬────────┘       │ sort: score DESC   │
             │                └─────────┬──────────┘
             │                          │
             └──────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │     decision_service.py     │  ◄── Roda a cada 30 min
              │                             │       (scheduler Flask)
              │  + Preço real atualizado    │
              │  + Recalcula zona           │
              │  + p_now_p_min              │
              │  + gain_pct, dy_real        │
              │  + Medalhas: Gold/Bronze    │
              │  + Selo Buffett             │
              │  + Setor/BEST               │
              └─────────────┬───────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │    decision_stocks.json     │
              │                             │
              │ ~127 ações ordenadas por    │
              │ p_now_p_min ASC             │
              │ (mais próximo do suporte    │
              │  = primeiro da lista)       │
              └─────────────┬───────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │       api_server.py         │
              │        (Flask REST)         │
              │                             │
              │  GET /api/decision          │
              │  GET /api/portfolio         │
              │  GET /api/chart/<ticker>    │
              │  GET /api/favoritos         │
              │  GET /api/radar             │
              │  ...                        │
              └─────────────┬───────────────┘
                            │
                            ▼
              ┌─────────────────────────────┐
              │     Frontend (index.html)   │
              │     JS Vanilla              │
              │                             │
              │  Screening / Carteira /     │
              │  Favoritos / Radar          │
              └─────────────────────────────┘
```

### Padrão de Persistência — Atomic Write

Todos os arquivos JSON são escritos atomicamente para evitar corrupção em caso de falha de processo:

```python
# Padrão usado em stock_repository.py
import tempfile, os

with tempfile.NamedTemporaryFile('w', dir=data_dir, delete=False, suffix='.tmp') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    tmp_path = f.name

os.replace(tmp_path, final_path)  # Operação atômica no Linux
```

### Intervalos de Atualização

| Dado | Intervalo | Motivo |
|------|-----------|--------|
| Preço atual | 30 min | Cache para não sobrecarregar Google Finance |
| stock_history | 7 dias | Dividendos e financials são anuais |
| financials_history | 30 dias | DRE e Balanço mudam trimestralmente |
| decision_stocks | 30 min | Scheduler automático |

---

## 4. Árvore de Arquivos do Backend

```
YFINANCE_REFACTOR/
├── frontend/
│   └── index.html              ← SPA completo (JS vanilla, ~3000 linhas)
│
└── backend/
    ├── api_server.py           ← Flask app + scheduler de 30 min
    │
    ├── config/
    │   ├── __init__.py
    │   └── rules.py            ← TODOS os thresholds e constantes
    │
    ├── repositories/
    │   ├── __init__.py
    │   └── stock_repository.py ← Camada de dados: leitura/escrita atômica dos JSONs
    │
    ├── services/
    │   ├── __init__.py
    │   ├── stock_validator.py      ← Valida tickers via yfinance
    │   ├── price_service.py        ← Classe PriceService (injetável, com testes)
    │   ├── price_fetcher.py        ← Versão procedural do price_service
    │   ├── history_fetcher.py      ← 6m preços + 5a dividendos + Buffett metrics
    │   ├── buffett_fetcher.py      ← Fase 2 (FCF/OE) e Fase 3 (tendências 4a)
    │   ├── financials_fetcher.py   ← DRE + Balanço + FCF via StatusInvest (10 anos)
    │   ├── valuation_calculator.py ← Motor principal: 21 critérios + 3 scores
    │   ├── decision_service.py     ← Gera decision_stocks.json (30 min)
    │   └── portfolio_service.py    ← Lê B3 XLS e calcula posições
    │
    ├── tests/
    │   ├── conftest.py
    │   ├── __init__.py
    │   └── test_price_service.py
    │
    ├── data/
    │   ├── all_indicators.json     ← Indicadores fundamentalistas (StatusInvest, exportado)
    │   ├── all_sectors.json        ← Ticker → {setor, subsetor, segmento}
    │   ├── stocks_list.json        ← Lista mestre de tickers monitorados
    │   ├── stock_validity.json     ← Status de validação por ticker
    │   ├── stock_prices.json       ← Preços atuais com timestamp
    │   ├── stock_history.json      ← 6m preços + 5a dividendos + Buffett
    │   ├── financials_history.json ← 10 anos de DRE, Balanço e Cashflow
    │   ├── valuations.json         ← Valuation completo por ticker
    │   ├── monitoring_stocks.json  ← Tickers pré-qualificados (score DESC)
    │   ├── decision_stocks.json    ← Decisões finais (p_now_p_min ASC)
    │   ├── favoritos.json          ← Favoritos do usuário
    │   ├── radar.json              ← Alertas de preço
    │   └── B3/
    │       └── Custodia*.xls       ← Arquivo de custódia exportado da B3
    │
    └── libs/
        └── transcribe_meeting.py   ← Utilitário de transcrição de áudio (Whisper)
```

---

## 5. Descrição das Classes e Arquivos Principais

### 5.1 `config/rules.py` — Todos os Thresholds

Arquivo central com **todas as constantes** da aplicação. Nunca há magic numbers espalhados no código — tudo vem daqui.

```python
# Exemplos de constantes
BASIN_BASE    = 0.06   # Yield-alvo base (compra moderada — Bazin)
BASIN_MIN     = 0.05   # Yield-alvo mínimo (monitorar)
BASIN_MAX     = 0.08   # Yield-alvo agressivo (compra forte — Barsi)
P_L_MAX       = 15.0   # P/L máximo (Graham)
P_VP_MAX      = 1.5    # P/VP máximo (Graham)
WEIGHTED_SCORE_MAX = 40.0  # Soma dos pesos → normalizado para 100
```

---

### 5.2 `repositories/stock_repository.py` — Camada de Dados

Ponto central de acesso a todos os arquivos JSON. **Nunca acesse os JSONs diretamente nos services** — sempre via repository.

**Funções principais:**

| Função | Arquivo | Operação |
|--------|---------|---------|
| `get/save_price(ticker)` | stock_prices.json | R/W |
| `get/save_history(ticker)` | stock_history.json | R/W |
| `get/save_valuation(ticker)` | valuations.json | R/W |
| `get/save_financials(ticker)` | financials_history.json | R/W |
| `get/save_validity(ticker)` | stock_validity.json | R/W |
| `get_monitoring_stocks()` | monitoring_stocks.json | R |
| `save_monitoring_stocks(data)` | monitoring_stocks.json | W |
| `get_all_indicators()` | all_indicators.json | R (read-only) |
| `get_indicators_by_ticker(ticker)` | all_indicators.json | R |
| `get_valid_tickers()` | stock_validity.json | R |

---

### 5.3 `services/stock_validator.py`

Verifica se um ticker existe e tem dados suficientes no mercado.

**Lógica:**
```python
df = yfinance.Ticker(f"{ticker}.SA").history(period="6mo")
# Inválido se: df vazio, < 10 pregões, preço zero, ou exceção do yfinance
```

**Persistência:** `stock_validity.json`  
**Intervalo:** 7 dias mínimo entre validações (`VALIDATION_INTERVAL_DAYS`)

---

### 5.4 `services/price_service.py` — Preço em Tempo Real

**Fonte:** Google Finance (scraping HTML)

```
URL: https://www.google.com/finance/quote/{TICKER}:BVMF
Extração: CSS class "YMlKec fxKbKc"
Regex: r'[\d]+[.,][\d]+'
Separador decimal: vírgula (BR) ou ponto
Cache: 30 min (PRICE_UPDATE_INTERVAL_HOURS = 0.5)
```

**Classe `PriceService`:**
- Construtor com injeção de dependências (`repository`, `http_client_factory`) — facilita testes
- `fetch_from_google(ticker)` → float ou None
- `update(ticker, force=False)` → busca + persiste
- `update_all(tickers, force, delay=0.3)` → batch com rate limiting

---

### 5.5 `services/history_fetcher.py`

Coleta dados históricos de 2 fontes e calcula métricas derivadas.

**O que coleta:**

```
Via yfinance:
  ├── Ticker.history(period="6mo")
  │     → price_min_6m, price_max_6m
  │     → close_avg_6m, volume_avg_6m
  │     → accumulation_score (% dias com P < avg_P e V < avg_V)
  │
  ├── Ticker.dividends (últimos 5 anos)
  │     → dividends_per_year {ano: valor}
  │     → avg_dividends_5y (ponderado: pesos [1,2,3,4,5])
  │     → dividends_sum_12m
  │     → paid_dividends_5_years (bool)
  │     → dividend_growing (último ano >= 90% do máximo anterior)
  │
  └── Ticker.financials["Net Income"] (últimos 5 anos)
        → net_income_per_year {ano: valor}
        → positive_income_5_years (bool)

Via StatusInvest:
  └── GET /acao/payoutresult?code={ticker_lower}
        → payout (campo "actual", float)

Via buffett_fetcher.py (chamado internamente):
  ├── Fase 2: buffett_cashflow {}
  │     → fcf, owner_earnings, fcf_lucro_ratio, capex_lucro_ratio
  │     → fcf_positivo, owner_earnings_positivo
  │     → fcf_quality_ok (fcf_lucro_ratio >= 0.80)
  │     → capex_moat_ok (capex_lucro_ratio <= 0.25)
  │
  └── Fase 3: buffett_trends {}
        → 4 anos de: margem_bruta, margem_liquida, roe, fcf,
                     divida_liq, capex_receita, sga_receita
        → trend por métrica: CRESCENDO | ESTAVEL | CAINDO | INDEFINIDO
```

**Intervalo:** 7 dias (`HISTORY_UPDATE_INTERVAL_DAYS`)

---

### 5.6 `services/buffett_fetcher.py` — Fases 2 e 3 do Moat

**Fase 2 — Qualidade de Caixa:**

```python
# Fonte: yfinance cashflow_stmt, income_stmt (últimos 4 anos, ano mais recente)
capex          = abs(cashflow["Capital Expenditure"])  # yfinance retorna negativo
da             = cashflow["Depreciation And Amortization"]
fco            = cashflow["Operating Cash Flow"]
net_income     = income_stmt["Net Income"]

fcf            = fco - capex                          # Fluxo de Caixa Livre
owner_earnings = net_income + da - capex              # Owner Earnings (Buffett)
fcf_lucro_ratio  = fcf / net_income                   # Qualidade do lucro
capex_lucro_ratio = capex / net_income                # Intensidade de CapEx
```

**Fase 3 — Tendências:**

```python
# Para cada métrica, calcula tendência via regressão linear (numpy)
def _calc_tendencia(valores: list, threshold_rel=0.05):
    # slope = coeficiente angular da regressão linear
    # mean  = média dos valores
    # Se slope / mean > +5%: CRESCENDO
    # Se slope / mean < -5%: CAINDO
    # Senão: ESTAVEL
    # Se < 2 pontos: INDEFINIDO
```

**Métricas com tendência calculada:**
`margem_bruta`, `margem_liquida`, `roe`, `fcf`, `divida_liq`, `capex_receita`, `sga_receita`

---

### 5.7 `services/financials_fetcher.py` — DRE 10 Anos do StatusInvest

Coleta o histórico longo de demonstrativos financeiros via API não oficial do StatusInvest.

**Endpoints StatusInvest:**

```
DRE (Demonstração de Resultado):
  GET https://statusinvest.com.br/acao/getdre
  Params: code={ticker}, type=0, range.min={ano}, range.max={ano}
  Campos: receita_liquida, lucro_bruto, ebitda, ebit, lucro_liquido,
          roe, roic, margem_bruta, margem_liquida, divida_bruta, divida_liquida

Balanço Patrimonial:
  GET https://statusinvest.com.br/acao/getativos
  Campos: ativo_total, ativo_circulante, caixa_equivalentes,
          passivo_total, passivo_circulante, patrimonio_liquido

Fluxo de Caixa:
  GET https://statusinvest.com.br/acao/getfluxocaixa
  Campos: fco (operacional), da (depreciação/amortização),
          fcf_livre, capex (via yfinance — mais confiável), financing
```

**Parse de valores StatusInvest:**
```python
# StatusInvest retorna valores formatados em PT-BR
"3.938,54 M"  → 3_938_540_000.0   (milhões × 10⁶)
"1,23 B"      → 1_230_000_000.0   (bilhões × 10⁹)
"-9,80"       → -9.8
"10,07%"      → 10.07
"-"           → None
```

**Rate limiting:** 1.5 segundos entre chamadas para não ser bloqueado  
**Intervalo de atualização:** 30 dias (`FINANCIALS_UPDATE_INTERVAL_DAYS`)  
**Anos coletados:** 10 (`FINANCIALS_YEARS`)

> **Nota importante sobre CapEx:** A linha de CapEx do StatusInvest não é confiável. Por isso, o CapEx é buscado diretamente do `yfinance.cashflow` e combinado com os dados do SI.

---

### 5.8 `services/valuation_calculator.py` — Motor Principal

**O coração da aplicação.** Combina todos os dados e aplica os 21 critérios de investimento.

**Entradas:**
- `all_indicators.json` → indicadores fundamentalistas (P/L, P/VP, ROE, ROIC, margens, dívidas, CAGR...)
- `stock_history.json` → histórico 6m + dividendos 5a + Buffett metrics
- `stock_prices.json` → preço atual
- `financials_history.json` → DRE/Balanço 10 anos (para tendências do Moat)

**Saídas:**
- `valuations.json` → valuation completo por ticker
- `monitoring_stocks.json` → apenas os tickers que passaram pelos filtros, ordenados por score

**Funções principais:**

| Função | Retorno |
|--------|---------|
| `calculate(ticker)` | dict com valuation completo |
| `_calc_buffett_moat_score(...)` | dict com score 0-10, flags, cashflow_values, trends |
| `_calc_piotroski(...)` | dict com score 0-9, flags individuais |
| `_calc_weighted_score(flags)` | dict com score 0-100 |
| `_calc_zone(price, t6, t8, t5)` | string: COMPRA_FORTE \| COMPRA \| MONITORAR \| CARO |

---

### 5.9 `services/decision_service.py`

Gera a visão final de entrada com **preço em tempo real**. Roda automaticamente a cada 30 minutos.

**O que faz para cada ticker:**
1. Busca preço atual (Google Finance via PriceService)
2. Carrega valuation pré-calculado (valuations.json)
3. Carrega histórico 6m (stock_history.json)
4. Recalcula zona com preço atual
5. Calcula métricas de entrada: `p_now_p_min`, `gain_pct`, `dy_real`
6. Calcula acumulação 30d: `yfinance.Ticker.history(period="1mo")`
7. Avalia medalhas: `is_gold`, `is_bronze`, `is_below_vpa_target`
8. Avalia Selo Buffett: `is_buffett_seal`
9. Busca setor e classifica `is_best`

**Ordenação:** por `p_now_p_min` ASC → ações mais próximas do suporte aparecem primeiro.

---

### 5.10 `services/portfolio_service.py`

Lê o arquivo XLS de custódia exportado da B3 e enriquece com análise fundamentalista.

**Processo:**
1. Encontra o arquivo XLS mais recente em `data/B3/`
2. Parse com `xlrd` → {ticker, qtd, preco_medio, total_investido}
3. Consolida duplicatas (mesmo ticker em múltiplas corretoras)
4. Separa Ações de FIIs
5. **Para ações**: busca valuation pré-calculado + preços em paralelo (10 workers)
6. **Para FIIs**: busca `dividends_sum_12m` via yfinance em paralelo (8 workers)
7. Calcula: valor_atual, retorno R$/%, DY s/PM

**Recomendações geradas:**
```
AUMENTAR     → zone COMPRA_FORTE + rank ≥ 12 + p_now_p_min ≤ 1.15
COMPRAR_MAIS → zone COMPRA ou COMPRA_FORTE + rank ≥ 9
AGUARDAR     → zone MONITORAR ou rank 6-8
AVALIAR_VENDA→ rank < 6 ou zone CARO
```

---

### 5.11 `api_server.py` — Flask + Scheduler

**Endpoints principais:**

| Endpoint | Método | Fonte | Descrição |
|----------|--------|-------|-----------|
| `/api/decision` | GET | decision_stocks.json | Lista principal de decisões |
| `/api/portfolio` | GET | B3 XLS + valuations | Carteira com análise |
| `/api/chart/<ticker>` | GET | yfinance (live) | OHLCV 6 meses para gráfico |
| `/api/history/<ticker>` | GET | stock_history.json | Histórico de dividendos/preços |
| `/api/valuation/<ticker>` | GET | valuations.json | Valuation detalhado |
| `/api/dividends_ytd/<ticker>` | GET | yfinance (live) | Dividendos acumulados no ano |
| `/api/favoritos` | GET/POST | favoritos.json | Lista de favoritos |
| `/api/radar` | GET/POST | radar.json | Alertas de preço |
| `/api/radar/alerts` | GET | radar + prices | Alertas disparados |
| `/api/radar/dismiss` | POST | radar.json | Silencia alerta por 24h |

**Scheduler:**
```python
# Daemon thread que roda em background
def _scheduler_loop():
    while True:
        decision_service.run()
        time.sleep(REFRESH_INTERVAL_HOURS * 3600)  # 30 min
```

---

## 6. Diagramas de Sequência

### Diagrama 1 — Pipeline de Inicialização (Execução Manual)

```
Operador          stock_validator   yfinance          repo              JSON
   │                    │               │               │                │
   │  validate_all()    │               │               │                │
   ├───────────────────►│               │               │                │
   │                    │ .history(6mo) │               │                │
   │                    ├──────────────►│               │                │
   │                    │◄── DataFrame ─┤               │                │
   │                    │               │               │                │
   │                    │     save_validity(ticker)     │                │
   │                    ├──────────────────────────────►│                │
   │                    │               │               ├── atomic_write►│ stock_validity.json
   │                    │               │               │                │
   │                    │               │               │                │
   │  update_all()      history_fetcher │               │                │
   ├───────────────────────────────────►│               │                │
   │                    │               │               │                │
   │                    │  .history(), .dividends,      │                │
   │                    │  .financials  │               │                │
   │                    │               ├──────────────►│                │
   │                    │               │◄── DataFrames ┤                │
   │                    │               │               │                │
   │                    │  StatusInvest: /acao/payoutresult              │
   │                    │               │               │                │
   │                    │         [buffett_fetcher]     │                │
   │                    │  yfinance cashflow, income    │                │
   │                    │  → FCF, OE, tendências 4a     │                │
   │                    │               │               │                │
   │                    │     save_history(ticker)      │                │
   │                    ├──────────────────────────────►│                │
   │                    │               │               ├── atomic_write►│ stock_history.json
   │                    │               │               │                │
   │  update_all()      financials_fetcher              │                │
   ├──────────────────────────────────────────────────► │                │
   │                    │     StatusInvest:             │                │
   │                    │     /getdre, /getativos,      │                │
   │                    │     /getfluxocaixa (10 anos)  │                │
   │                    │               │               │                │
   │                    │     yfinance: CapEx           │                │
   │                    │               │               │                │
   │                    │     save_financials(ticker)   │                │
   │                    ├──────────────────────────────►│                │
   │                    │               │               ├── atomic_write►│ financials_history.json
   │                    │               │               │                │
   │  calculate_all()   valuation_calc  │               │                │
   ├──────────────────────────────────────────────────► │                │
   │                    │    get_all_indicators()       │                │
   │                    ├──────────────────────────────►│                │
   │                    │    get_history()              │                │
   │                    ├──────────────────────────────►│                │
   │                    │    get_financials()           │                │
   │                    ├──────────────────────────────►│                │
   │                    │◄── indicadores + histórico ───┤                │
   │                    │                               │                │
   │                    │  calc_21_criteria()           │                │
   │                    │  calc_buffett_moat() ──── 3 fases              │
   │                    │  calc_piotroski()             │                │
   │                    │  calc_weighted_score()        │                │
   │                    │                               │                │
   │                    │     save_valuation(ticker)    │                │
   │                    ├──────────────────────────────►│                │
   │                    │               │               ├── atomic_write►│ valuations.json
   │                    │     save_monitoring_stocks()  │                │
   │                    ├──────────────────────────────►│                │
   │                    │               │               ├── atomic_write►│ monitoring_stocks.json
```

---

### Diagrama 2 — Ciclo de Decisão Automático (a cada 30 min)

```
Flask Scheduler    decision_service   PriceService   Google Finance   repo
      │                   │                │                │           │
      │  run()            │                │                │           │
      ├──────────────────►│                │                │           │
      │                   │  get_monitoring_stocks()        │           │
      │                   ├───────────────────────────────────────────►│
      │                   │◄── ~127 tickers ──────────────────────────┤
      │                   │                │                │           │
      │         [loop para cada ticker]    │                │           │
      │                   │                │                │           │
      │                   │  update(ticker)│                │           │
      │                   ├───────────────►│                │           │
      │                   │                │  GET /finance/quote/BVMF  │
      │                   │                ├───────────────►│           │
      │                   │                │◄── HTML preço ─┤           │
      │                   │                │  save_price()  │           │
      │                   │                ├────────────────────────── ►│
      │                   │◄── price_now ──┤                │           │
      │                   │                │                │           │
      │                   │  get_valuation() + get_history()            │
      │                   ├───────────────────────────────────────────►│
      │                   │◄── valuation{} + history{} ───────────────┤
      │                   │                │                │           │
      │                   │  _calc_zone(price_now, t6, t8, t5)         │
      │                   │  _calc p_now_p_min = price/min_6m          │
      │                   │  _calc gain_pct = (t6 - price)/price*100   │
      │                   │  _calc dy_real = avg_div/price*100         │
      │                   │  _calc_accumulation_30d() via yfinance     │
      │                   │  is_gold = below_vpa + below_t6 + div_grow │
      │                   │  is_bronze = below_t6 + not below_vpa      │
      │                   │  is_buffett_seal = moat≥7 + fcf_ok + oe_ok │
      │                   │  is_best = setor ∈ BEST                    │
      │                   │  [fim do loop]                              │
      │                   │                │                │           │
      │                   │  sort by p_now_p_min ASC                    │
      │                   │  save_decision_stocks()                     │
      │                   ├───────────────────────────────────────────►│
      │                   │               │                │            ├── atomic_write
      │                   │               │                │            │   decision_stocks.json
```

---

### Diagrama 3 — Requisição Frontend (Screening)

```
Browser           api_server      repo         decision_stocks.json
   │                   │            │                   │
   │  GET /api/decision│            │                   │
   ├──────────────────►│            │                   │
   │                   │  get_decision_stocks()         │
   │                   ├───────────►│                   │
   │                   │            │  read JSON        │
   │                   │            ├──────────────────►│
   │                   │            │◄── JSON data ─────┤
   │                   │◄── data[] ─┤                   │
   │◄── JSON ~127 stocks───────────┤                   │
   │                   │            │                   │
   │  renderScreening(data)         │                   │
   │  aplica filtros ativos         │                   │
   │  (zona, medalha, BEST, etc.)   │                   │
   │  renderiza tabela:             │                   │
   │    - badges coloridos (zona)   │                   │
   │    - barra Dist.Mín com cores  │                   │
   │    - medalhas/selos            │                   │
   │    - cards de resumo clicáveis │                   │
```

---

### Diagrama 4 — Carregamento da Carteira

```
Browser   api_server   portfolio_service   repo    ThreadPool   yfinance   Google Finance
   │           │               │             │         │            │            │
   │  GET /api/portfolio        │             │         │            │            │
   ├──────────►│               │             │         │            │            │
   │           │  load()        │             │         │            │            │
   │           ├──────────────►│             │         │            │            │
   │           │               │  parse B3 XLS (xlrd)  │            │            │
   │           │               │  consolidar tickers    │            │            │
   │           │               │  separar Ações / FIIs  │            │            │
   │           │               │             │         │            │            │
   │           │               │  get_valuation(t)       │            │            │
   │           │               ├────────────►│         │            │            │
   │           │               │◄── val{} ───┤         │            │            │
   │           │               │             │         │            │            │
   │           │               │  [10 workers paralelos — preços]   │            │
   │           │               ├────────────────────────►│          │            │
   │           │               │             │         │  price_service.update() │
   │           │               │             │         ├────────────────────────►│
   │           │               │             │         │◄── price_now ──────────┤
   │           │               │◄── prices[] ┤         │            │            │
   │           │               │             │         │            │            │
   │           │               │  [8 workers paralelos — FII dividendos]         │
   │           │               ├────────────────────────────────────►│            │
   │           │               │             │         │  .dividends(12m)        │
   │           │               │◄── div_sum[]┤         │            │            │
   │           │               │             │         │            │            │
   │           │               │  calc: retorno, DY s/PM, recomendações          │
   │           │◄── portfolio{} ┤             │         │            │            │
   │◄── JSON ──┤               │             │         │            │            │
```

---

## 7. Cálculos e Métricas Detalhadas

### 7.1 Alvo Bazin e Zonas de Preço (Sinal)

**Fórmula central de Bazin:**
```
Alvo 6% = avg_dividends_5y / 0.06   → zona COMPRA
Alvo 8% = avg_dividends_5y / 0.08   → zona COMPRA_FORTE  
Alvo 5% = avg_dividends_5y / 0.05   → zona MONITORAR
```

**Cálculo da média ponderada de dividendos (5 anos):**
```python
# Pesos: mais recente tem maior peso
# Ordem: [ano-4, ano-3, ano-2, ano-1, ano-0]
pesos = [1, 2, 3, 4, 5]

# Exemplo: dividendos de 2021=0.5, 2022=0.6, 2023=0.7, 2024=0.8, 2025=0.9
weighted_avg = (0.5×1 + 0.6×2 + 0.7×3 + 0.8×4 + 0.9×5) / (1+2+3+4+5)
             = (0.5 + 1.2 + 2.1 + 3.2 + 4.5) / 15
             = 11.5 / 15
             = 0.767
```

**Por que 6%?** Bazin definiu 6% como a taxa mínima de atratividade para renda variável frente à renda fixa. Abaixo disso, o risco não se justifica.

**Por que 8%?** Barsi usa o alvo a 8% como sinal de compra agressiva — quando o mercado oferece esse yield, a assimetria risco/retorno é excepcional.

**Zonas e classificação:**

| Zona | Condição | Yield Implícito | Cor |
|------|---------|----------------|-----|
| `COMPRA_FORTE` | preço ≤ alvo 8% | ≥ 8% | Verde Vivo |
| `COMPRA` | alvo 8% < preço ≤ alvo 6% | 6–8% | Verde |
| `MONITORAR` | alvo 6% < preço ≤ alvo 5% | 5–6% | Amarelo |
| `CARO` | preço > alvo 5% | < 5% | Vermelho |

```python
# Código real (decision_service.py e valuation_calculator.py)
def _calc_zone(price_now, target_6, target_8, target_5):
    if target_8 and price_now <= target_8:
        return "COMPRA_FORTE"
    if target_6 and price_now <= target_6:
        return "COMPRA"
    if target_5 and price_now <= target_5:
        return "MONITORAR"
    return "CARO"
```

---

### 7.2 Potencial de Valorização (gain_pct)

**Coluna:** `Potencial (%)`

```python
gain_pct = ((price_target_6pct - price_now) / price_now) * 100
```

**Interpretação:**
- **Positivo (+%)**: ação está abaixo do alvo — há potencial de valorização até o preço justo
- **Negativo (-%)**: ação está acima do alvo — "cara" pelo critério Bazin

**Exemplo:**
```
avg_dividends_5y = R$ 0.90/ano
alvo_6pct = 0.90 / 0.06 = R$ 15.00

Preço atual = R$ 12.00
Potencial = (15.00 - 12.00) / 12.00 × 100 = +25.0%

Preço atual = R$ 17.00
Potencial = (15.00 - 17.00) / 17.00 × 100 = -11.8%
```

**Cor no frontend:** verde se positivo, vermelho se negativo.

---

### 7.3 Distância do Mínimo (Dist. Mín. / p_now_p_min)

**Coluna:** `Dist. Mín.`

```python
p_now_p_min = price_now / price_min_6m
```

**Por que é importante:** Barsi compra na queda — quanto mais próximo do mínimo recente, melhor o ponto de entrada. Um ativo que está 5% acima do fundo de 6 meses representa excelente assimetria.

**Interpretação visual:**

| Valor | Cores (barra) | Significado |
|-------|-------------|------------|
| ≤ 1.05 | 🟢 Verde vivo | Máximo 5% acima do mínimo — entrada excelente |
| ≤ 1.20 | 🟢 Verde | 5–20% acima — boa entrada |
| ≤ 1.40 | 🟡 Amarelo | 20–40% acima — entrada moderada |
| ≤ 1.60 | 🟠 Laranja | 40–60% acima — entrada fraca |
| > 1.60 | 🔴 Vermelho | > 60% acima — aguardar correção |

**Escala da barra:** usa raiz quadrada para realçar diferenças perto de 1.0 (o ponto mais relevante) e comprimir os valores altos.

```javascript
// Frontend: ratioBarWidth()
const norm = Math.max(0, v - 0.85) / 1.35;
return Math.min(Math.max(Math.sqrt(norm) * 100, 5), 100);
```

---

### 7.4 Score Ponderado (0–100)

**Coluna:** `Score`

O Score agrega 21 critérios binários com pesos diferenciados pela importância relativa de cada dimensão de qualidade.

**Critérios e Pesos:**

| # | Critério | Flag | Limiar | Peso | Filosofia |
|---|---------|------|--------|------|-----------|
| 1 | ROE | `roe_ok` | ≥ 10% | **3.0** | Graham/Buffett |
| 2 | ROIC | `roic_ok` | ≥ 10% | **3.0** | Greenblatt/Buffett |
| 3 | Margem EBIT | `margem_ebit_ok` | ≥ 10% | **3.0** | Graham |
| 4 | Margem Líquida | `margem_liq_ok` | ≥ 10% | **3.0** | Graham |
| 5 | CAGR Receita 5a | `cagr_receita_ok` | ≥ 5% | 2.0 | Lynch/Graham |
| 6 | CAGR Lucro 5a | `cagr_lucro_ok` | ≥ 5% | 2.0 | Lynch |
| 7 | Dividendo Crescente | `dividendo_crescente_ok` | último ≥ 90% máx anterior | 2.0 | Barsi |
| 8 | DL/PL | `dl_pl_ok` | ≤ 1.0 | 2.0 | Bazin/Graham |
| 9 | DL/EBITDA | `dl_ebitda_ok` | ≤ 3.0 | 2.0 | Bazin |
| 10 | Passivo/Ativo | `passivo_ativo_ok` | ≤ 65% | 2.0 | Graham |
| 11 | Liquidez Corrente | `liquidez_corrente_ok` | ≥ 2.0 | 2.0 | Graham |
| 12 | P/L | `p_l_ok` | ≤ 15 | 1.5 | Graham |
| 13 | P/VP | `p_vp_ok` | ≤ 1.5 | 1.5 | Graham |
| 14 | Graham Combo | `graham_combo_ok` | P/L × P/VP ≤ 22.5 | 1.5 | Graham |
| 15 | Abaixo VPA | `abaixo_vpa` | preço ≤ VPA | 1.5 | Graham/Barsi |
| 16 | DY Real | `dy_ok` | ≥ 6% | 1.5 | Barsi/Bazin |
| 17 | Abaixo Alvo 6% | `abaixo_target_6pct` | preço ≤ alvo 6% | 1.5 | Bazin/Barsi |
| 18 | Abaixo Alvo 8% | `abaixo_target_8pct` | preço ≤ alvo 8% | 1.5 | Barsi |
| 19 | Payout | `payout_ok` | 40–80% | 1.5 | Bazin |
| 20 | Liquidez Diária | `liquidez_diaria_ok` | ≥ R$200k/dia | 1.0 | Bazin |
| 21 | Acumulação Silenciosa | `accumulation_ok` | ≥ 50% | 1.0 | Barsi |

**Fórmula:**
```python
WEIGHTED_SCORE_MAX = 40.0  # soma de todos os pesos

earned_points = sum(weight for flag, weight in WEIGHTS.items() if flag_value[flag] == True)
weighted_score = (earned_points / 40.0) * 100
```

**Interpretação:**
- ≥ 65%: Verde — qualidade excelente
- 40–65%: Amarelo — qualidade moderada
- < 40%: Vermelho — qualidade baixa

> **Nota:** O critério `liquidez_corrente_ok` e `passivo_ativo_ok` são isentos para empresas do setor financeiro (bancos, seguradoras), pois seu modelo de negócio é estruturalmente diferente.

---

### 7.5 Piotroski F-Score (0–9)

**Coluna:** `Saúde`

9 sinais binários de saúde financeira, adaptados aos dados disponíveis.

**Grupo 1 — Lucratividade (3 sinais):**

| Sinal | Condição | Fonte |
|-------|---------|-------|
| P1 | Lucro Líquido > 0 (ano mais recente) | `net_income_per_year` (yfinance) |
| P2 | Margem EBIT > 0 (proxy de caixa operacional positivo) | `all_indicators.json` |
| P3 | Lucro mais recente > lucro do ano anterior | `net_income_per_year` (yfinance) |

**Grupo 2 — Alavancagem/Liquidez (3 sinais):**

| Sinal | Condição | Limiar | Filosofia |
|-------|---------|--------|-----------|
| P4 | DL/PL conservador | ≤ 0.5 (metade do limite principal de 1.0) | Conservador |
| P5 | Liquidez Corrente sólida | ≥ 1.5 (entre Graham 2.0 e o mínimo) | Piotroski |
| P6 | Balanço conservador | Passivo/Ativo ≤ 0.4 (abaixo de 40%) | Conservador |

**Grupo 3 — Eficiência/Qualidade (3 sinais):**

| Sinal | Condição | Significado |
|-------|---------|------------|
| P7 | CAGR Lucro > CAGR Receita | Margens se expandindo — empresa mais eficiente |
| P8 | CAGR Receita > 0% | Crescimento real de receita (não deflação de custos) |
| P9 | ROE ≥ 15% | Rentabilidade forte (acima do mínimo básico de 10%) |

**Classificação:**
- ≥ 7 → **FORTE** (verde) — empresa financeiramente saudável
- 4–6 → **MODERADO** (amarelo)
- ≤ 3 → **FRACO** (vermelho)

---

### 7.6 Buffett Moat Score (0–10)

**Coluna:** `MOAT`

Mede a presença e durabilidade da **vantagem competitiva** do negócio, usando proxies financeiros de 3 fases.

#### Fase 1 — Critérios Base (0–10 pontos)

| Critério | Limiar | Peso | Por que Buffett usa |
|---------|--------|------|-------------------|
| Margem Bruta | ≥ 40% | **2** | Empresas com moat mantêm pricing power — poucos concorrentes conseguem destruir a margem bruta |
| Margem Líquida | ≥ 20% | 1 | Padrão Buffett (vs. 10% do screening básico) — lucro real após todos os custos |
| ROE | ≥ 20% | **2** | Eficiência na conversão de capital em lucro — o melhor indicador de moat econômico |
| ROIC | ≥ 15% | 1 | Retorno sobre capital investido — moat = capital gera retorno acima do custo |
| DL/PL | ≤ 0.5 | 1 | Empresa com moat real não precisa de alavancagem para crescer |
| CAGR Lucro 5a | ≥ 10% | 1 | Crescimento acima da inflação — moat mantém precificação acima dos custos |
| CAGR Receita 5a | ≥ 5% | 1 | Crescimento consistente de receita — precificação e expansão sustentáveis |
| Dividendo crescente | — | 1 | Sinal estrutural de geração de caixa sustentável |

**Score máximo Fase 1:** 10 pontos

#### Fase 2 — Validação de Caixa (Informacional, não afeta score)

Flags que enriquecem a análise mas não entram no score diretamente:

| Flag | Condição | Significado |
|------|---------|------------|
| `fcf_positivo` | FCF > 0 | Empresa gera caixa real (não apenas lucro contábil) |
| `owner_earnings_positivo` | OE > 0 | Lucro disponível para o dono após manter capacidade produtiva |
| `fcf_quality_ok` | FCF/Lucro ≥ 80% | Alta qualidade de lucro — 80%+ converte em caixa real |
| `capex_moat_ok` | CapEx/Lucro ≤ 25% | Moat = não precisa reinvestir muito para manter posição |

#### Fase 3 — Modificadores de Tendência (±0.5 por critério)

Aplicados sobre o score da Fase 1 com base em tendências históricas de 4-10 anos (regressão linear):

| Situação | Ajuste | Lógica |
|---------|--------|--------|
| Margem Bruta aprovada + tendência **CAINDO** | −0.5 | Moat erodindo silenciosamente — pricing power diminuindo |
| Margem Bruta reprovada + tendência **CRESCENDO** | +0.5 | Moat em construção — empresa ganhando poder de preço |
| ROE aprovado + tendência **CAINDO** | −0.5 | Eficiência de capital se deteriorando |
| ROE reprovado + tendência **CRESCENDO** | +0.5 | Eficiência de capital melhorando |
| FCF tendência **CAINDO** | −0.5 | Geração de caixa diminuindo — moat questionável |
| FCF reprovado + tendência **CRESCENDO** | +0.5 | FCF melhorando (bônus só se FCF era negativo) |

**Score final:** `clamp(score_fase1 + modificadores, 0, 10)`

**Classificação:**
- ≥ 7 → **FORTE** (verde) — vantagem competitiva durável provável
- 4–6 → **MODERADO** (amarelo) — moat parcial ou em desenvolvimento
- ≤ 3 → **FRACO** (vermelho) — sem evidência de moat

> **Aviso:** `data_confidence_low = True` quando score é FORTE mas há menos de 6 anos de histórico disponível.

---

### 7.7 FCF/Lucro — Qualidade do Lucro

**Coluna:** `FCF/L`

```python
FCF = FCO (Fluxo de Caixa Operacional) - |CapEx|
fcf_lucro_ratio = FCF / Lucro_Liquido * 100
```

**Por que é importante:** O lucro contábil pode ser "inflado" por receitas não-caixa, reconhecimento antecipado de receita, ou consumo de capital de giro. O FCF é o caixa real gerado. Se FCF/Lucro < 50%, o lucro é de baixa qualidade.

**Interpretação:**

| Faixa | Cor | Significado |
|-------|-----|------------|
| ≥ 80% | 🟢 Verde | Excelente — lucro é essencialmente caixa real |
| 50–80% | 🟡 Amarelo | Bom — maior parte do lucro é caixa real |
| < 50% | 🔴 Vermelho | Atenção — grande parte do lucro não vira caixa |

**Padrão Buffett:** FCF/Lucro ≥ 80% como referência de alta qualidade de lucro (`BUFFETT_FCF_QUALITY_MIN = 0.80`).

---

### 7.8 Acumulação Silenciosa (Estratégia Barsi)

**Colunas:** `Acum. 6m (%)` e `Acum. 30d`

Barsi identifica o melhor momento de compra observando quando **"mãos fortes" (institucionais) acumulam silenciosamente**: quando o preço E o volume estão ambos abaixo da média — o mercado está desinteressado, mas alguém está comprando devagar.

**Acum. 6m:**
```python
# Para cada dia nos últimos 6 meses:
cond = (Close < close_avg_6m) AND (Volume < volume_avg_6m)
accumulation_score = (dias_cond_true / total_dias) * 100
```

**Acum. 30d:**
```python
# Mesmo critério, janela de 1 mês (≈ 21-23 pregões)
df = yfinance.Ticker(f"{ticker}.SA").history(period="1mo")
cond = (df["Close"] < close_avg_6m) & (df["Volume"] < volume_avg_6m)
accumulation_30d_days = int(cond.sum())
accumulation_30d_total = len(df)
```

**Interpretação:**
- ≥ 60%: Verde — acumulação forte (mais da metade dos dias com condição)
- 40–60%: Amarelo — acumulação moderada
- < 40%: Cinza — sem sinal claro de acumulação

---

## 8. Sistema de Medalhas e Selos

### 8.1 Medalha de Ouro 🥇 — Ouro Barsi

**A combinação mais rara e favorável.** Reúne os três melhores critérios ao mesmo tempo.

**Critérios (TODOS obrigatórios):**
```python
is_below_vpa    = price_now <= vpa               # Margem de segurança patrimonial
below_target_6  = price_now <= price_target_6pct  # Zona de compra Bazin
dividend_growing = latest_div >= 0.90 * max_prior_div  # Dividendo crescente (10% tolerância)

is_gold = is_below_vpa AND below_target_6 AND dividend_growing
```

**Por que é especial:**
- **Preço ≤ VPA**: o mercado está vendendo o negócio abaixo do valor do patrimônio — desconto sobre o patrimônio líquido
- **Preço ≤ Alvo 6%**: yield atual implícito ≥ 6% — atrativo por dividendo
- **Dividendo crescente**: a empresa não está apenas pagando dividendo — ela está **crescendo** o dividendo, sinal de saúde do caixa

Tooltip: *"Ouro Barsi: Valor atual abaixo VPA e do Alvo Bazin e com dividendos crescente. Preço baixo, dividendo sustentável e em crescimento — conjunto mais favorável."*

---

### 8.2 Medalha de Prata 🥈 — Margem Dupla

**Critérios (TODOS obrigatórios, sem exigir crescimento de dividendo):**
```python
is_below_vpa_target = price_now <= vpa AND price_now <= price_target_6pct
is_silver = is_below_vpa_target AND NOT is_gold
```

**Por que é valiosa:**
- **Margem de segurança dupla**: desconto patrimonial (preço < VPA) + yield atraente (preço < alvo 6%)
- É a combinação clássica de Graham + Bazin: barato e com renda

Tooltip: *"Prata: Valor abaixo do VPA e do Alvo Bazin 6%. Margem de segurança dupla: desconto patrimonial e preço dentro da zona de compra por dividendos."*

---

### 8.3 Medalha de Bronze 🥉 — Atrativo por Dividendo

**Critérios:**
```python
is_bronze = price_now <= price_target_6pct AND price_now > vpa
```

**Por que é válida:**
- Está na zona de compra Bazin (yield implícito ≥ 6%)
- MAS não tem desconto ao valor patrimonial (preço > VPA)
- Empresa de qualidade que o mercado já reconhece — entrada válida com menos margem

Tooltip: *"Bronze: Abaixo do Alvo Bazin 6%, porém acima do VPA. Atrativo por dividendos, sem desconto sobre o valor patrimonial."*

---

### 8.4 Selo Buffett ★ — Excelência de Negócio

**A insígnia de qualidade máxima.** Pode coexistir com qualquer medalha ou sem medalha.

**Critérios (TODOS obrigatórios):**
```python
is_buffett_seal = (
    buffett_moat.get("score", 0) >= 7           # Moat FORTE
    and buffett_cf.get("fcf_quality_ok", False)  # FCF/Lucro >= 80%
    and buffett_cf.get("owner_earnings_positivo", False)  # OE > 0
)
```

**Por que 3 condições:**
1. **Moat FORTE (≥ 7)**: a empresa tem vantagem competitiva durável que protege os lucros
2. **FCF quality OK**: o lucro reportado é real — ≥ 80% converte em caixa
3. **Owner Earnings > 0**: após manter toda a capacidade produtiva, ainda sobra caixa para o dono

> **Combinação possível:** É possível ter Selo Buffett em uma ação CARO (acima do alvo). Isso significa empresa excepcional, mas ainda não com preço atrativo pelo critério de dividendo. Nesse caso, aguardar correção.

Tooltip: *"Selo Buffett: Moat FORTE com FCF positivo e Owner Earnings positivo. Empresas com vantagem competitiva durável e geração de caixa de alta qualidade."*

---

### 8.5 Filtro BEST — Setores Barsi

Barsi concentra capital em setores com **demanda inelástica** — empresas que as pessoas precisam mesmo em crises.

**Setores BEST implementados:**

```python
def _is_best(sector_info):
    sub = sector_info.get("subsetor", "")
    seg = sector_info.get("segmento", "")
    
    if seg == "Bancos":            return True  # B — Bancos
    if sub == "Energia Elétrica":  return True  # E — Elétricas (geração, distribuição, transmissão)
    if sub == "Água e Saneamento": return True  # S — Saneamento
    if sub == "Previdência e Seguros" or "Segur" in seg: return True  # S — Seguros
    return False
```

**Por que esses setores:**
- **Bancos**: lucram com o crédito da economia inteira, regulados, resilientes
- **Elétricas/Transmissão**: monopólios naturais com contratos de longo prazo regulados pela ANEEL
- **Saneamento**: demanda inelástica (SAPR11, SBSP3, CSMG3) — ninguém para de usar água
- **Seguros/Previdência**: receita previsível, float de investimentos (modelo Buffett)

---

## 9. Páginas da Aplicação

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
| `Score` | `weighted_score` | Score ponderado 0-100 |
| `MOAT` | `buffett_moat_score` | Score Buffett Moat 0-10 |
| `Saúde` | `piotroski_score` | Piotroski F-Score 0-9 |
| `FCF/L` | `fcf_lucro_ratio` | FCF / Lucro Líquido (qualidade) |
| `Acum. 6m (%)` | `accumulation_score` | % dias em acumulação Barsi |
| `Acum. 30d` | `accumulation_30d_days` | Dias de acumulação último mês |
| `Sinal` | `zone` | Badge colorido: FORTE / COMPRA / AGUARDAR / ACIMA |

**Filtros disponíveis:**

| Filtro | Ação |
|--------|-----|
| Por zona | FORTE / COMPRA / AGUARDAR / ACIMA (clique nos cards) |
| Ocultar CARO | Toggle para esconder ações acima do alvo |
| 🥇 Gold Only | Apenas medalha ouro |
| 🥈 Silver Only | Apenas abaixo VPA + alvo |
| 🥉 Bronze Only | Apenas abaixo do alvo (acima VPA) |
| ★ Buffett | Apenas com Selo Buffett |
| BEST | Apenas setores Barsi |

**Barra de resumo:** 10 cards clicáveis mostrando contagem por categoria (total, zonas, medalhas, BEST).

---

### 9.2 Carteira — Gestão de Posições

**Propósito:** Acompanhar posições reais com análise integrada.

**Fonte de dados:** Arquivo XLS de custódia exportado da B3 (`data/B3/Custodia*.xls`).

#### Sub-aba Ações

| Coluna | Campo JSON | Descrição |
|--------|-----------|-----------|
| `Ativo` | `ticker` | Ticker |
| `Qtd` | `qtd` | Quantidade de ações |
| `PT %` | `pt_pct` | % do portfólio total |
| `PM (R$)` | `preco_medio` | Preço médio de compra |
| `Preço (R$)` | `preco_atual` | Preço atual |
| `Investido (R$)` | `total_investido` | Total investido (Qtd × PM) |
| `Valor (R$)` | `valor_atual` | Valor atual (Qtd × Preço) |
| `Retorno (R$)` | `retorno` | Lucro/prejuízo em R$ |
| `Retorno (%)` | `retorno_pct` | Lucro/prejuízo em % |
| `DY s/PM (%)` | `dy_on_cost` | Dividend Yield calculado sobre o PM |
| `Score` | `weighted_score` | Score de qualidade |
| `MOAT` | `buffett_moat_score` | Moat score |
| `Saúde` | `piotroski_score` | Piotroski |
| `FCF/L` | `fcf_lucro_ratio` | Qualidade do lucro |
| `Sinal` | `zone` | Zona de preço atual |

**DY sobre PM:** `avg_dividends_5y / preco_medio * 100`  
É o yield que o investidor está **realmente recebendo** sobre o capital investido — não sobre o preço atual.

#### Sub-aba FIIs

Mesmas colunas posicionais, acrescentando:
- `DY Real (%)` — yield calculado sobre o preço atual
- `DY s/PM (%)` — yield calculado sobre o preço médio de compra

---

### 9.3 Favoritos — Lista Personalizada

**Propósito:** Curadoria pessoal de ativos com visualização rápida.

**Gerenciamento:** Ícone de coração (❤️) na tela de Screening adiciona/remove da lista. Persiste em `favoritos.json`.

**Modo Card:** cada ativo exibe:
- Ticker + badges (zona, selos)
- Preço atual + Potencial
- Score + DY
- Piotroski + MOAT
- Setor/Segmento

**Modo Tabela:** versão compacta com as mesmas informações em linha.

---

### 9.4 Radar — Alertas de Preço

**Propósito:** Monitorar ativos específicos com gatilhos automáticos de preço.

**Configuração por ativo:**
- **Alerta Compra (≤):** dispara quando preço cai abaixo do valor configurado
- **Alerta Venda (≥):** dispara quando preço sobe acima do valor configurado

**Verificação de alertas:**
```
GET /api/radar/alerts
  → Busca preços frescos para todos os itens do radar
  → Compara com limiares configurados
  → Retorna alertas disparados
```

**Dismissal:** `POST /api/radar/dismiss` silencia um alerta por 24 horas sem removê-lo.

**Persistência:** `radar.json` com histórico de disparos e timestamps de dismissal.

---

## 10. Tabela de Referência — Todos os Limiares

### Bazin/Barsi — Dividendos

| Parâmetro | Valor | Constante | Filosofia |
|-----------|-------|-----------|-----------|
| Yield mínimo (zona MONITORAR) | 5% | `BASIN_MIN = 0.05` | Barsi |
| Yield base (zona COMPRA) | 6% | `BASIN_BASE = 0.06` | Bazin/Barsi |
| Yield agressivo (COMPRA_FORTE) | 8% | `BASIN_MAX = 0.08` | Barsi |
| DY% mínimo aprovado | 6% | `DIVIDEND_YIELD_MIN = 6.0` | Bazin |
| Payout mínimo saudável | 40% | `PAYOUT_MIN = 40.0` | Bazin |
| Payout máximo saudável | 80% | `PAYOUT_MAX = 80.0` | Bazin |
| Anos mínimos com dividendo | 5 | `DIVIDEND_YEARS_MIN = 5` | Barsi/Bazin |

### Graham — Valuation

| Parâmetro | Valor | Constante | Filosofia |
|-----------|-------|-----------|-----------|
| P/L máximo | 15 | `P_L_MAX = 15.0` | Graham |
| P/VP máximo | 1.5 | `P_VP_MAX = 1.5` | Graham |
| Graham Combo máximo | 22.5 | `GRAHAM_COMBO = 22.5` | Graham |
| Liquidez Corrente mínima | 2.0 | `LIQUIDEZ_CORRENTE_MIN = 2.0` | Graham |
| DL/PL máximo | 1.0 | `DL_PL_MAX = 1.0` | Bazin/Graham |
| DL/EBITDA máximo | 3.0 | `DL_EBITDA_MAX = 3.0` | Bazin |
| Passivo/Ativo máximo | 65% | `PASSIVO_ATIVO_MAX = 0.65` | Graham |

### Qualidade — Rentabilidade

| Parâmetro | Valor | Constante |
|-----------|-------|-----------|
| Margem EBIT mínima | 10% | `MARGEM_EBIT_MIN = 10.0` |
| Margem Líquida mínima | 10% | `MARGEM_LIQ_MIN = 10.0` |
| ROE mínimo | 10% | `ROE_MIN = 10.0` |
| ROIC mínimo | 10% | `ROIC_MIN = 10.0` |
| CAGR Receita 5a mínimo | 5% | `CAGR_RECEITA_MIN = 5.0` |
| CAGR Lucro 5a mínimo | 5% | `CAGR_LUCRO_MIN = 5.0` |

### Buffett Moat — Padrões Mais Exigentes

| Parâmetro | Valor | vs. Screening Básico |
|-----------|-------|---------------------|
| Margem Bruta mínima (moat) | 40% | vs. não há no screening |
| Margem Líquida mínima (moat) | 20% | vs. 10% no screening |
| ROE mínimo (moat) | 20% | vs. 10% no screening |
| ROIC mínimo (moat) | 15% | vs. 10% no screening |
| DL/PL máximo (moat) | 0.5 | vs. 1.0 no screening |
| CAGR Lucro (moat) | ≥ 10% | vs. 5% no screening |
| FCF Quality mínimo | 80% | `BUFFETT_FCF_QUALITY_MIN = 0.80` |
| CapEx/Lucro máximo (moat) | 25% | `BUFFETT_CAPEX_MOAT_MAX = 0.25` |

### Piotroski — Limiares Conservadores

| Sinal | Limiar | vs. Screening principal |
|-------|--------|------------------------|
| DL/PL (P4) | ≤ 0.5 | vs. 1.0 |
| Liquidez Corrente (P5) | ≥ 1.5 | vs. 2.0 (Graham) |
| Passivo/Ativo (P6) | ≤ 40% | vs. 65% |
| ROE forte (P9) | ≥ 15% | vs. 10% |

### Técnico/Liquidez

| Parâmetro | Valor | Constante |
|-----------|-------|-----------|
| Liquidez diária mínima | R$200k/dia | `LIQUIDEZ_DIARIA_MIN = 200000.0` |
| Acumulação mínima | 50% | `ACCUMULATION_SCORE_MIN = 50.0` |
| Atualização de preço | 30 min | `PRICE_UPDATE_INTERVAL_HOURS = 0.5` |
| Atualização histórico | 7 dias | `HISTORY_UPDATE_INTERVAL_DAYS = 7` |
| Atualização financials | 30 dias | `FINANCIALS_UPDATE_INTERVAL_DAYS = 30` |

---

## 11. Fontes de Dados Externas

### 11.1 Google Finance — Preços em Tempo Real

```
URL:    https://www.google.com/finance/quote/{TICKER}:BVMF
Método: Scraping HTML
Extração: CSS class "YMlKec fxKbKc"
Regex:  r'[\d]+[.,][\d]+'
Formato: vírgula ou ponto como separador decimal (tratado)
Cache:  30 minutos
Risco:  frágil (classe CSS pode mudar a qualquer momento)
```

### 11.2 Yahoo Finance (yfinance)

Biblioteca Python que wrappa a API não oficial do Yahoo Finance.

| Método | Dados Retornados | Usado em |
|--------|-----------------|---------|
| `Ticker.history(period="6mo")` | OHLCV 6 meses | history_fetcher, decision_service |
| `Ticker.history(period="1mo")` | OHLCV 1 mês | decision_service (acum. 30d) |
| `Ticker.dividends` | Série histórica de dividendos | history_fetcher |
| `Ticker.financials["Net Income"]` | Lucro líquido anual 4-5 anos | history_fetcher |
| `Ticker.cashflow` | FCO, CapEx, D&A, FCF | buffett_fetcher |
| `Ticker.income_stmt` | Receita, EBIT, Net Income 4a | buffett_fetcher (tendências) |
| `Ticker.balance_sheet` | Dívida, PL, Ativos 4a | buffett_fetcher (tendências) |

> **Nota:** Todos os tickers B3 recebem o sufixo `.SA` no yfinance. Ex: `yfinance.Ticker("BBAS3.SA")`

### 11.3 StatusInvest — API Não Oficial

StatusInvest é uma plataforma de análise de ações brasileira. A aplicação usa endpoints não documentados observados via inspeção de rede.

| Endpoint | Dados | Usado em | Rate Limit |
|----------|-------|---------|-----------|
| `/acao/payoutresult?code={t}` | Payout ratio atual | history_fetcher | 1.5s |
| `/acao/getdre?code={t}&range.min={y}&range.max={y}` | DRE 10 anos | financials_fetcher | 1.5s |
| `/acao/getativos?code={t}&range.min={y}&range.max={y}` | Balanço 10 anos | financials_fetcher | 1.5s |
| `/acao/getfluxocaixa?code={t}&range.min={y}&range.max={y}` | Cashflow 10 anos | financials_fetcher | 1.5s |

**Headers obrigatórios:**
```python
headers = {
    "User-Agent": "Mozilla/5.0 ...",
    "Accept": "application/json",
    "Referer": "https://statusinvest.com.br/"
}
```

**`all_indicators.json`:** arquivo exportado manualmente do StatusInvest contendo 36+ indicadores fundamentalistas por ação (~615 tickers B3). Atualização manual periódica.

### 11.4 B3 — Arquivo de Custódia

Arquivo XLS exportado manualmente do portal da B3 (CEI ou plataforma da corretora), contendo todas as posições do investidor.

```
Local: data/B3/Custodia*.xls
Leitura: xlrd (Python)
Campos: ticker, quantidade, preço médio, total investido
Atualização: manual (download do portal B3)
```

---

## 12. Limitações e Considerações Conhecidas

### 12.1 CapEx Total vs. Manutenção

**Problema:** A aplicação usa o **CapEx total** (manutenção + expansão) para calcular FCF e Owner Earnings. Para empresas em forte fase de crescimento (ex: WEGE3), o CapEx de expansão é alto — isso **sub-estima** o Owner Earnings e pode gerar um score de qualidade injustamente baixo.

**Impacto estimado:** até 17% de distorção negativa em empresas de alto crescimento.

**Solução ideal:** separar CapEx de manutenção (maintenance capex) do CapEx de crescimento. Isso exige estimativas qualitativas ou dados de notas de demonstrações.

### 12.2 Moat por Proxies Financeiros

O Buffett Moat Score mede **sintomas financeiros de moat** (altas margens, ROE elevado), mas não a **causa estrutural** do moat. Os verdadeiros moats de Buffett são:

- **Switching costs**: custo alto de trocar de fornecedor (ex: SAP, Oracle)
- **Network effects**: valor cresce com usuários (ex: bolsas, redes sociais)
- **Intangibles**: marcas, patentes, licenças regulatórias
- **Cost advantages**: escala, propriedade única de recursos

Uma empresa pode ter moat estrutural e margens baixas hoje (early stage), ou pode ter margens altas por conjuntura (sem moat durável). O score atual não diferencia esses casos.

### 12.3 Fonte Única de Dados Fundamentalistas

`all_indicators.json` vem exclusivamente do StatusInvest. Sem cross-validação com outras fontes. Se o StatusInvest tiver um dado errado, todos os cálculos baseados nele serão afetados. **Alertas:** verificar valores outliers no Screening.

### 12.4 Setores Financeiros — Critérios Diferentes

Bancos e seguradoras têm modelos de negócio onde **alta alavancagem é estrutural** (captam barato, emprestam caro). Por isso, dois critérios são isentos para esses setores:

- `liquidez_corrente_ok`: inaplicável — bancos têm passivo circulante (depósitos) > ativo circulante por design
- `passivo_ativo_ok`: inaplicável — alavancagem de 10-20x é normal e regulada pelo Banco Central

**Identificação:** `FINANCIAL_PL_ATIVO_MAX = 0.20` — se PL/Ativo ≤ 20%, a empresa é tratada como financeira.

### 12.5 Sem Testes Automatizados sobre Lógica de Negócio

Existe `test_price_service.py`, mas não há testes cobrindo:
- Cálculo dos 21 critérios
- Buffett Moat Score
- Piotroski F-Score
- Lógica de medalhas

**Risco:** mudanças em `valuation_calculator.py` podem introduzir regressões silenciosas.

### 12.6 Frágil Dependência do Google Finance

O scraping do Google Finance depende de uma classe CSS (`YMlKec fxKbKc`) que pode mudar sem aviso. Se o Google mudar o HTML, a coleta de preços para completamente. Mitigação: verificar logs de `PriceService` regularmente.

---

*Documento gerado em Abril de 2026 com base no código fonte da branch `decision-making-improvements`.*
