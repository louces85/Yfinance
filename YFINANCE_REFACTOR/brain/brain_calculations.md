# Brain YFinance — Cálculos, Métricas, Medalhas e Limiares

> Parte 3/4 do brain. Para filosofias → `brain_overview.md`. Para arquitetura/código → `brain_architecture.md`. Para UI/dados/limitações → `brain_frontend.md`.

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

**Por que 6%?** Bazin definiu 6% como a taxa mínima de atratividade para renda variável frente à renda fixa.

**Zonas e classificação:**

| Zona | Condição | Yield Implícito | Cor |
|------|---------|----------------|-----|
| `COMPRA_FORTE` | preço ≤ alvo 8% | ≥ 8% | Verde Vivo |
| `COMPRA` | alvo 8% < preço ≤ alvo 6% | 6–8% | Verde |
| `MONITORAR` | alvo 6% < preço ≤ alvo 5% | 5–6% | Amarelo |
| `CARO` | preço > alvo 5% | < 5% | Vermelho |

```python
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

```python
gain_pct = ((price_target_6pct - price_now) / price_now) * 100
```

- **Positivo (+%)**: ação está abaixo do alvo — há potencial até o preço justo
- **Negativo (-%)**: ação está acima do alvo — "cara" pelo critério Bazin

---

### 7.3 Distância do Mínimo (Dist. Mín. / p_now_p_min)

```python
p_now_p_min = price_now / price_min_6m
```

**Por que é importante:** Barsi compra na queda — quanto mais próximo do mínimo recente, melhor o ponto de entrada.

| Valor | Cor | Significado |
|-------|-----|------------|
| ≤ 1.05 | 🟢 Verde vivo | Máximo 5% acima do mínimo — entrada excelente |
| ≤ 1.20 | 🟢 Verde | 5–20% acima — boa entrada |
| ≤ 1.40 | 🟡 Amarelo | 20–40% acima — entrada moderada |
| ≤ 1.60 | 🟠 Laranja | 40–60% acima — entrada fraca |
| > 1.60 | 🔴 Vermelho | > 60% acima — aguardar correção |

**Escala da barra (frontend):**
```javascript
// ratioBarWidth() — usa raiz quadrada para realçar diferenças perto de 1.0
const norm = Math.max(0, v - 0.85) / 1.35;
return Math.min(Math.max(Math.sqrt(norm) * 100, 5), 100);
```

---

### 7.4 Score Ponderado (0–100)

O Score agrega 21 critérios binários com pesos diferenciados.

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
- ≥ 65%: Verde | 40–65%: Amarelo | < 40%: Vermelho

> **Nota:** `liquidez_corrente_ok` e `passivo_ativo_ok` são isentos para empresas do setor financeiro (bancos, seguradoras) — PL/Ativo ≤ 20% identifica como financeira.

---

### 7.5 Piotroski F-Score (0–9)

9 sinais binários de saúde financeira.

**Grupo 1 — Lucratividade (3 sinais):**

| Sinal | Condição | Fonte |
|-------|---------|-------|
| P1 | Lucro Líquido > 0 (ano mais recente) | `net_income_per_year` (yfinance) |
| P2 | Margem EBIT > 0 | `all_indicators.json` |
| P3 | Lucro mais recente > lucro do ano anterior | `net_income_per_year` (yfinance) |

**Grupo 2 — Alavancagem/Liquidez (3 sinais):**

| Sinal | Condição | Limiar |
|-------|---------|--------|
| P4 | DL/PL conservador | ≤ 0.5 |
| P5 | Liquidez Corrente sólida | ≥ 1.5 |
| P6 | Balanço conservador | Passivo/Ativo ≤ 40% |

**Grupo 3 — Eficiência/Qualidade (3 sinais):**

| Sinal | Condição |
|-------|---------|
| P7 | CAGR Lucro > CAGR Receita (margens se expandindo) |
| P8 | CAGR Receita > 0% |
| P9 | ROE ≥ 15% |

**Classificação:** ≥ 7 → FORTE (verde) | 4–6 → MODERADO (amarelo) | ≤ 3 → FRACO (vermelho)

---

### 7.6 Buffett Moat Score (0–10)

#### Fase 1 — Critérios Base (0–10 pontos)

| Critério | Limiar | Peso |
|---------|--------|------|
| Margem Bruta | ≥ 40% | **2** |
| ROE | ≥ 20% | **2** |
| Margem Líquida | ≥ 20% | 1 |
| ROIC | ≥ 15% | 1 |
| DL/PL | ≤ 0.5 | 1 |
| CAGR Lucro 5a | ≥ 10% | 1 |
| CAGR Receita 5a | ≥ 5% | 1 |
| Dividendo crescente | — | 1 |

#### Fase 2 — Validação de Caixa (informacional, não afeta score)

| Flag | Condição |
|------|---------|
| `fcf_positivo` | FCF > 0 |
| `owner_earnings_positivo` | OE > 0 |
| `fcf_quality_ok` | FCF/Lucro ≥ 80% |
| `capex_moat_ok` | CapEx/Lucro ≤ 25% |

#### Fase 3 — Modificadores de Tendência (±0.5 por critério)

| Situação | Ajuste |
|---------|--------|
| Margem Bruta aprovada + tendência CAINDO | −0.5 |
| Margem Bruta reprovada + tendência CRESCENDO | +0.5 |
| ROE aprovado + tendência CAINDO | −0.5 |
| ROE reprovado + tendência CRESCENDO | +0.5 |
| FCF tendência CAINDO | −0.5 |
| FCF reprovado + tendência CRESCENDO | +0.5 |

**Score final:** `clamp(score_fase1 + modificadores, 0, 10)`

**Classificação:** ≥ 7 → FORTE | 4–6 → MODERADO | ≤ 3 → FRACO

---

### 7.7 FCF/Lucro — Qualidade do Lucro

```python
FCF = FCO (Fluxo de Caixa Operacional) - |CapEx|
fcf_lucro_ratio = FCF / Lucro_Liquido
```

| Faixa | Cor | Significado |
|-------|-----|------------|
| ≥ 80% | 🟢 Verde | Excelente — lucro é essencialmente caixa real |
| 50–80% | 🟡 Amarelo | Bom |
| < 50% | 🔴 Vermelho | Atenção |

---

### 7.8 Acumulação Silenciosa (Estratégia Barsi)

Barsi identifica o momento de compra observando quando preço E volume estão abaixo da média — "mãos fortes" acumulando silenciosamente.

**Acum. 6m:**
```python
cond = (Close < close_avg_6m) AND (Volume < volume_avg_6m)
accumulation_score = (dias_cond_true / total_dias) * 100
```

**Acum. 30d:** mesmo critério, janela de 1 mês.

**Interpretação:** ≥ 60% Verde | 40–60% Amarelo | < 40% Cinza

---

### 7.9 BRank — Ranking Unificado Buffett × Barsi × Bazin

**Campo JSON:** `unified_rank` (float 0–100)
**Implementação:** `decision_service.py` → `_calc_unified_rank(entry)`

#### O problema que o BRank resolve

Os três scores existentes medem dimensões **independentes**:
- **Score (0-100)** — amplitude: 21 critérios binários
- **MOAT (0-10)** — qualidade: vantagem competitiva Buffett
- **Piotroski (0-9)** — saúde: solidez financeira

O BRank **consolida tudo em uma única escala comparável**, ponderando cada dimensão pela sua importância filosófica.

#### Passo 1 — Normalização para [0, 1]

| Métrica | Normalização | Cap / Observação |
|---------|-------------|-----------------|
| `weighted_score` | `score / 100` | — |
| `buffett_moat_score` | `moat / 10` | — |
| `piotroski_score` | `pio / 9` | — |
| `fcf_lucro_ratio` | `clamp(fcf, 0, 1.5) / 1.5` | Cap em 1.5. Se null → 0.3 (penalidade leve) |
| `dy_real` | `min(dy / 12.0, 1.0)` | Cap em 12%: yield acima disso frequentemente indica queda de preço |
| `payout` | tent function com pico em 60% | Zona ideal Bazin: 40–80% |

**Tent function do Payout:**
```python
if payout is None or payout < 0:
    payout_n = 0.0
elif payout <= 60:
    payout_n = payout / 60.0          # sobe linearmente até 60%
elif payout <= 100:
    payout_n = (100 - payout) / 40.0  # cai linearmente de 60% a 100%
else:
    payout_n = 0.0
```

#### Passo 2 — Soma Ponderada

```
BRank_base = 0.30 × score_n
           + 0.20 × moat_n
           + 0.20 × piotroski_n
           + 0.15 × dy_n
           + 0.10 × fcf_n
           + 0.05 × payout_n
```

| Métrica | Peso | Justificativa |
|---------|------|--------------|
| `weighted_score` | **30%** | Amplitude — "checklist completa" de 21 critérios |
| `buffett_moat_score` | **20%** | Qualidade estrutural — fator mais ligado à performance de longo prazo |
| `piotroski_score` | **20%** | Saúde financeira **independente** — impede empresa fragilizada compensar com DY alto |
| `dy_real` | **15%** | Versão contínua: DY de 9% é muito melhor que 6%, o binário do Score não captura |
| `fcf_lucro_ratio` | **10%** | Qualidade do lucro — distingue lucro contábil de caixa real |
| `payout` | **5%** | Sustentabilidade. Peso menor: Score já cobre faixa 40–80% de forma binária |

#### Passo 3 — Gates Binários (penalidades multiplicativas)

| Condição | Penalidade | Por que multiplicativo |
|---------|-----------|----------------------|
| `owner_earnings_positivo = False` | × 0.85 (−15%) | Empresa consome mais caixa do que gera — sinal grave para Buffett |
| `fcf_lucro_ratio < 0` (FCF negativo) | × 0.85 (−15%) | FCF negativo: empresa não gera caixa suficiente para cobrir investimentos |

**Por que multiplicativo:** subtrair valor fixo seria arbitrário. Multiplicar por 0.85 aplica penalidade **proporcional** — empresa com BRank 80 cai para 68; com BRank 40 cai para 34.

Se ambos os gates disparam: `penalty = 0.85 × 0.85 = 0.7225` → penalidade total de ~28%.

#### Fórmula Completa

```python
# decision_service.py → _calc_unified_rank(entry)

penalty = 1.0
if not entry.get("owner_earnings_positivo", True):
    penalty *= 0.85
if fcf_r is not None and fcf_r < 0:
    penalty *= 0.85

unified_rank = round(BRank_base * penalty * 100, 1)
```

#### Interpretação e Cores

| Faixa BRank | Cor | Interpretação |
|------------|-----|--------------|
| ≥ 70 | 🟢 Verde | Excelente |
| 45–69 | 🟡 Amarelo | Moderado |
| < 45 | 🔴 Vermelho | Baixo |

> **Nota frontend:** `wscoreClass()` usa thresholds ligeiramente diferentes (≥65 verde, ≥45 amarelo, <45 vermelho). A documentação aqui reflete os thresholds conceituais.

#### Onde aparece

| Local | Como aparece |
|-------|-------------|
| **Tabela Screening** | Coluna `BRank` (ordenável), pill colorida |
| **Tabela Carteira (Ações)** | Coluna `BRank` entre FCF/L e Sinal |
| **Cards Favoritos** | Linha de métricas: `Score XX% · BRank YY · DY Z%` |
| **Tabela Favoritos** | Coluna `BRank` entre Score e DY |
| **Modal de detalhe — Radar** | 7º eixo do gráfico heptagonal |

#### Sanity Check — Exemplos Esperados

| Perfil da empresa | BRank esperado |
|------------------|---------------|
| MOAT 9, Piotroski 8, DY 8%, Score 75, FCF/L 110%, Payout 60% | ~88–92 |
| MOAT 5, Piotroski 6, DY 6%, Score 55, FCF/L 80%, Payout 50% | ~60–65 |
| MOAT 2, Piotroski 3, DY 9%, Score 40, FCF/L negativo | ~28–35 (gates disparam) |
| MOAT 7, Piotroski 7, DY 3%, Score 60, OE negativo | ~47–52 (gate OE) |

---

### 7.11 Detector de Resultado Não Recorrente

**Campo JSON:** `resultado_nao_recorrente` (bool) em `buffett_moat.trends_values`
**Implementação:** `valuation_calculator.py` → `_calc_buffett_moat_score()`, após construir `_ext_ml_hist`

#### Problema que resolve

Eventos tributários ou judiciais irrepetíveis (créditos da Lei do Bem, recuperação de DIFAL, IR diferido) inflam o lucro líquido de um único ano, distorcendo todos os scores derivados:
- Piotroski P3 (`lucro_crescendo`) e P7 (`margens_expandindo`) disparam `True` incorretamente
- Buffett Moat: `moat_ml_trend = CRESCENDO` e `moat_roe_trend = CRESCENDO` por spike de ML/ROE
- BRank: sobe por melhora ilusória de margens e rentabilidade

**Exemplo real — ALLD3 2025:**
- ML 2025: 6,04% (inclui R$389M em crédito Lei do Bem + DIFAL = 117% do LL)
- ML média 2021–2024: 2,81%
- Ratio: 6,04 / 2,81 = **2,2× → acima do limiar 1,8×**
- Receita 2025: −0,3% → **abaixo de 10%**
- Resultado: `resultado_nao_recorrente = True`

#### Fórmula

```python
# Requer ext_ml_hist com pelo menos 5 anos
ml_ultimo      = ext_ml_hist[0]          # ML do ano mais recente
prev_valid     = [v for v in ext_ml_hist[1:5] if v is not None]  # até 4 anos anteriores
ml_media_prev  = sum(prev_valid) / len(prev_valid)   # exige >= 3 anos válidos

rec_ultimo     = dre["receita_liquida"][ext_anos[0]]
rec_anterior   = dre["receita_liquida"][ext_anos[1]]
rec_growth     = (rec_ultimo / rec_anterior) - 1     # crescimento YoY

resultado_nao_recorrente = (
    ml_media_prev > 0
    and (ml_ultimo / ml_media_prev) >= 1.8   # ML spike: >= 1.8× média anterior
    and (rec_growth is None or rec_growth < 0.10)  # receita flat (<10%)
)
```

#### Limiares

| Parâmetro | Valor | Justificativa |
|-----------|-------|--------------|
| Ratio ML mínimo para spike | **1,8×** | Captura spikes como ALLD3 2025 (2,2×) e 2021 (2,5×) sem gerar falsos positivos em turnarounds genuínos |
| Receita máxima aceita | **10%** | Turnaround real geralmente vem acompanhado de crescimento de receita |
| Anos anteriores mínimos | **3** (de 4 buscados) | Evita falso positivo quando há poucos anos históricos |

#### Comportamento quando ativado

O flag é **apenas informacional** — não altera scores diretamente. O impacto é na **UI** (ver `brain_frontend.md`):
- Badge amarelo ⚠ no modal de tendências históricas
- Alerta ao usuário para investigar notas explicativas antes de usar os scores

> **Nota:** O flag detecta o *sintoma* (spike de ML com receita flat), não a causa. Pode ativar em turnarounds legítimos de margens sem crescimento de receita. Sempre validar contra as notas dos demonstrativos financeiros.

---

### 7.10 DCF — Valor Intrínseco (VI)

**Implementação:** `valuation_calculator.py` → `_calc_dcf(price_now, p_l, cagr_lucro, fcf_lucro_ratio, moat_label)`

**Campo JSON:** `dcf` (objeto) dentro do retorno de `/api/valuation/<ticker>`

#### Filosofia

Buffett: o valor de um negócio é o valor presente de todos os fluxos de caixa futuros. A taxa de desconto mínima é **10% a.a. — independente da Selic**. Mesmo em ambiente de juros 7%, usar 7% como desconto superestima o VI e reduz a margem de segurança.

#### Base do Cálculo — LPA

```python
lpa = price_now / p_l   # Lucro Por Ação aproximado
```

O LPA é derivado do preço e do P/L (disponíveis em `indicators`), sem necessidade de `shares_outstanding`. É o ponto de partida: representa o lucro atual gerado por ação.

#### Penalidade FCF — Crescimento, Não Base

O `fcf_lucro_ratio` penaliza o **crescimento projetado**, nunca a base. Isso evita distorção em empresas com FCF baixo mas lucro legítimo.

```python
if   fcf_lucro_ratio is None:   fcf_penalty = 0.75   # sem dados: conservador
elif fcf_lucro_ratio < 0:       fcf_penalty = 0.50   # FCF negativo: crescimento limitado
elif fcf_lucro_ratio >= 0.8:    fcf_penalty = 1.00   # qualidade excelente: pleno
else:                           fcf_penalty = 0.50 + 0.50 * (fcf_lucro_ratio / 0.8)
```

#### Teto de Crescimento por MOAT

| MOAT label | Cap fase 1 | Constante |
|-----------|-----------|-----------|
| FORTE     | 15%       | `DCF_MOAT_CAP_FORTE = 0.15` |
| MODERADO  | 10%       | `DCF_MOAT_CAP_MODERADO = 0.10` |
| FRACO     | 5%        | `DCF_MOAT_CAP_FRACO = 0.05` |

#### Fórmula — 2-Stage DCF

```python
cagr_raw = cagr_lucro / 100.0   # CAGR histórico 5 anos
g1_base  = min(max(cagr_raw, 0), moat_cap[moat_label])
g1       = g1_base * fcf_penalty   # fase 1 (anos 1–5): crescimento real
g2       = g1 * 0.5                # fase 2 (anos 6–10): fade 50%

r  = 0.10   # taxa de desconto (Buffett mínimo)
gT = 0.035  # crescimento terminal perpétuo (inflação + PIB longo prazo)

iv = 0.0
cf = lpa
for t in range(1, 11):
    g  = g1 if t <= 5 else g2
    cf = cf * (1 + g)
    iv += cf / (1 + r) ** t

# Terminal Value — Gordon Growth Model
iv += (cf * (1 + gT) / (r - gT)) / (1 + r) ** 10
```

#### Margem de Segurança

```python
margin_of_safety = (iv - price_now) / iv * 100
```

Escala: **0% a 100%** (100% = ação custando zero — máximo teórico).  
Não usar `(iv - price) / price` — esse é "upside %", não margem de segurança Graham/Buffett.

| Faixa MoS | Cor | Significado |
|-----------|-----|------------|
| ≥ 20%     | 🟢 Verde  | Boa margem — ação abaixo do VI com folga |
| 0–20%     | 🟡 Amarelo | Margem estreita — próximo ao VI |
| Negativo  | 🔴 Vermelho | Acima do VI pelo critério DCF |
| < −200%   | 🔴 "< −200%" | Display truncado para evitar valores extremos |

#### Output do campo `dcf`

```json
{
  "intrinsic_value":  63.86,
  "margin_of_safety": 58.1,
  "lpa":              4.2105,
  "g1_pct":           3.61,
  "g2_pct":           1.81,
  "fcf_penalty":      0.72
}
```

#### Quando retorna `null`

- `p_l` ausente ou ≤ 0 (empresa com prejuízo ou sem dado)
- `price_now` ausente ou zero

#### Sanity Check

| Empresa | Preço | VI | MoS | Nota |
|---------|-------|-----|-----|------|
| ROMI3 (CAGR -13%, FCF neg.) | R$7,08 | ~R$10,22 | +30,8% | CAGR negativo → g1=0, apenas terminal value |
| UNIP6 (FCF 6,79%, MOAT MOD) | R$62,03 | ~R$108,66 | +42,9% | FCF penalty=0.54 limita crescimento a 5,4% |
| ALLD3 (FCF 652%, MOAT FORTE) | R$6,75 | ~R$98,17 | +93,1% | Preço muito abaixo do VI — MoS perto do teórico máximo |
| TASA4 (p_l=null) | — | — | — | Sem P·L: DCF inaplicável |

#### Por que FCF penalty no crescimento, não na base?

Se usarmos `base = lpa * fcfQ`, uma empresa com `fcf_lucro_ratio = 6,79%` (UNIP6) teria base = R$0,44 → VI = R$9,62 → MoS = −544%. Isso distorce porque trata FCF baixo como se a empresa "ganhasse menos" — mas o LPA é o lucro reportado, independente do FCF. A qualidade baixa do FCF deve penalizar *quanto o crescimento é sustentável*, não *quanto a empresa ganha hoje*.

---

## 8. Sistema de Medalhas e Selos

### 8.1 Medalha de Ouro 🥇 — Ouro Barsi

**A combinação mais rara e favorável.** Todos obrigatórios:
```python
is_gold = (price_now <= vpa) AND (price_now <= price_target_6pct) AND dividend_growing
```
- Preço ≤ VPA: mercado vendendo abaixo do patrimônio
- Preço ≤ Alvo 6%: yield implícito ≥ 6%
- Dividendo crescente: caixa saudável e em crescimento

---

### 8.2 Medalha de Prata 🥈 — Margem Dupla

```python
is_silver = (price_now <= vpa) AND (price_now <= price_target_6pct) AND NOT is_gold
```
Margem de segurança dupla: desconto patrimonial + yield atraente. Sem exigir crescimento de dividendo.

---

### 8.3 Medalha de Bronze 🥉 — Atrativo por Dividendo

```python
is_bronze = (price_now <= price_target_6pct) AND (price_now > vpa)
```
Zona de compra Bazin, mas sem desconto patrimonial (preço > VPA).

---

### 8.4 Selo Buffett ★ — Excelência de Negócio

```python
is_buffett_seal = (
    buffett_moat.get("score", 0) >= 7           # Moat FORTE
    and buffett_cf.get("fcf_quality_ok", False)  # FCF/Lucro >= 80%
    and buffett_cf.get("owner_earnings_positivo", False)  # OE > 0
)
```
Pode coexistir com qualquer medalha ou mesmo com zona CARO.

---

### 8.5 Filtro BEST — Setores Barsi

```python
def _is_best(sector_info):
    sub = sector_info.get("subsetor", "")
    seg = sector_info.get("segmento", "")

    if seg == "Bancos":            return True  # B — Bancos
    if sub == "Energia Elétrica":  return True  # E — Elétricas
    if sub == "Água e Saneamento": return True  # S — Saneamento
    if sub == "Previdência e Seguros" or "Segur" in seg: return True  # S — Seguros
    return False
```

---

## 10. Tabela de Referência — Todos os Limiares

### Bazin/Barsi — Dividendos

| Parâmetro | Valor | Constante |
|-----------|-------|-----------|
| Yield mínimo (zona MONITORAR) | 5% | `BASIN_MIN = 0.05` |
| Yield base (zona COMPRA) | 6% | `BASIN_BASE = 0.06` |
| Yield agressivo (COMPRA_FORTE) | 8% | `BASIN_MAX = 0.08` |
| DY% mínimo aprovado | 6% | `DIVIDEND_YIELD_MIN = 6.0` |
| Payout mínimo saudável | 40% | `PAYOUT_MIN = 40.0` |
| Payout máximo saudável | 80% | `PAYOUT_MAX = 80.0` |
| Anos mínimos com dividendo | 5 | `DIVIDEND_YEARS_MIN = 5` |

### Graham — Valuation

| Parâmetro | Valor | Constante |
|-----------|-------|-----------|
| P/L máximo | 15 | `P_L_MAX = 15.0` |
| P/VP máximo | 1.5 | `P_VP_MAX = 1.5` |
| Graham Combo máximo | 22.5 | `GRAHAM_COMBO = 22.5` |
| Liquidez Corrente mínima | 2.0 | `LIQUIDEZ_CORRENTE_MIN = 2.0` |
| DL/PL máximo | 1.0 | `DL_PL_MAX = 1.0` |
| DL/EBITDA máximo | 3.0 | `DL_EBITDA_MAX = 3.0` |
| Passivo/Ativo máximo | 65% | `PASSIVO_ATIVO_MAX = 0.65` |

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
| Margem Líquida mínima (moat) | 20% | vs. 10% |
| ROE mínimo (moat) | 20% | vs. 10% |
| ROIC mínimo (moat) | 15% | vs. 10% |
| DL/PL máximo (moat) | 0.5 | vs. 1.0 |
| CAGR Lucro (moat) | ≥ 10% | vs. 5% |
| FCF Quality mínimo | 80% | `BUFFETT_FCF_QUALITY_MIN = 0.80` |
| CapEx/Lucro máximo (moat) | 25% | `BUFFETT_CAPEX_MOAT_MAX = 0.25` |

### Piotroski — Limiares Conservadores

| Sinal | Limiar | vs. Screening principal |
|-------|--------|------------------------|
| DL/PL (P4) | ≤ 0.5 | vs. 1.0 |
| Liquidez Corrente (P5) | ≥ 1.5 | vs. 2.0 (Graham) |
| Passivo/Ativo (P6) | ≤ 40% | vs. 65% |
| ROE forte (P9) | ≥ 15% | vs. 10% |

### BRank — Ranking Unificado

| Parâmetro | Valor |
|-----------|-------|
| Peso `weighted_score` | 30% |
| Peso `buffett_moat_score` | 20% |
| Peso `piotroski_score` | 20% |
| Peso `dy_real` | 15% |
| Peso `fcf_lucro_ratio` | 10% |
| Peso `payout` | 5% |
| Cap DY (normalização) | 12% |
| Cap FCF/L (normalização) | 150% |
| Payout ótimo (tent peak) | 60% |
| Gate OE negativo | × 0.85 |
| Gate FCF negativo | × 0.85 |
| Threshold verde (frontend) | ≥ 65 |
| Threshold amarelo (frontend) | ≥ 45 |
| Threshold vermelho (frontend) | < 45 |

### DCF — Valor Intrínseco

| Parâmetro | Valor | Constante |
|-----------|-------|-----------|
| Taxa de desconto | 10% a.a. | `DCF_DISCOUNT_RATE = 0.10` |
| Crescimento terminal | 3,5% | `DCF_TERMINAL_GROWTH = 0.035` |
| Horizonte de projeção | 10 anos | `DCF_PROJECTION_YEARS = 10` |
| Cap crescimento — MOAT FORTE | 15% | `DCF_MOAT_CAP_FORTE = 0.15` |
| Cap crescimento — MOAT MODERADO | 10% | `DCF_MOAT_CAP_MODERADO = 0.10` |
| Cap crescimento — MOAT FRACO | 5% | `DCF_MOAT_CAP_FRACO = 0.05` |
| FCF penalty — sem dados | 75% | hardcoded |
| FCF penalty — FCF negativo | 50% | hardcoded |
| Display MoS mínimo | "< −200%" | display cap frontend |
| MoS verde (boa margem) | ≥ 20% | frontend threshold |
| MoS amarelo (estreita) | 0–20% | frontend threshold |

### Técnico/Liquidez

| Parâmetro | Valor | Constante |
|-----------|-------|-----------|
| Liquidez diária mínima | R$200k/dia | `LIQUIDEZ_DIARIA_MIN = 200000.0` |
| Acumulação mínima | 50% | `ACCUMULATION_SCORE_MIN = 50.0` |
| Atualização de preço | 30 min | `PRICE_UPDATE_INTERVAL_HOURS = 0.5` |
| Atualização histórico | 7 dias | `HISTORY_UPDATE_INTERVAL_DAYS = 7` |
| Atualização financials | 30 dias | `FINANCIALS_UPDATE_INTERVAL_DAYS = 30` |
