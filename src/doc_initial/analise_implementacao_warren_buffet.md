# Warren Buffett e a Análise de Balanços — Plano de Implementação

> Baseado no livro *Warren Buffett and the Interpretation of Financial Statements* de Mary Buffett e David Clark.
> Data da análise: 2026-03-19

---

## Status de Implementação

| Fase | Status | Data |
|------|--------|------|
| **Fase 1** — Buffett Moat Score com dados existentes | ✅ Implementado | 2026-03-19 |
| **Fase 2** — Integração yfinance (FCF, Owner Earnings, CapEx) | ✅ Implementado | 2026-03-19 |
| **Fase 3** — Tendências históricas 4 anos | ✅ Implementado | 2026-03-20 |
| **Fase 4** — Frontend visual expandido + SG&A | ✅ Implementado | 2026-03-20 |

### O que foi implementado na Fase 1

- `_calc_buffett_moat_score()` em `valuation_calculator.py` — 8 critérios, score 0-10
- Coluna **Score MOAT** na tabela de screening e carteira (ao lado de Score)
- **MOAT** no card do modal (elemento periódico), ao lado de Score e Saúde
- Seção **Buffett Moat Score** no modal com 8 critérios ✅/❌ detalhados
- Score propagado via `valuations.json`, `decision_stocks.json` e portfolio API

### O que foi implementado na Fase 2

- `buffett_fetcher.py` (novo serviço) — busca `Capital Expenditure`, `D&A`, `Operating Cash Flow` e `Net Income` via `yfinance.cashflow` + `income_stmt`
- Cálculo de **FCF** (FCO − |CapEx|), **Owner Earnings** (NI + D&A − |CapEx|), **FCF/Lucro** e **CapEx/Lucro**
- Dados persistidos em `stock_history.json` como `buffett_cashflow` por ticker
- Trigger integrado em `history_fetcher.fetch_history()` — mesma pipeline, sem processo separado
- 4 flags informacionais adicionados ao `buffett_moat.flags` em `valuation_calculator.py`: `moat_fcf_positivo`, `moat_fcf_quality`, `moat_capex_moat`, `moat_owner_earnings_ok` — **não alteram o score 0-10**
- `cashflow_values` passado no retorno do `_calc_buffett_moat_score()` para uso no frontend
- Constantes `BUFFETT_FCF_QUALITY_MIN = 0.80` e `BUFFETT_CAPEX_MOAT_MAX = 0.25` em `rules.py`
- Seção **"QUALIDADE DO CAIXA"** no modal do frontend com 3 cards monetários (FCF | Owner Earnings | Lucro Líquido), barra FCF/Lucro e checklist dos 4 critérios
- Graceful failure: `cashflow_available: false` quando dados indisponíveis (comum em small caps BR)

### O que foi implementado na Fase 3

- `fetch_trends()` em `buffett_fetcher.py` — busca tendências históricas de até 4 anos via `yfinance.income_stmt`, `cashflow` e `balance_sheet`
- 6 métricas calculadas ano a ano: **Margem Bruta**, **Margem Líquida**, **ROE**, **FCF**, **Dívida Líquida**, **CapEx/Receita**
- `_safe_series()` — helper que extrai lista de até 4 valores históricos de uma linha do DataFrame (antes só `.iloc[0]` era usado)
- `_calc_tendencia()` — classifica a direção como `CRESCENDO` / `ESTAVEL` / `CAINDO` (≥ 75% dos intervalos em alta → CRESCENDO)
- Dados persistidos em `stock_history.json` como `buffett_trends` por ticker, atualizados junto com o pipeline existente
- `trends_values` propagado via `valuation_calculator._calc_buffett_moat_score()` → `valuations.json` e `decision_stocks.json`
- Flags informacionais adicionadas (`moat_mb_trend`, `moat_roe_trend`, `moat_fcf_trend`, `moat_divida_trend`, `moat_capex_rec_trend`) — **não alteram o score 0-10**
- Seção **"TENDÊNCIAS HISTÓRICAS (4 ANOS)"** no modal do frontend com tabela de valores ano a ano e badges coloridos (`↗ Subindo` / `↘ Descendo` / `→ Estável`)
- Lógica de cor invertida para Dívida Líquida e CapEx/Receita (CAINDO = positivo = verde)
- Graceful failure: `{"trends_available": false}` quando dados insuficientes (comum em small caps BR)

### O que foi implementado na Fase 4

- **SG&A / Receita** adicionado ao `fetch_trends()` em `buffett_fetcher.py` — série histórica de 4 anos com `sga_receita_hist` e `sga_receita_trend` (CAINDO = positivo, mesmo padrão de CapEx/Receita)
- **`moat_indicators`** — novo dict no retorno de `_calc_buffett_moat_score()` com os valores reais de cada critério (margem_bruta, margem_liq, roe, roic, dl_pl, cagr_lucro, cagr_receita) para exibição no frontend
- **Gauge visual do Moat Score** — barra horizontal 0-10 com 3 zonas de cor (vermelho 0-3 / amarelo 4-6 / verde 7-10) e marcadores nos thresholds 4 e 7; substituiu o pill simples
- **Valores reais por critério** — cada linha do checklist Buffett agora exibe o valor numérico do indicador à direita (ex: `ROE ≥ 20% (peso 2 — Buffett)   28.5%`)
- **Linha SG&A/Receita na tabela de tendências** — adicionada após CapEx/Receita, com lógica de cor invertida (↘ Descendo = verde)
- **Rodapé atualizado** — "Dívida, CapEx/Receita e SG&A/Receita: ↓ CAINDO = positivo"
- **Flag `moat_sga_trend`** propagada via `flags` em `valuation_calculator.py` (informacional, não altera score 0-10)
- **Graceful failure** — SG&A pode ser `null` para muitas ações BR sem quebrar a exibição

---

## 1. A Metodologia do Livro

Mary Buffett e David Clark ensinam a identificar empresas com **Vantagem Competitiva Durável** (*economic moat*) analisando 3 demonstrativos financeiros de forma sistemática.

### Os 3 Tipos de Vantagem Competitiva Durável

- Empresas que vendem **produtos únicos** (ex: Coca-Cola)
- Empresas que vendem **serviços únicos** (ex: American Express)
- **Provedores de baixo custo** de produtos/serviços que o público precisa consistentemente (ex: Walmart)

### As 3 Características de uma Empresa com Moat

1. **Poder de precificação** — pode aumentar preços sem perder clientes
2. **Lucros previsíveis** — fluxo de caixa estável ao longo de ciclos econômicos
3. **Valor de marca** — lealdade do cliente cria barreiras psicológicas à concorrência

---

## 2. Os 3 Pilares da Análise

### 2.1 Demonstração de Resultado (DRE)

| Métrica | Threshold de Buffett | Significado |
|---------|---------------------|-------------|
| Margem Bruta | ≥ 40% | Vantagem forte; < 20% = guerra de preços |
| SG&A / Receita | ≤ 30% | Empresa não precisa gastar demais para manter o moat |
| Margem Líquida | ≥ 20% | Empresa se beneficia de vantagem competitiva durável |
| Crescimento do LPA | ≥ 10% a.a. por ≥ 10 anos | Consistência e crescimento real |

### 2.2 Balanço Patrimonial

| Métrica | Threshold de Buffett | Significado |
|---------|---------------------|-------------|
| Dívida Líq. / PL | ≤ 0.5 (prefere próximo de 0) | Empresas com moat real não precisam de dívida |
| Liquidez Corrente | ≥ 1.5 | Saúde financeira de curto prazo |
| ROE médio 10 anos | ≥ 20% (mínimo anual ≥ 15%) | Eficiência na conversão de capital em lucro |
| Caixa forte | Autofinanciamento | Sem necessidade de dívida para crescer |

### 2.3 Fluxo de Caixa

| Métrica | Threshold de Buffett | Significado |
|---------|---------------------|-------------|
| Free Cash Flow (FCF) | Positivo e crescente por ≥ 10 anos | Geração real de caixa |
| CapEx / Lucro Líquido | Baixo | Moat forte = baixo reinvestimento necessário |
| Owner Earnings | Net Income + D&A − CapEx manutenção | Verdadeiro lucro disponível ao acionista |

### 2.4 Fórmula Owner Earnings

```
Owner Earnings = Lucro Líquido
               + Depreciação & Amortização (D&A)
               − CapEx de Manutenção
```

> Owner Earnings representa o caixa verdadeiro disponível aos donos — mais relevante para valuation do que o lucro líquido contábil.

---

## 3. Thresholds Completos de Buffett

| Categoria | Métrica | Benchmark | Período |
|-----------|---------|-----------|---------|
| **Rentabilidade** | Margem Bruta | ≥ 40% | Consistente ao longo do tempo |
| | Margem Líquida | ≥ 20% | Média histórica |
| | ROE | ≥ 20% médio, ≥ 15% mínimo anual | Mínimo 10 anos |
| | ROIC | ≥ 15% | Consistente |
| **Operacional** | SG&A / Receita | ≤ 30% | — |
| | P&D / Receita | ≤ 30% | — |
| | D&A / Lucro Bruto | ≤ 10% | — |
| **Dívida** | DL / PL | ≤ 0.5 | — |
| | Liquidez Corrente | ≥ 1.5 | — |
| **Crescimento** | Crescimento LPA | ≥ 10% a.a. | Com margens altas |
| **Caixa** | Free Cash Flow | Positivo e crescente | Mínimo 10 anos |
| | Owner Earnings | Positivo e sustentável | Para valuation |

---

## 4. Diagnóstico da Aplicação Atual

### 4.1 Fontes de Dados Atuais

| Fonte | Dados Fornecidos |
|-------|-----------------|
| **all_indicators.json** | 31 indicadores fundamentalistas (snapshot atual) |
| **yfinance** | Preço mín/máx 6m, dividendos 5 anos, lucro líquido 5 anos, score de acumulação |
| **StatusInvest API** | Payout ratio |

### 4.2 O que já temos — Base Sólida

| Critério | Dado | Threshold Atual |
|----------|------|----------------|
| ✅ Margem Bruta | `margembruta` | disponível (sem scoring Buffett) |
| ✅ Margem EBIT | `margemebit` | ≥ 10% |
| ✅ Margem Líquida | `margemliquida` | ≥ 10% |
| ✅ ROE | `roe` | ≥ 10% |
| ✅ ROIC | `roic` | ≥ 10% |
| ✅ DL/PL | `dividaliquidapatrimonioliquido` | ≤ 1.0 |
| ✅ DL/EBITDA | `dividaliquidaebit` | ≤ 3.0 |
| ✅ Liquidez Corrente | `liquidezcorrente` | ≥ 2.0 (Graham) |
| ✅ CAGR 5a Receita | `receitas_cagr5` | ≥ 5% |
| ✅ CAGR 5a Lucro | `lucros_cagr5` | ≥ 5% |
| ✅ Dividendos consistentes | 5 anos histórico | pago todos os anos |
| ✅ Piotroski F-Score | 9 sinais | adaptado |

### 4.3 Gaps Críticos — O que falta

| Dado | Impacto para Buffett | Está em alguma fonte atual? |
|------|---------------------|-----------------------------|
| CapEx | CRÍTICO — base do Owner Earnings | ❌ Não |
| Depreciação & Amortização (D&A) | CRÍTICO — base do Owner Earnings | ❌ Não |
| Fluxo de Caixa Operacional (FCO) | CRÍTICO — Free Cash Flow | ❌ Não |
| Free Cash Flow (FCF) | CRÍTICO — geração real de caixa | ❌ Não |
| Owner Earnings | CRÍTICO — valuation Buffett | ❌ Não |
| SG&A como % Receita | ALTO | ❌ Não |
| Margem Bruta histórica (tendência) | ALTO — pricing power | ❌ Não |
| ROE histórico ano a ano | ALTO — consistência 10 anos | ❌ Não |
| FCF / Lucro Líquido (qualidade) | ALTO — distingue lucro real de contábil | ❌ Não |
| Receita bruta histórica (ano a ano) | MÉDIO | ❌ Não |
| Tendência de dívida (4 anos) | MÉDIO | ❌ Não |
| Threshold Margem Bruta ≥ 40% | MÉDIO — existe o dado, falta o scoring | ⚠️ Parcial |
| Threshold ROE ≥ 20% (Buffett) | MÉDIO — existe o dado (10% atual) | ⚠️ Parcial |
| Threshold Margem Líquida ≥ 20% | MÉDIO — existe o dado (10% atual) | ⚠️ Parcial |

---

## 5. O que o Yahoo Finance (yfinance) pode fornecer

### 5.1 Dados disponíveis via yfinance para ações brasileiras (formato `.SA`)

```python
import yfinance as yf
ticker = yf.Ticker("WEGE3.SA")

ticker.income_stmt          # DRE anual (4 anos)
ticker.balance_sheet        # Balanço anual (4 anos)
ticker.cashflow             # Fluxo de Caixa anual (4 anos)
ticker.quarterly_income_stmt    # DRE trimestral
ticker.quarterly_cashflow       # Fluxo de Caixa trimestral
```

| Dado | Demonstrativo yfinance | Resolve gap? |
|------|----------------------|--------------|
| **CapEx** | `cashflow.loc["Capital Expenditure"]` | ✅ SIM |
| **D&A** | `cashflow.loc["Depreciation And Amortization"]` | ✅ SIM |
| **FCO** | `cashflow.loc["Operating Cash Flow"]` | ✅ SIM |
| **Free Cash Flow** | FCO − CapEx | ✅ SIM |
| **Owner Earnings** | Net Income + D&A − CapEx | ✅ SIM |
| **FCF / Lucro Líquido** | FCF ÷ Net Income | ✅ SIM |
| **SG&A como % Receita** | `income_stmt.loc["Selling General And Administration"]` | ✅ SIM |
| **Margem Bruta histórica (4 anos)** | Gross Profit ÷ Revenue | ✅ SIM |
| **Tendência ROE (4 anos)** | Net Income ÷ Equity | ✅ PARCIAL |
| **CapEx / Lucro** (proxy moat) | CapEx ÷ Net Income | ✅ SIM |
| **Evolução da dívida** | Balance Sheet (4 anos) | ✅ SIM |
| ROE histórico 10 anos | — | ❌ NÃO (limite 4 anos) |
| Indicadores qualitativos de moat | — | ❌ NÃO |
| Participação de mercado | — | ❌ NÃO |

### 5.2 Limitações do yfinance

- Histórico financeiro limitado a **4 anos** (Buffett recomenda 10 anos)
- Rate limit: ~360 requisições/hora
- Confiabilidade ~98% (fonte não-oficial, pode quebrar com mudanças no Yahoo)
- Alguns campos podem estar ausentes para determinadas ações brasileiras

---

## 6. Plano de Implementação

### Fase 1 — Impacto imediato (dados já disponíveis)

> Usar `all_indicators.json` que já temos. Sem nova integração.

**Ações:**

1. Adicionar `margembruta ≥ 40%` como critério de ranking (hoje não pontua)
2. Elevar threshold de `margemliquida` de 10% para 20% (Buffett)
3. Elevar threshold de `roe` de 10% para 20% (Buffett) — criar flag separada `roe_buffett`
4. Elevar threshold de `roic` de 10% para 15% (Buffett) — criar flag separada `roic_buffett`
5. Elevar threshold de `dividaliquidapatrimonioliquido` de 1.0 para 0.5 — criar flag separada `dl_pl_buffett`
6. Criar **Buffett Moat Score** (0-10) baseado nos dados existentes

**Arquivo a modificar:** [valuation_calculator.py](../backend/services/valuation_calculator.py)

```python
# BUFFETT MOAT SCORE (0-10) — usando dados já disponíveis

def calcular_buffett_moat_score(indicators: dict, history: dict) -> dict:
    score = 0
    flags = {}

    # Critério 1: Margem Bruta ≥ 40% (peso 2 — critério principal)
    mb = indicators.get("margembruta", 0)
    flags["moat_margem_bruta"] = mb >= 40
    if mb >= 40: score += 2

    # Critério 2: Margem Líquida ≥ 20%
    flags["moat_margem_liquida"] = indicators.get("margemliquida", 0) >= 20
    if flags["moat_margem_liquida"]: score += 1

    # Critério 3: ROE ≥ 20% (peso 2 — critério principal)
    flags["moat_roe"] = indicators.get("roe", 0) >= 20
    if flags["moat_roe"]: score += 2

    # Critério 4: ROIC ≥ 15%
    flags["moat_roic"] = indicators.get("roic", 0) >= 15
    if flags["moat_roic"]: score += 1

    # Critério 5: Dívida baixíssima (DL/PL ≤ 0.5)
    flags["moat_baixa_divida"] = indicators.get("dividaliquidapatrimonioliquido", 999) <= 0.5
    if flags["moat_baixa_divida"]: score += 1

    # Critério 6: Crescimento de lucro ≥ 10% a.a.
    flags["moat_lucro_crescendo"] = indicators.get("lucros_cagr5", 0) >= 10
    if flags["moat_lucro_crescendo"]: score += 1

    # Critério 7: Crescimento de receita ≥ 5% a.a.
    flags["moat_receita_crescendo"] = indicators.get("receitas_cagr5", 0) >= 5
    if flags["moat_receita_crescendo"]: score += 1

    # Critério 8: Dividendos crescentes
    flags["moat_div_crescente"] = history.get("dividend_growing", False)
    if flags["moat_div_crescente"]: score += 1

    label = "FORTE" if score >= 7 else "MODERADO" if score >= 4 else "FRACO"

    return {"score": score, "score_max": 10, "label": label, "flags": flags}
```

---

### Fase 2 — Integração yfinance para dados de Caixa

> Criar novo serviço que busca DRE, Balanço e Fluxo de Caixa histórico.

**Novo arquivo:** `yfinance_fundamentals_fetcher.py`

**Dados a buscar e calcular:**

```python
import yfinance as yf

def fetch_fundamentals(ticker: str) -> dict:
    t = yf.Ticker(f"{ticker}.SA")

    cf = t.cashflow          # Fluxo de Caixa anual
    inc = t.income_stmt      # DRE anual
    bs = t.balance_sheet     # Balanço anual

    # Métricas Buffett calculadas
    capex       = cf.loc["Capital Expenditure"].iloc[0]       # CapEx mais recente
    da          = cf.loc["Depreciation And Amortization"].iloc[0]  # D&A
    fco         = cf.loc["Operating Cash Flow"].iloc[0]       # FCO
    net_income  = inc.loc["Net Income"].iloc[0]               # Lucro Líquido
    revenue     = inc.loc["Total Revenue"].iloc[0]            # Receita

    fcf           = fco - abs(capex)                          # Free Cash Flow
    owner_earn    = net_income + da - abs(capex)              # Owner Earnings
    fcf_quality   = fcf / net_income if net_income > 0 else 0 # FCF/NI ratio
    capex_ratio   = abs(capex) / net_income if net_income > 0 else 0  # CapEx/NI

    return {
        "capex": capex,
        "da": da,
        "fco": fco,
        "fcf": fcf,
        "owner_earnings": owner_earn,
        "fcf_quality": fcf_quality,       # > 0.8 = excelente
        "capex_lucro_ratio": capex_ratio, # < 0.25 = moat forte
        "capex_moat_ok": capex_ratio < 0.25,
        "fcf_positivo": fcf > 0,
        "owner_earnings_positivo": owner_earn > 0,
    }
```

**Critérios de scoring adicionais (Fase 2):**

| Critério | Threshold | Interpretação |
|----------|-----------|---------------|
| FCF positivo | FCF > 0 | Geração real de caixa |
| FCF / Lucro Líquido | ≥ 0.8 | Lucro de alta qualidade (pouco accrual) |
| CapEx / Lucro Líquido | ≤ 0.25 | Moat forte — baixo reinvestimento |
| Owner Earnings positivo | OE > 0 | Empresa realmente lucrativa para o dono |

---

### Fase 3 — Tendências históricas (4 anos yfinance)

> Analisar a **direção** dos indicadores, não só o valor pontual.

**Métricas de tendência:**

| Métrica | Sinal positivo | Sinal negativo |
|---------|---------------|----------------|
| Margem Bruta crescendo | ✅ pricing power aumentando | ❌ competição erodindo moat |
| ROE crescendo | ✅ eficiência melhorando | ❌ retorno deteriorando |
| Dívida Líquida caindo | ✅ empresa se desendividando | ❌ alavancagem crescente |
| FCF crescendo | ✅ geração de caixa acelerando | ❌ queima de caixa |
| CapEx / Receita caindo | ✅ menos reinvestimento necessário | ❌ moat enfraquecendo |

```python
def calcular_tendencia(valores: list) -> str:
    """
    Recebe lista de valores do mais recente ao mais antigo.
    Retorna: CRESCENDO, ESTAVEL, CAINDO
    """
    if len(valores) < 2:
        return "INDEFINIDO"
    crescimentos = [valores[i] > valores[i+1] for i in range(len(valores)-1)]
    positivos = sum(crescimentos)
    if positivos >= len(crescimentos) * 0.75:
        return "CRESCENDO"
    elif positivos <= len(crescimentos) * 0.25:
        return "CAINDO"
    return "ESTAVEL"
```

---

### Fase 4 — Frontend: Buffett Score Visual

Adicionar ao card de cada ação um painel **Buffett Moat Score**:

```
┌─────────────────────────────────────────┐
│  WEGE3  ★ MOAT FORTE (8/10)            │
├─────────────────────────────────────────┤
│ Margem Bruta:     ✅ 47%   (≥ 40%)     │
│ Margem Líquida:   ✅ 22%   (≥ 20%)     │
│ ROE:              ✅ 28%   (≥ 20%)     │
│ ROIC:             ✅ 19%   (≥ 15%)     │
│ Dívida (DL/PL):   ✅ 0.1   (≤ 0.5)    │
│ CAGR Lucro 5a:    ✅ 18%   (≥ 10%)     │
│ CAGR Receita 5a:  ✅ 12%   (≥ 5%)      │
│ Div. Crescentes:  ✅ Sim               │
├─────────────────────────────────────────┤
│ FCF (Fase 2):     ✅ R$ 2.1bi          │
│ Owner Earnings:   ✅ R$ 1.9bi          │
│ CapEx/Lucro:      ✅ 18%   (≤ 25%)     │
└─────────────────────────────────────────┘
```

---

## 7. Prioridade de Implementação

| Fase | Ação | Esforço | Impacto | Depende de |
|------|------|---------|---------|------------|
| **1a** | Ajustar thresholds Buffett (MB, ML, ROE, ROIC, DL/PL) | Baixo | Alto | Nada — dados já existem |
| **1b** | Criar Buffett Moat Score (0-10) | Baixo | Alto | Fase 1a |
| **2a** | Criar `yfinance_fundamentals_fetcher.py` | Médio | Alto | yfinance já instalado |
| **2b** | Calcular FCF, Owner Earnings, CapEx ratio | Médio | Alto | Fase 2a |
| **2c** | Integrar ao pipeline de `stock_history.json` | Médio | Médio | Fase 2b |
| **3a** | Calcular tendências 4 anos (margem bruta, ROE, FCF) | Médio | Médio | Fase 2a |
| **4a** | Exibir Moat Score no frontend | Médio | Médio | Fase 1b |
| **4b** | Exibir FCF e Owner Earnings no frontend | Médio | Médio | Fase 2b |

---

## 8. O que nunca conseguiremos automatizar

Alguns aspectos do método Buffett são qualitativos e requerem análise manual:

- **Poder de precificação real** — a empresa pode aumentar preços sem perder clientes?
- **Custo de troca do cliente** — o cliente fica preso ao produto/serviço?
- **Qualidade do management** — gestão alinhada com acionistas?
- **Simplicidade do negócio** — Buffett quer entender o que a empresa faz
- **Proteção regulatória** — concessões, patentes, barreiras de entrada
- **Participação de mercado** — tendência de dominância do setor

> Esses fatores podem ser documentados manualmente por ação no campo `notes` do sistema de monitoramento.

---

## 9. Resumo Executivo

### O que ganhamos com a implementação completa

| Antes | Depois |
|-------|--------|
| Metodologia Bazin/Barsi (renda, dividendos) | Metodologia Buffett (qualidade + renda) |
| Threshold ROE ≥ 10% | Threshold ROE ≥ 20% (mais exigente) |
| Threshold Margem Líquida ≥ 10% | Threshold Margem Líquida ≥ 20% |
| Margem Bruta não avaliada | Margem Bruta ≥ 40% como critério primário |
| Lucro Líquido como proxy de caixa | Owner Earnings = caixa verdadeiro do dono |
| Sem análise de CapEx | CapEx/Lucro como sinal de qualidade do moat |
| Sem Free Cash Flow | FCF positivo e crescente como requisito |
| Score baseado em 21 critérios | Score com 27 critérios + Buffett Moat Score (0-10) |

### Dados que o yfinance resolve

```
✅ CapEx              → Owner Earnings
✅ D&A                → Owner Earnings
✅ FCO                → Free Cash Flow
✅ FCF = FCO − CapEx  → Qualidade de caixa
✅ SG&A histórico     → Eficiência operacional
✅ Margem Bruta 4 anos → Tendência de pricing power
✅ ROE histórico 4 anos → Consistência de retorno
```

### Dados que ainda precisaremos de análise manual ou outras fontes

```
❌ Histórico > 4 anos (ROE 10 anos ideal)
❌ Qualidade do management
❌ Poder de precificação real
❌ Participação de mercado
❌ Switching costs do cliente
```
