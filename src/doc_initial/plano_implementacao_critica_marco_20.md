# Plano de Implementação — Correções da Crítica de 20/03/2026
> Baseado em `critica_marco_20_2026.md`
> Data: 2026-03-20

---

## Status das 10 Falhas Identificadas

| # | Falha | Status Atual no Código | Prioridade |
|---|-------|------------------------|------------|
| F1 | Moat Score com 4 anos — aviso ausente na UI | ⚠️ Sem aviso | Média |
| F2 | Payout > 100% gera COMPRA | ❌ Sem hard filter na pré-qualificação | **Urgente** |
| F3 | Owner Earnings usa CapEx total, não manutenção | ❌ `buffett_fetcher.py` usa `abs(capex)` total | Alta |
| F4 | Tendências de MB/ROE não impactam o Moat Score | ✅ **Implementado** — modificadores ±0.5 no Moat Score + exibição no modal | Alta |
| F5 | Setor Financeiro penalizado por liquidez corrente | ✅ **Já corrigido** via `_is_financial` (proxy `pl_ativo`) | — |
| F6 | `avg_dividends_5y` é média simples | ✅ **Implementado** — média ponderada por recência [1,2,3,4,5] em `history_fetcher.py` | Alta |
| F7 | Gestão não avaliada e sem aviso | ❌ Campo inexistente | Média |
| F8 | Lista de decisão mistura COMPRA e CARO | ❌ Frontend ordena por `p_now_p_min` sem separar zonas | **Urgente** |
| F9 | `dividend_growing` é binário | ✅ **Parcialmente corrigido** — tolerância de 10% (`>= prior_max * 0.90`) em `history_fetcher.py` | Alta |
| F10 | Zero testes na lógica de negócio | ❌ `valuation_calculator.py` e `decision_service.py` sem cobertura | Alta |

> **Nota F5:** A correção do setor financeiro já existe via proxy `pl_ativo <= 0.20` em `valuation_calculator.py` (linhas 383 e 426-427). O Piotroski, porém, ainda não tem essa exceção — corrigido na Fase 1.

---

## Fases de Implementação

---

### FASE 1 — Correções Urgentes
**Objetivo:** Eliminar recomendações incorretas que custam dinheiro.
**Esforço:** Baixo | **Impacto:** Crítico

---

#### 1.1 Hard Filter: Payout > 100% → INQUALIFICÁVEL

> **⚠️ STATUS: TENTADO EM 22/03/2026 — REVERTIDO**
>
> O hard filter foi implementado, testado e revertido no mesmo dia. Ver justificativa completa em `critica_marco_20_2026.md` — FALHA 2.
>
> **Resumo do motivo do abort:** 50 tickers com payout > 100% foram encontrados nos dados reais, incluindo VALE3 (176%), GRND3 (172%), TAEE (267%), ABEV3 (113%), BBDC (104%), ITSA4 (129%). Bloquear todas essas empresas seria um falso positivo agressivo. Os payouts > 100% em empresas sólidas decorrem de: dividendos extraordinários pontuais, JCP que reduz o lucro contábil artificialmente, lucro deprimido num único ano com manutenção de dividendo histórico, ou distorção de janela temporal nos dados do StatusInvest.
>
> **Solução adotada:** Alerta visual no modal (vermelho se payout > 100%, verde se ≤ 100%). O score já penaliza via `payout_ok = False` (−1.5 pts no weighted score). A decisão final fica com o usuário.

**Arquivo:** `backend/services/valuation_calculator.py`
**Função:** `calculate()` — bloco de pré-qualificação (após linha 367)

**Problema:** TGMA3 com payout 104.32% aparece como COMPRA. Empresa paga dividendo com dívida ou reserva. Dividendo insustentável.

**Mudança planejada (não executada):**
```python
# Pré-qualificação adicional: payout insustentável
payout_raw = _safe_float((repo.get_history(ticker) or {}).get("payout"))
if payout_raw is not None and payout_raw > 100:
    pre_qual_failed.append("payout_insustentavel")
    if not force:
        return None
```

**Teste que validaria:**
```python
def test_payout_acima_100_nao_qualifica():
    # empresa com payout=104 não pode entrar na lista de decisão
    result = calculate("TGMA3_MOCK")
    assert result is None
```

---

#### 1.2 Separar Lista de Decisão por Zona no Frontend

**Arquivo:** `frontend/index.html`
**Função:** Lógica de renderização da tabela de decisão

**Problema:** MDIA3 (zona CARO, DY 3.9%) aparece em 2º lugar na lista porque tem `p_now_p_min` baixo. Usuário interpreta como oportunidade.

**Mudança na lógica de renderização:**
```javascript
// Separar stocks por zona antes de renderizar
const compraForte = stocks.filter(s => s.zone === 'COMPRA_FORTE');
const compra      = stocks.filter(s => s.zone === 'COMPRA');
const monitorar   = stocks.filter(s => s.zone === 'MONITORAR');
const caro        = stocks.filter(s => s.zone === 'CARO');

// Renderizar seções separadas:
// 1. COMPRA_FORTE (verde escuro) — acima do fold
// 2. COMPRA (verde) — visível
// 3. MONITORAR (amarelo) — colapsado por padrão
// 4. CARO (vermelho/cinza) — oculto, requer clique para expandir
```

**Regra:** Dentro de cada seção, manter ordenação por `p_now_p_min` ASC.

---

#### 1.3 Piotroski: Exceção para Setor Financeiro no Critério P5

**Arquivo:** `backend/services/valuation_calculator.py`
**Função:** `_calc_piotroski()`

**Problema:** O critério P5 (`liquidez_corrente >= 1.5`) penaliza bancos no Piotroski mesmo que `_is_financial` já isente o score principal. A informação `_is_financial` não passa para `_calc_piotroski`.

**Mudança:** Passar `is_financial` como parâmetro:
```python
def _calc_piotroski(indicators: dict, history: dict, is_financial: bool = False) -> dict:
    ...
    # P5: bancos têm liquidez corrente < 1 por design — isento para setor financeiro
    p5 = is_financial or (liq_corrente is not None and liq_corrente >= rules.PIOTROSKI_LIQ_CORRENTE_MIN)
    # P6: passivo/ativo alto é estrutural em bancos — isento para setor financeiro
    p6 = is_financial or (passivo_ativo is not None and passivo_ativo <= rules.PIOTROSKI_PASSIVO_ATIVO_MAX)
```

**Em `calculate()`:**
```python
piotroski = _calc_piotroski(_indicators_raw, history, is_financial=_is_financial)
```

---

### FASE 2 — Qualidade dos Scores
**Objetivo:** Scores que refletem a realidade do negócio, não só o snapshot.
**Esforço:** Médio | **Impacto:** Alto

---

#### 2.1 Média Ponderada para `avg_dividends_5y` ✅ IMPLEMENTADO (22/03/2026)

**Arquivo:** `backend/services/history_fetcher.py`
**Função:** Onde `avg_dividends_5y` é calculado

**Problema:** ABCB4 com dividendo crescendo de R$0.98 para R$2.62 tem target subestimado em 35% pela média simples.

**Mudança:**
```python
def _calc_avg_dividends_weighted(dividends_by_year: dict) -> float:
    """
    Média ponderada dos dividendos anuais: anos recentes têm maior peso.
    Ex: 5 anos → pesos [1, 2, 3, 4, 5] (mais recente = peso 5)
    """
    years = sorted(dividends_by_year.keys())  # do mais antigo ao mais recente
    values = [dividends_by_year[y] for y in years]
    weights = list(range(1, len(values) + 1))  # [1, 2, 3, 4, 5]
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / total_weight
```

**Em `rules.py`:**
```python
# Pesos para média ponderada de dividendos (índice 0 = mais antigo)
DIVIDEND_WEIGHTED = True   # feature flag para ativar/desativar
```

---

#### 2.2 `dividend_growing` com Tendência Linear (regressão simples) — ✅ PARCIALMENTE IMPLEMENTADO

**Arquivo:** `backend/services/history_fetcher.py`
**Função:** Onde `dividend_growing` é calculado

**Problema:** Empresa com dividendos `[0.50, 1.00, 1.50, 2.00, 1.90]` recebe `False` por uma queda pontual de 5% no último ano.

**Mudança:**
```python
def _calc_dividend_trend(dividends_by_year: dict) -> bool:
    """
    Retorna True se a tendência geral dos dividendos é crescente
    (coeficiente angular da regressão linear > 0).
    Critério: ao menos 3 anos de dados para regressão.
    Fallback para critério binário se menos de 3 anos.
    """
    years = sorted(dividends_by_year.keys())
    values = [dividends_by_year[y] for y in years]

    if len(values) < 3:
        # Fallback: critério original binário
        return values[-1] >= max(values[:-1]) if len(values) >= 2 else False

    n = len(values)
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(values) / n
    numerator   = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
    denominator = sum((xi - x_mean) ** 2 for xi in x)

    if denominator == 0:
        return False
    slope = numerator / denominator
    return slope > 0  # tendência positiva = True
```

---

#### 2.3 Tendências de MB e ROE Impactam o Moat Score ✅ IMPLEMENTADO (22/03/2026)

**Arquivo:** `backend/services/valuation_calculator.py`
**Função:** `_calc_buffett_moat_score()`

**Problema:** Empresa com Margem Bruta 42% em tendência CAINDO (52%→42% em 4 anos) recebe ✅ no critério de MB. Isso é um moat sendo erodido.

**Lógica dos modificadores de tendência:**
```python
# Modificador de tendência aplicado sobre critérios já aprovados:
# - Critério aprovado + tendência CAINDO  → -0.5 ponto (penalidade)
# - Critério aprovado + tendência CRESCENDO → sem alteração (mantém)
# - Critério reprovado + tendência CRESCENDO → +0.5 ponto (bônus de recuperação)

TREND_PENALTY  = -0.5  # em rules.py
TREND_BONUS    =  0.5  # em rules.py

tr = history.get("buffett_trends") or {}
mb_trend  = tr.get("margem_bruta_trend")   # "CRESCENDO" / "CAINDO" / "ESTAVEL"
roe_trend = tr.get("roe_trend")

# Aplicar modificador na Margem Bruta
if mb_trend == "CAINDO":
    score += rules.TREND_PENALTY   # penaliza moat erodindo
elif mb_trend == "CRESCENDO" and not flags["moat_margem_bruta"]:
    score += rules.TREND_BONUS     # bônus: ainda não passa, mas está melhorando

# Aplicar modificador no ROE
if roe_trend == "CAINDO":
    score += rules.TREND_PENALTY
elif roe_trend == "CRESCENDO" and not flags["moat_roe"]:
    score += rules.TREND_BONUS

# Garantir bounds [0, 10]
score = max(0, min(10, score))
```

**Em `rules.py`:**
```python
MOAT_TREND_PENALTY = -0.5   # penalidade por tendência CAINDO em critério aprovado
MOAT_TREND_BONUS   =  0.5   # bônus por tendência CRESCENDO em critério reprovado
```

---

#### 2.4 Owner Earnings com CapEx de Manutenção (proxy D&A)

> **⚠️ STATUS: ESTUDADO EM 22/03/2026 — NÃO AUTOMATIZADO POR ENQUANTO**
>
> Foi conduzida pesquisa aprofundada com dados reais de WEGE3 e VALE3 (2021–2023) para validar o proxy `CapEx manutenção ≈ D&A`. Ver detalhes completos em `critica_marco_20_2026.md` — FALHA 3.
>
> **Resumo dos achados:**
> - WEGE3: D&A representa 32–38% do CapEx total. Proxy subestima manutenção futura porque a base de ativos cresce rápido com as expansões internacionais. Diferença de +21% no Owner Earnings usando proxy vs. CapEx total.
> - VALE3: DD&A subestima o CapEx de manutenção real em ~37%. O sustaining CapEx reportado pela Vale no RI (US$ 4,2 bi) é 37% maior que o DD&A (US$ 3,07 bi). O DD&A inclui depleção contábil, mas abrir novas frentes de lavra custa mais do que a depleção registrada.
> - GRND3: CapEx ≈ D&A — proxy preciso para empresas maduras de consumo.
> - Bancos/Seguradoras: D&A irrelevante para o modelo de negócio — proxy não se aplica.
>
> **Por que não automatizar:** para aplicar o proxy corretamente seria necessário classificar cada empresa por setor e estágio de maturidade — dados que o sistema não possui de forma estruturada. Um proxy genérico aplicado a mineração (VALE3) ou utilities subestimaria o CapEx de manutenção em ~37%, inflando artificialmente o Owner Earnings. Aplicado a bancos, seria irrelevante. Automatizar sem essa distinção cria falsa precisão.
>
> **Decisão:** manter o cálculo atual (CapEx total — mais conservador) e adicionar nota explicativa no frontend para o usuário interpretar corretamente para empresas em expansão.

**Arquivo:** `backend/services/buffett_fetcher.py`
**Função:** `fetch_cashflow()`

**Problema:** `Owner Earnings = NI + D&A − CapEx_total` subvaloriza empresas em expansão. WEGE3 tem CapEx de expansão alto que distorce o Owner Earnings real.

**Mudança planejada (não executada — ver nota acima):**
```python
# CapEx de manutenção (proxy conservador de Buffett): usa D&A como estimativa
# Fundamento: em steady-state, manutenção ≈ reposição do ativo depreciado
capex_manutencao = abs(da)   # D&A como proxy do CapEx de manutenção

# Owner Earnings correto:
owner_earnings_manutencao = net_income + da - capex_manutencao

# Manter cálculo original como referência (CapEx total = mais conservador)
owner_earnings_total = net_income + da - abs(capex)

# Expor ambos no JSON:
return {
    ...
    "owner_earnings":            owner_earnings_total,       # versão conservadora (atual)
    "owner_earnings_manutencao": owner_earnings_manutencao,  # versão Buffett correta
    "capex_total":               abs(capex),
    "capex_manutencao_proxy":    abs(da),
    "capex_expansao_estimado":   max(0, abs(capex) - abs(da)),  # estimativa do CapEx de crescimento
}
```

**Pré-requisito para retomar:** mapear `sectorname` de cada ticker para um dos perfis (expansão acelerada / madura / mineração / financeiro) e aplicar o proxy apenas onde ele é válido. Sem esse mapeamento, a automação piora a análise ao invés de melhorá-la.

---

### FASE 3 — Testes do Core
**Objetivo:** Garantir que a lógica de decisão nunca quebre silenciosamente.
**Esforço:** Médio | **Impacto:** Alto (confiabilidade)

---

#### 3.1 Testes para `valuation_calculator.py`

**Arquivo novo:** `backend/tests/test_valuation_calculator.py`

**Casos obrigatórios:**

```python
# 1. Hard filter payout > 100%
def test_payout_insustentavel_nao_qualifica():
    """Payout 104% deve retornar None na pré-qualificação."""

# 2. Zona COMPRA_FORTE: preço abaixo do target 8%
def test_zone_compra_forte():
    """Preço R$20 com target_8pct R$22 → zone = COMPRA_FORTE"""

# 3. Zona COMPRA: preço entre target_8 e target_6
def test_zone_compra():
    """Preço R$25 com target_6pct R$28, target_8pct R$22 → zone = COMPRA"""

# 4. Zona CARO: preço acima do target_5%
def test_zone_caro():
    """Preço R$40 com target_5pct R$35 → zone = CARO"""

# 5. Moat Score máximo com todos os critérios atendidos
def test_moat_score_maximo():
    """MB=45, ML=25, ROE=25, ROIC=16, DL/PL=0.3, CAGR_L=12, CAGR_R=8, div_growing=True → score=10"""

# 6. Moat Score mínimo
def test_moat_score_minimo():
    """Todos critérios abaixo do threshold → score=0, label=FRACO"""

# 7. Setor financeiro: liquidez_corrente não penaliza banco
def test_banco_nao_penalizado_liquidez_corrente():
    """pl_ativo=0.08 (banco) + liquidez_corrente=0.7 → liquidez_corrente_ok=True"""

# 8. is_gold requer abaixo do VPA
def test_is_gold_false_acima_vpa():
    """Preço R$35 > VPA R$30 → is_gold=False mesmo com outros critérios ok"""

# 9. is_gold true com todos os critérios
def test_is_gold_true():
    """Abaixo VPA + abaixo target_6 + dividend_growing=True → is_gold=True"""

# 10. Tendência CAINDO penaliza Moat Score
def test_moat_trend_penaliza_mb_caindo():
    """MB=42% (aprovado) + mb_trend=CAINDO → score recebe penalidade de -0.5"""
```

---

#### 3.2 Testes para `decision_service.py`

**Arquivo novo:** `backend/tests/test_decision_service.py`

**Casos obrigatórios:**

```python
# 1. Ordenação dentro de cada zona
def test_ordenacao_por_zona_e_pmin():
    """COMPRA_FORTE deve aparecer antes de COMPRA, que aparece antes de MONITORAR."""

# 2. zona CARO não contamina zona COMPRA na lista retornada
def test_caro_separado_de_compra():
    """Stocks com zone=CARO não devem aparecer junto com COMPRA no output da decisão."""

# 3. DY real calculado com preço atual (não DY estático)
def test_dy_real_com_preco_atual():
    """avg_div=2.0, price_now=25.0 → dy_real=8.0 (não usa dy do JSON)"""

# 4. Buffett Seal: requer moat >= 7 + FCF quality + OE positivo
def test_buffett_seal_requer_todos_criterios():
    """moat_score=8 mas fcf_quality_ok=False → is_buffett_seal=False"""
```

---

### FASE 4 — Transparência e Aviso de Limitações
**Objetivo:** O usuário sabe exatamente o que o sistema não consegue fazer.
**Esforço:** Baixo | **Impacto:** Médio (UX e confiabilidade percebida)

---

#### 4.1 Warning de Janela de Dados no Frontend

**Arquivo:** `frontend/index.html`
**Onde:** Seção "Buffett Moat Score" no modal de cada ativo

**Adição:**
```html
<div class="moat-warning">
  ⚠️ Score baseado em dados de até 4 anos.
  Buffett recomenda mínimo de 10 anos para identificar moat real.
  Verificar histórico longo manualmente.
</div>
```

---

#### 4.2 Campo Manual `gestao_nota` por Empresa

**Arquivo:** Novo campo em `stock_history.json` (por ticker)
**Interface:** Campo editável no modal do frontend

**Estrutura:**
```json
{
  "gestao": {
    "nota": 4,
    "nota_max": 5,
    "observacao": "Gestão conservadora, histórico de alocação eficiente. CEO fundador.",
    "atualizado_em": "2026-03-20"
  }
}
```

**Impacto no Moat Score:** `gestao_nota` como multiplicador de confiança (não altera o score numérico, mas exibe badge de validação manual).

**Regra:**
- `gestao_nota >= 4` → badge 👤 GESTÃO VALIDADA (verde)
- `gestao_nota = 3`  → badge 👤 GESTÃO OK (amarelo)
- `gestao_nota <= 2` → badge ⚠️ GESTÃO DUVIDOSA (vermelho)
- ausente           → badge ❓ GESTÃO NÃO AVALIADA (cinza)

---

#### 4.3 Identificação de Setor Financeiro por `sectorname` (reforço)

**Arquivo:** `backend/services/valuation_calculator.py`
**Função:** `calculate()`

**Problema atual:** `_is_financial` usa proxy `pl_ativo <= 0.20`. Embora funcione para bancos, empresas com PL muito baixo por outros motivos podem ser marcadas incorretamente.

**Melhoria:** Combinação proxy + sectorname:
```python
_sector_lower = sector.lower() if sector else ""
_is_financial = (
    (pl_ativo is not None and pl_ativo <= rules.FINANCIAL_PL_ATIVO_MAX)
    or "financeiro" in _sector_lower
    or "banco" in _sector_lower
    or "seguro" in _sector_lower
    or "seguradora" in _sector_lower
)
```

---

## Resumo por Arquivo Modificado

| Arquivo | Mudanças | Fase |
|---------|----------|------|
| `config/rules.py` | `PAYOUT_INSUSTENTAVEL_MAX`, `MOAT_TREND_PENALTY`, `MOAT_TREND_BONUS`, `DIVIDEND_WEIGHTED` | 1, 2 |
| `services/valuation_calculator.py` | Hard filter payout, exceção Piotroski p5/p6, trend modifiers no Moat Score, `_is_financial` por sectorname | 1, 2, 4 |
| `services/history_fetcher.py` | `_calc_avg_dividends_weighted()`, `_calc_dividend_trend()` com regressão | 2 |
| `services/buffett_fetcher.py` | Owner Earnings com CapEx manutenção (proxy D&A), expor ambas versões | 2 |
| `services/decision_service.py` | Sem mudança de lógica — testes validam comportamento atual | 3 |
| `frontend/index.html` | Separação visual COMPRA/CARO, warning 4 anos, badge gestão | 1, 4 |
| `tests/test_valuation_calculator.py` | **Novo** — 10 casos críticos | 3 |
| `tests/test_decision_service.py` | **Novo** — 4 casos críticos | 3 |

---

## Ordem de Execução Recomendada

```
Fase 1a  → Hard filter payout > 100%          (30 min)
Fase 1b  → Separação visual COMPRA/CARO       (1h)
Fase 1c  → Piotroski: exceção setor financeiro (30 min)
─────────────────────────────────────────────────────────
Fase 2a  → Média ponderada dividendos         (1h)
Fase 2b  → dividend_growing com regressão     (1h)
Fase 2c  → Trend modifiers no Moat Score      (1h)
Fase 2d  → Owner Earnings manutenção          (1h)
─────────────────────────────────────────────────────────
Fase 3a  → Testes valuation_calculator        (2h)
Fase 3b  → Testes decision_service            (1h)
─────────────────────────────────────────────────────────
Fase 4a  → Warning 4 anos na UI               (30 min)
Fase 4b  → Campo gestao_nota                  (2h)
Fase 4c  → _is_financial robusto              (30 min)
```

**Estimativa total:** ~13 horas de implementação

---

## Critério de Conclusão

Cada fase está **concluída** quando:

1. Código modificado e funcionando
2. `python valuation_calculator.py BBAS3 WEGE3 TGMA3` roda sem erros
3. Testes da fase passam: `pytest backend/tests/ -v`
4. TGMA3 não aparece mais como COMPRA em `decision_stocks.json`
5. MDIA3 e TOTS3 (zona CARO) aparecem em seção separada no frontend
