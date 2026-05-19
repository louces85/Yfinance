# Como Grandes Investidores Encontram Bons Ativos
## e Como Esta Aplicação Pode Identificá-los

---

## 1. Os Investidores e Suas Filosofias

### Luiz Barsi Filho — "A Galinha dos Ovos de Ouro"

**Filosofia central:** Comprar empresas como quem compra um negócio. O objetivo é acumular renda, não especular com preço. "Compre a galinha, não o ovo."

**Critérios objetivos:**

| Critério | Threshold | Status no projeto |
|----------|-----------|-------------------|
| Dividend Yield | >= 6% ao ano | ✅ `D_Y = 6` em rules.py |
| Preço abaixo do alvo (avg_div / 0.06) | pNow < pTarget | ✅ calculado em valuation.py |
| P/VP | < 1 (bonus) | ✅ `flagVPA` em valuation.py |
| Consistência de dividendos | >= 5 anos consecutivos | ❌ **não implementado** |
| Acumular na queda | preço E volume abaixo da média | ✅ "Build Position" em analysis.py |
| Setores preferidos | Bancos, utilities, telecom, saneamento | ❌ sem filtro de setor |

**O que Barsi faz que ainda não fazemos:**
- Verifica se a empresa pagou dividendos em **cada** um dos últimos 5 anos (não média)
- Calcula o yield **real atual**: `sum(dividendos 12 meses) / preço_agora`
- Usa três zonas de preço alvo: 5% (monitorar), 6% (comprar), 8% (compra agressiva)
- Considera o crescimento do dividendo ano a ano (CAGR de dividendos)

---

### Décio Bazin — "Faça Fortuna com Ações" (1992)

**Filosofia central:** Ações são pedaços de um negócio. O preço justo é determinado pela renda que o negócio gera.

**Fórmula do preço justo:**
```
Preço Justo = Média de Dividendos (últimos 4-5 anos) / 0.06
```

**6 Critérios:**

| # | Critério | Threshold Bazin | Status no projeto |
|---|----------|-----------------|-------------------|
| 1 | Dividend Yield | >= 6% | ✅ `D_Y = 6` |
| 2 | Consistência dividendos | >= 5 anos sem interrupção | ❌ **não implementado** |
| 3 | Payout Ratio | 40% a 80% | ⚠️ exibido mas sem filtro de faixa |
| 4 | Dívida Líq./PL | <= 1.0 | ✅ `DL_PL = 1` |
| 5 | Liquidez diária | > R$1M/dia | ✅ `D.AVG.LQ >= 0.2M` (pode elevar) |
| 6 | Setores defensivos | Utilities, bancos, telecom | ❌ sem filtro de setor |

**Detalhe crítico — Payout fora da faixa:**
- Payout < 40%: empresa retém demais (sinal de má alocação ou problema escondido)
- Payout > 80%: dividendo insustentável (paga mais do que ganha)

---

### Benjamin Graham — "O Investidor Inteligente"

**Filosofia:** Comprar com margem de segurança. O mercado é um parceiro maníaco-depressivo (Mr. Market) — compre quando ele está deprimido.

**7 Critérios do Investidor Defensivo:**

| # | Critério | Threshold Graham | Status no projeto |
|---|----------|-----------------|-------------------|
| 1 | Tamanho mínimo | Receita > R$2B | ❌ não filtrado |
| 2 | Liquidez corrente | >= 2.0 | ⚠️ `L_Q >= 1` (menos exigente) |
| 3 | Estabilidade de lucros | 10 anos sem prejuízo | ⚠️ apenas booleano net_income |
| 4 | Histórico de dividendos | 20 anos ininterruptos | ❌ não implementado |
| 5 | Crescimento de EPS | +33% em 10 anos (~3% CAGR) | ⚠️ `CAGR_L = 5%` em 5 anos |
| 6 | P/L moderado | <= 15x (média 3 anos) | ✅ `P_L = 15` |
| 7 | P/VP moderado | <= 1.5 | ✅ `P_VP = 1.5` |

**Regra combinada de Graham:**
```
P/L × P/VP <= 22.5
```
*Exemplo: P/L = 12 e P/VP = 1.8 → 12 × 1.8 = 21.6 ✅ (dentro do limite)*
**Esta regra combinada não está implementada.**

**NCAV (Net Current Asset Value) — as "pontas de charuto":**
```
NCAV = Ativo Circulante - Total de Passivos
Compra se: Preço < 2/3 × NCAV
```
Disponível via yfinance: `balance_sheet['Current Assets'] - balance_sheet['Total Liabilities Net Minority Interest']`

---

### Joel Greenblatt — "Magic Formula"

**Filosofia:** Comprar boas empresas a preços baratos. Simples assim.

**Duas métricas, ambas computáveis via yfinance:**

```python
# Earnings Yield (EY) — quão "barata" é a empresa
EY = EBIT / Enterprise Value
# Enterprise Value = Market Cap + Total Debt - Cash

# Return on Invested Capital (ROIC) — quão "boa" é a empresa
ROIC = EBIT / (Net PPE + Net Working Capital)
```

**Processo:**
1. Rankear todas as ações por EY (do maior para o menor)
2. Rankear todas as ações por ROIC (do maior para o menor)
3. Somar os dois ranks
4. Comprar as 20-30 com menor soma (melhor EY + melhor ROIC)

| Campo | yfinance | Status no projeto |
|-------|---------|-------------------|
| EBIT | `financials.loc['EBIT']` | ⚠️ vem do JSON (StatusInvest) |
| Enterprise Value | `info['enterpriseValue']` | ❌ não usado |
| Net PPE | `balance_sheet.loc['Net PPE']` | ❌ não usado |
| Working Capital | `balance_sheet.loc['Working Capital']` | ❌ não usado |
| ROIC | `info['returnOnEquity']` aprox. | ✅ `ROIC` do JSON |
| EV/EBIT | `info['enterpriseToEbitda']` aprox. | ✅ `ev_ebit` no JSON |

**O JSON all_indicators.json já contém `roic` e `ev_ebit` — o ranking da Magic Formula pode ser implementado diretamente sobre os dados existentes.**

---

### Peter Lynch — PEG Ratio

**Filosofia:** Invista no que você conhece. O P/L sozinho não diz nada — é preciso relacionar com o crescimento.

**Fórmula principal:**
```python
PEG = P/L / Taxa de crescimento anual do lucro (%)
# PEG < 1.0  → potencialmente subvalorizado
# PEG < 0.5  → forte sinal de compra
# PEG > 1.5  → potencialmente caro

# Versão ajustada por dividendos (para empresas maduras):
PEG_adj = P/L / (crescimento_lucro + dividend_yield)
```

| Campo | yfinance | JSON | Status |
|-------|---------|------|--------|
| PEG | `info['trailingPegRatio']` | `peg_ratio` | ✅ no JSON |
| P/L | `info['trailingPE']` | `p_l` | ✅ |
| CAGR Lucro | calcular de `financials` | `lucros_cagr5` | ✅ |

**O JSON já contém `peg_ratio` e `lucros_cagr5` — podemos usar o PEG ajustado por dividendos imediatamente.**

---

## 2. Dados Disponíveis na Aplicação

### Fonte 1 — all_indicators.json (StatusInvest)
36 campos por ação. Os mais relevantes por categoria:

**Valuation:**
`p_l`, `p_vp`, `p_ebit`, `p_ativo`, `p_sr`, `p_capitalgiro`, `p_ativocirculante`, `ev_ebit`, `peg_ratio`

**Rentabilidade:**
`margembruta`, `margemebit`, `margemliquida`, `roe`, `roa`, `roic`

**Dívida/Liquidez:**
`dividaliquidapatrimonioliquido`, `dividaliquidaebit`, `liquidezcorrente`, `passivo_ativo`

**Crescimento:**
`receitas_cagr5`, `lucros_cagr5`

**Identificação/Setor:**
`segmentname`, `sectorname`, `subsectorname`

**Mercado:**
`liquidezmediadiaria`, `valormercado`, `vpa`, `lpa`

---

### Fonte 2 — Yahoo Finance (yfinance)

**Histórico de preço/volume — `ticker.history(period="2y")`**

| Campo | Uso atual | Uso potencial |
|-------|-----------|---------------|
| `Close` | min/max 6 meses | percentil histórico 2 anos |
| `Volume` | min/max 6 meses | acumulação silenciosa |
| `Dividends` | avg 4 anos → price target | CAGR dividendos, consistência |
| `High`/`Low` | não usado | suporte/resistência |

**Dados fundamentalistas — `ticker.info`**

| Campo yfinance | Uso Potencial |
|---------------|---------------|
| `payoutRatio` | Filtro Bazin (40-80%) |
| `currentRatio` | Confirmação liquidez |
| `debtToEquity` | Confirmação dívida |
| `freeCashflow` | FCF yield (Graham) |
| `returnOnEquity` | ROE independente |
| `trailingPegRatio` | PEG (Lynch) |
| `fiftyTwoWeekLow` / `High` | Contexto 52 semanas |
| `twoHundredDayAverage` | Tendência longa |
| `bookValue` | P/VP em tempo real |
| `fiveYearAvgDividendYield` | DY médio 5 anos |
| `earningsGrowth` | Crescimento recente |
| `targetMeanPrice` | Consenso de analistas |

**Demonstrativos completos:**

```python
ticker.financials       # DRE — EBIT, Net Income, Revenue (4 anos)
ticker.balance_sheet    # Balanço — Net Debt, Working Capital, Net PPE (4 anos)
ticker.cashflow         # Fluxo de Caixa — Free Cash Flow, CapEx (4 anos)
ticker.dividends        # Histórico completo de dividendos
```

---

### Fonte 3 — Google Finance (scraping)
- `price_now` — preço atual para o cálculo do yield real
- Frágil: depende de classe CSS `YMlKec fxKbKc`

---

## 3. O Que Podemos Implementar (e Com Que Dados)

### Alta prioridade — dados já disponíveis

#### A. Yield Atual Real (Barsi/Bazin)
```python
# Em vez do DY% estático do StatusInvest:
dividendos = ticker.history(period="2y")["Dividends"]
soma_12m    = dividendos[dividendos.index >= hoje - 365].sum()
yield_real  = (soma_12m / preco_agora) * 100

# Se yield_real >> dy_estatusinvest: ação caiu muito → oportunidade
```
**Impacto:** Quando o preço cai, o yield real sobe. Uma ação que o StatusInvest mostra 6% pode estar pagando 10-12% ao preço atual — esse é o sinal mais forte de Barsi.

---

#### B. Três Zonas de Preço Alvo (Barsi)
```python
# Em vez de um único target a 6%:
target_conservador = avg_div / 0.08   # Compra agressiva — yield exigido 8%
target_base        = avg_div / 0.06   # Compra moderada (atual)
target_minimo      = avg_div / 0.05   # Apenas monitorar — yield exigido 5%
```
**Impacto:** Não é binário (caro/barato). Mostra em qual zona o preço está agora.

---

#### C. Score de Acumulação — % do tempo abaixo das médias
```python
# condition_percentage já existe em analysis.py linha 107
# mas não está sendo usado no ranking
# Quanto maior o %, mais tempo o ativo está em acumulação silenciosa
```
**Impacto:** Uma ação que passa 70% do tempo com preço E volume abaixo da média está sendo acumulada devagar — exatamente o padrão Barsi.

---

#### D. Magic Formula Rank (Greenblatt)
```python
# Ambos os campos estão no JSON (all_indicators.json):
# ev_ebit → equivale a 1/EY (menor = mais barato)
# roic    → direto

# Rank por ev_ebit (crescente) + rank por roic (decrescente) = Magic Score
magic_score = rank_ev_ebit + rank_roic
# Menor magic_score = melhor ação pelo critério Greenblatt
```
**Impacto:** Zero dados novos necessários. Só precisa rankear o que já existe.

---

#### E. PEG Ajustado por Dividendos (Lynch)
```python
# Ambos no JSON:
peg_ajustado = p_l / (lucros_cagr5 + dy_percent)
# PEG_adj < 1.0 → crescimento não está sendo precificado
```

---

#### F. Regra Combinada de Graham
```python
# Ambos no JSON:
graham_score = p_l * p_vp
# graham_score <= 22.5 → aprovado por Graham
# Adicionar 1 ponto ao ranking
```

---

### Média prioridade — requer leitura do `ticker.dividends`

#### G. Consistência de Dividendos (Barsi/Bazin)
```python
divs = ticker.dividends.resample("Y").sum()
anos_com_dividendo = (divs > 0).sum()
# +1 no ranking se pagou em todos os 5 últimos anos
# +1 no ranking se CAGR do dividendo > 0 (dividendo crescente)
```

#### H. Payout dentro da faixa Bazin (40-80%)
```python
# Payout já vem do valuation.py — só criar o filtro:
payout_saudavel = 0.40 <= payout <= 0.80
```

---

### Média prioridade — requer `ticker.financials` e `ticker.balance_sheet`

#### I. NCAV Graham (pontas de charuto)
```python
ncav = current_assets - total_liabilities
ncav_per_share = ncav / shares_outstanding
margem_graham  = preco_atual / (ncav_per_share * 0.67)
# Se margem_graham < 1: compra com margem de segurança Graham pura
```

#### J. Earnings Yield Real (Greenblatt)
```python
ebit = financials.loc["EBIT"].iloc[0]
ev   = info["enterpriseValue"]
earnings_yield = (ebit / ev) * 100
# Mais preciso que o ev_ebit do JSON (que pode estar desatualizado)
```

---

### Baixa prioridade — qualitativo

#### K. Filtro por Setor (Barsi/Bazin)
Setores defensivos presentes no JSON (`sectorname`, `segmentname`):
- Financeiro (bancos, seguros)
- Utilidade Pública (energia, saneamento)
- Telecomunicações
- Consumo não Cíclico (alimentos, farmacêuticos)

---

## 4. Ranking Proposto — Versão Melhorada

| # | Critério | Origem | Threshold | Pontos |
|---|----------|--------|-----------|--------|
| 1 | DY Real atual | yfinance dividends + price_now | >= 6% | 1 |
| 2 | Preço abaixo do target (6%) | avg_div / 0.06 | pNow < target | 1 |
| 3 | Zona agressiva (8%) | avg_div / 0.08 | pNow < target_8 | 1 |
| 4 | P/VP | all_indicators.json | <= 1.5 | 1 |
| 5 | Preço abaixo do VPA | all_indicators.json | pNow <= VPA | 1 |
| 6 | P/L | all_indicators.json | <= 15 | 1 |
| 7 | Graham combinado | p_l × p_vp | <= 22.5 | 1 |
| 8 | Dívida Líq./PL | all_indicators.json | <= 1 | 1 |
| 9 | Dívida Líq./EBITDA | all_indicators.json | <= 3 | 1 |
| 10 | Liquidez Corrente | all_indicators.json | >= 1 | 1 |
| 11 | Margem EBIT | all_indicators.json | >= 10% | 1 |
| 12 | Margem Líquida | all_indicators.json | >= 10% | 1 |
| 13 | ROE | all_indicators.json | >= 10% | 1 |
| 14 | ROIC | all_indicators.json | >= 10% | 1 |
| 15 | CAGR Receita 5a | all_indicators.json | >= 5% | 1 |
| 16 | CAGR Lucro 5a | all_indicators.json | >= 5% | 1 |
| 17 | Payout saudável (Bazin) | valuation.py payout | 40-80% | 1 |
| 18 | Consistência dividendos | yfinance dividends | 5 anos consecutivos | 1 |
| 19 | PEG ajustado (Lynch) | p_l / (cagr_l + dy) | < 1.0 | 1 |
| 20 | Magic Formula (Greenblatt) | rank(ev_ebit) + rank(roic) | top 30% | 1 |

**Score máximo: 20 pontos** (vs 14 atual)

---

## 5. Campos yfinance Não Usados com Alto Potencial

| Campo | Insight |
|-------|---------|
| `fiftyTwoWeekLow` | Mostra se o preço está perto do fundo de 52 semanas (complementa now/min 6 meses) |
| `twoHundredDayAverage` | Tendência de longo prazo — comprar abaixo da MM200 é sinal técnico importante |
| `fiveYearAvgDividendYield` | Contexto do yield histórico — se DY atual > DY médio 5 anos, está barato |
| `freeCashflow` | FCF Yield = FCF / Market Cap. Empresas com alto FCF yield sustentam dividendos |
| `targetMeanPrice` | Consenso de analistas — pode confirmar ou contradizer nosso price target |
| `heldPercentInsiders` | Insider comprando = alinhamento. Insider vendendo = alerta |

---

## 6. Alerta Telegram — Gatilho Ideal

Quando **todas** as condições abaixo forem verdadeiras simultaneamente:

```
✅ Ranking >= 12/20
✅ Yield real atual >= 8%
✅ pNow/pMin <= 1.10 (máximo 10% acima do fundo)
✅ Score de acumulação >= 50% (metade do tempo abaixo das médias)
✅ pNow < price_target_8pct (preço abaixo do target a 8%)
✅ volume_agora < volume_media (mercado desinteressado)
```

Mensagem sugerida:
```
🚨 BUILD POSITION — BBAS3
Yield real: 9.2% | Alvo (6%): R$34.50 | Alvo (8%): R$25.87
Preço: R$24.10 | pNow/pMin: 1.04 | Rank: 15/20
Tempo em acumulação: 67% dos últimos 90 dias
Potencial até target: +43.1%
```

---

## Fontes e Referências

- **Barsi:** Entrevistas e livro "Ações para o Longo Prazo" (Alexandre Barsi)
- **Bazin:** "Faça Fortuna com Ações" (Décio Bazin, 1992)
- **Graham:** "The Intelligent Investor" (1949, rev. 1973) e "Security Analysis" (1934)
- **Greenblatt:** "The Little Book That Beats the Market" (2005)
- **Lynch:** "One Up on Wall Street" (1989) e "Beating the Street" (1993)
- **yfinance docs:** https://github.com/ranaroussi/yfinance — `ticker.info`, `ticker.financials`, `ticker.balance_sheet`, `ticker.cashflow`, `ticker.dividends`
- **StatusInvest JSON:** `files/bkp_indicators/all_indicators.json` — 36 campos, ~615 tickers B3
