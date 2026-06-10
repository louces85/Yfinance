# Swing: Desconto vs. Médias + Volume Crescente na Nota — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pontuar na nota A/B/C do swing o desconto do preço vs. médias de 1m/3m/6m (Pullback/Reversão) e o volume crescente 1m>3m (todos os setups), sem alterar detecção nem níveis de risco.

**Architecture:** Dois indicadores novos calculados em `build_context()` (`below_avgs`, `vol_rising`) a partir do OHLCV de 1 ano que o `swing_service` já baixa; `grade_setup()` passa a receber o `ctx` e soma os pesos novos; os dois campos entram no schema do `swing_data.json` para todo ticker. Spec: `docs/superpowers/specs/2026-06-10-swing-discount-volume-grade-design.md`.

**Tech Stack:** Python 3.8 (sem walrus/f-string complexa), pytest, Flask backend existente. Thresholds SEMPRE em `src/backend/config/rules.py`.

**Comando de teste (da raiz do repo):** `python3 -m pytest src/backend/tests/test_swing_service.py -v`
(o `conftest.py` injeta `src/backend` no path; imports nos testes são `from services import swing_service`, `from config import rules`)

---

## File Map

| Arquivo | Ação |
|---------|------|
| `src/backend/config/rules.py` | Modificar — 5 constantes novas no bloco Swing |
| `src/backend/services/swing_service.py` | Modificar — `_below_avg_count`, `_vol_rising`, `build_context`, `grade_setup`, `_pick_best_setup`, `analyze_ticker` |
| `src/backend/tests/test_swing_service.py` | Criar — testes dos indicadores novos e da nota |
| `src/backend/data/swing_data.json` | Regenerar ao final |
| `src/brain/brain_calculations.md` | Modificar — §7.12.1, §7.12.5, §7.12.7, tabela de limiares |

---

### Task 1: Constantes em rules.py

**Files:**
- Modify: `src/backend/config/rules.py` (bloco "Pesos do score", após `W_RR_OK`, ~linha 152)

- [ ] **Step 1: Adicionar as constantes**

Em `src/backend/config/rules.py`, dentro do bloco `# Pesos do score de qualidade (0–100) e cortes de nota`, logo após a linha `W_RR_OK = 10 ...` e antes de `GRADE_A`:

```python
W_BELOW_AVG_PER          = 4      # por média (1m/3m/6m) que o preço está abaixo — máx. 12;
                                  # só Pullback/Reversão (Rompimento está acima por natureza)
W_VOL_RISING             = 8      # volume médio 1m > volume médio 3m (acumulação) — todos os setups
```

E, no mesmo bloco Swing, logo após `MA50_SLOPE_LOOKBACK = 10 ...` (~linha 137):

```python
PRICE_AVG_SHORT_DAYS     = 21     # média de preço/volume de 1 mês (pregões)
PRICE_AVG_MID_DAYS       = 63     # média de preço/volume de 3 meses (pregões)
PRICE_AVG_LONG_DAYS      = 126    # média de preço de 6 meses (pregões)
```

- [ ] **Step 2: Verificar import**

Run: `cd /home/fabiano/Documents/Yfinance/src/backend && python3 -c "from config import rules; print(rules.W_BELOW_AVG_PER, rules.W_VOL_RISING, rules.PRICE_AVG_SHORT_DAYS, rules.PRICE_AVG_MID_DAYS, rules.PRICE_AVG_LONG_DAYS)"`
Expected: `4 8 21 63 126`

- [ ] **Step 3: Commit**

```bash
git add src/backend/config/rules.py
git commit -m "feat(swing): constantes de desconto vs. médias e volume crescente"
```

---

### Task 2: Indicadores `_below_avg_count` e `_vol_rising` (TDD)

**Files:**
- Create: `src/backend/tests/test_swing_service.py`
- Modify: `src/backend/services/swing_service.py` (após `vol_confirm`, ~linha 163; e `build_context`, ~linha 177)

- [ ] **Step 1: Escrever os testes que falham**

Criar `src/backend/tests/test_swing_service.py`:

```python
"""
Testes unitários para swing_service — fatores de assertividade da nota
(desconto vs. médias 1m/3m/6m e volume crescente).
"""

from config import rules
from services import swing_service as svc


# ---------------------------------------------------------------
# _below_avg_count
# ---------------------------------------------------------------

class TestBelowAvgCount:
    def test_preco_abaixo_das_tres_medias(self):
        # 129 fechamentos a 10.0 e o último a 9.0: abaixo de 1m, 3m e 6m
        closes = [10.0] * 129 + [9.0]
        assert svc._below_avg_count(closes) == 3

    def test_preco_acima_de_todas_as_medias(self):
        # série ascendente: último preço é o topo, acima de qualquer média
        closes = [float(i) for i in range(1, 131)]
        assert svc._below_avg_count(closes) == 0

    def test_historico_curto_ignora_media_6m(self):
        # 70 closes: médias 1m/3m existem, 6m (126) não — conta no máx. 2
        closes = [10.0] * 69 + [9.0]
        assert svc._below_avg_count(closes) == 2

    def test_abaixo_apenas_da_media_curta(self):
        # caiu recente: abaixo da média 1m, mas ainda acima das médias longas
        closes = [5.0] * 100 + [20.0] * 29 + [15.0]
        assert svc._below_avg_count(closes) == 1


# ---------------------------------------------------------------
# _vol_rising
# ---------------------------------------------------------------

class TestVolRising:
    def test_volume_crescente(self):
        volumes = [100.0] * 42 + [200.0] * 21   # média 1m=200 > média 3m≈133
        assert svc._vol_rising(volumes) is True

    def test_volume_decrescente(self):
        volumes = [200.0] * 42 + [100.0] * 21   # média 1m=100 < média 3m≈167
        assert svc._vol_rising(volumes) is False

    def test_historico_insuficiente_retorna_false(self):
        volumes = [100.0] * 30                  # < 63: média 3m indisponível
        assert svc._vol_rising(volumes) is False


# ---------------------------------------------------------------
# build_context expõe os campos novos
# ---------------------------------------------------------------

def _ohlcv(n, close=10.0, vol=100.0):
    closes = [close] * n
    highs = [close + 0.5] * n
    lows = [close - 0.5] * n
    volumes = [vol] * n
    return closes, highs, lows, volumes


class TestBuildContext:
    def test_contexto_tem_below_avgs_e_vol_rising(self):
        closes, highs, lows, volumes = _ohlcv(130)
        ctx = svc.build_context(closes, highs, lows, volumes)
        assert "below_avgs" in ctx
        assert "vol_rising" in ctx
        assert ctx["below_avgs"] == 0          # série plana: nunca estritamente abaixo
        assert ctx["vol_rising"] is False      # volume constante
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 -m pytest src/backend/tests/test_swing_service.py -v` (da raiz do repo)
Expected: FAIL — `AttributeError: module 'services.swing_service' has no attribute '_below_avg_count'`

- [ ] **Step 3: Implementar**

Em `src/backend/services/swing_service.py`, logo após a função `vol_confirm` (~linha 163), adicionar:

```python
def _below_avg_count(closes):
    """Quantas médias de preço (1m/3m/6m) disponíveis o último fechamento está abaixo."""
    price = closes[-1]
    count = 0
    periods = (rules.PRICE_AVG_SHORT_DAYS, rules.PRICE_AVG_MID_DAYS,
               rules.PRICE_AVG_LONG_DAYS)
    for period in periods:
        avg = calc_sma(closes, period)
        if avg is not None and price < avg:
            count += 1
    return count


def _vol_rising(volumes):
    """True se a média de volume 1m supera a média 3m (acumulação)."""
    short = calc_avg_volume(volumes, rules.PRICE_AVG_SHORT_DAYS)
    mid = calc_avg_volume(volumes, rules.PRICE_AVG_MID_DAYS)
    if short is None or mid is None:
        return False
    return short > mid
```

E em `build_context()` (~linha 177), adicionar duas chaves ao dict retornado, após `"vol_confirm": ...`:

```python
        "vol_confirm": vol_confirm(volumes, rules.VOL_SURGE_MULT),
        "below_avgs":  _below_avg_count(closes),
        "vol_rising":  _vol_rising(volumes),
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python3 -m pytest src/backend/tests/test_swing_service.py -v`
Expected: PASS (8 testes)

- [ ] **Step 5: Commit**

```bash
git add src/backend/services/swing_service.py src/backend/tests/test_swing_service.py
git commit -m "feat(swing): indicadores below_avgs e vol_rising no contexto"
```

---

### Task 3: Pesos novos em `grade_setup` (TDD)

**Files:**
- Modify: `src/backend/services/swing_service.py` (`grade_setup` ~linha 358; caller em `_pick_best_setup` ~linha 410)
- Test: `src/backend/tests/test_swing_service.py`

A assinatura muda de `grade_setup(setup, levels, trend)` para `grade_setup(setup, levels, ctx)` — `trend`, `below_avgs` e `vol_rising` saem do `ctx`. O único caller é `_pick_best_setup` (linha 410: `grade_setup(m, levels, ctx["trend"])` → `grade_setup(m, levels, ctx)`).

- [ ] **Step 1: Escrever os testes que falham**

Adicionar ao final de `src/backend/tests/test_swing_service.py`:

```python
# ---------------------------------------------------------------
# grade_setup — pesos de desconto e volume crescente
# ---------------------------------------------------------------

def _ctx(trend, below_avgs, vol_rising):
    return {"trend": trend, "below_avgs": below_avgs, "vol_rising": vol_rising}


def _setup(setup_type, strength=2, vol_confirm=False):
    return {"setup_type": setup_type, "strength": strength,
            "vol_confirm": vol_confirm, "trigger": "t"}


class TestGradeSetupNovosFatores:
    def test_pullback_recebe_desconto_e_volume_crescente(self):
        # 30 (ALTA) + 16 (2 gatilhos) + 10 (rr ok) + 8 (2 médias) + 8 (vol) = 72 → A
        score, grade = svc.grade_setup(
            _setup("PULLBACK"), {"rr": 1.93}, _ctx("ALTA", 2, True))
        assert score == 72
        assert grade == "A"

    def test_breakout_nao_recebe_desconto(self):
        # 30 + 16 + 15 (vol dia) + 20 (rr forte) = 81; below_avgs=3 NÃO soma
        score, grade = svc.grade_setup(
            _setup("BREAKOUT", vol_confirm=True), {"rr": 2.0}, _ctx("ALTA", 3, False))
        assert score == 81
        assert grade == "A"

    def test_breakout_recebe_volume_crescente(self):
        # 30 + 16 + 15 + 20 + 8 (vol_rising vale p/ todos) = 89
        score, grade = svc.grade_setup(
            _setup("BREAKOUT", vol_confirm=True), {"rr": 2.0}, _ctx("ALTA", 3, True))
        assert score == 89

    def test_reversao_descontada_sobe_para_b(self):
        # 12 (LATERAL) + 16 + 20 (rr forte) + 12 (3 médias) = 60 → B
        score, grade = svc.grade_setup(
            _setup("REVERSAL"), {"rr": 2.73}, _ctx("LATERAL", 3, False))
        assert score == 60
        assert grade == "B"

    def test_score_clampa_em_100(self):
        # 30 + 24 (3 gatilhos) + 15 + 20 + 12 + 8 = 109 → 100
        score, grade = svc.grade_setup(
            _setup("PULLBACK", strength=3, vol_confirm=True),
            {"rr": 2.5}, _ctx("ALTA", 3, True))
        assert score == 100
        assert grade == "A"

    def test_sem_fatores_novos_score_inalterado(self):
        # caso de hoje: ABEV3-like — 30 + 16 + 10 = 56 → B (igual ao motor atual)
        score, grade = svc.grade_setup(
            _setup("PULLBACK"), {"rr": 1.93}, _ctx("ALTA", 0, False))
        assert score == 56
        assert grade == "B"
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 -m pytest src/backend/tests/test_swing_service.py -v`
Expected: FAIL nos testes novos — `grade_setup` atual recebe `trend` (string) e quebra ao indexar `ctx` (`TypeError`/`KeyError`), ou scores divergem.

- [ ] **Step 3: Implementar**

Substituir `grade_setup` em `src/backend/services/swing_service.py` (~linha 358) por:

```python
def grade_setup(setup, levels, ctx):
    """Score composto 0–100 e nota A/B/C."""
    score = 0
    trend = ctx["trend"]
    if trend == "ALTA":
        score += rules.W_TREND_ALTA
    elif trend == "LATERAL":
        score += rules.W_TREND_LATERAL

    score += min(setup["strength"], 3) * rules.W_TRIGGER_PER

    if setup["vol_confirm"]:
        score += rules.W_VOLUME

    rr = levels["rr"] or 0
    if rr >= rules.RR_STRONG:
        score += rules.W_RR_HIGH
    elif rr >= rules.RR_MIN:
        score += rules.W_RR_OK

    # Fatores de assertividade: desconto vs. médias 1m/3m/6m (Rompimento fica de
    # fora — está acima das médias por natureza) e volume crescente (todos)
    if setup["setup_type"] != "BREAKOUT":
        score += ctx["below_avgs"] * rules.W_BELOW_AVG_PER
    if ctx["vol_rising"]:
        score += rules.W_VOL_RISING

    score = min(int(round(score)), 100)
    if score >= rules.GRADE_A:
        grade = "A"
    elif score >= rules.GRADE_B:
        grade = "B"
    else:
        grade = "C"
    return score, grade
```

E em `_pick_best_setup` (~linha 410) trocar:

```python
            score, grade = grade_setup(m, levels, ctx["trend"])
```

por:

```python
            score, grade = grade_setup(m, levels, ctx)
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python3 -m pytest src/backend/tests/test_swing_service.py -v`
Expected: PASS (14 testes)

- [ ] **Step 5: Rodar a suíte inteira do backend**

Run: `python3 -m pytest src/backend/tests/ -q`
Expected: 83 testes (69 existentes + 14 novos), todos PASS — resumo final `Status : OK`

- [ ] **Step 6: Commit**

```bash
git add src/backend/services/swing_service.py src/backend/tests/test_swing_service.py
git commit -m "feat(swing): nota pondera desconto vs. médias e volume crescente"
```

---

### Task 4: Campos `below_avgs` e `vol_rising` no schema (TDD)

**Files:**
- Modify: `src/backend/services/swing_service.py` (`analyze_ticker` ~linha 435)
- Test: `src/backend/tests/test_swing_service.py`

- [ ] **Step 1: Escrever o teste que falha**

Adicionar ao final de `src/backend/tests/test_swing_service.py`:

```python
# ---------------------------------------------------------------
# analyze_ticker — schema com os campos novos
# ---------------------------------------------------------------

class TestAnalyzeTickerSchema:
    def test_entry_contem_below_avgs_e_vol_rising(self):
        closes, highs, lows, volumes = _ohlcv(130)
        entry = svc.analyze_ticker("TEST3", closes, highs, lows, volumes)
        assert entry["below_avgs"] == 0
        assert entry["vol_rising"] is False
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 -m pytest src/backend/tests/test_swing_service.py::TestAnalyzeTickerSchema -v`
Expected: FAIL — `KeyError: 'below_avgs'`

- [ ] **Step 3: Implementar**

Em `analyze_ticker` (~linha 438), no dict `entry`, adicionar após `"vol_confirm": False,`:

```python
        "vol_confirm": False,
        "below_avgs":  ctx["below_avgs"],
        "vol_rising":  ctx["vol_rising"],
```

(O `entry.update(best)` não sobrescreve esses campos — o candidato de `_pick_best_setup` não os contém.)

- [ ] **Step 4: Rodar e ver passar**

Run: `python3 -m pytest src/backend/tests/test_swing_service.py -v`
Expected: PASS (15 testes)

- [ ] **Step 5: Commit**

```bash
git add src/backend/services/swing_service.py src/backend/tests/test_swing_service.py
git commit -m "feat(swing): below_avgs e vol_rising no schema do swing_data.json"
```

---

### Task 5: Regenerar swing_data.json

**Files:**
- Modify: `src/backend/data/swing_data.json` (gerado)

- [ ] **Step 1: Rodar o motor** (busca yfinance p/ ~127 tickers, 1–3 min)

Run: `cd /home/fabiano/Documents/Yfinance/src/backend && python3 -c "from services.swing_service import run; run()"`
Expected: termina sem traceback.

- [ ] **Step 2: Conferir os campos novos e o efeito na nota**

Run (da raiz do repo):

```bash
python3 - <<'EOF'
import json
d = json.load(open('src/backend/data/swing_data.json'))
assert all('below_avgs' in x and 'vol_rising' in x for x in d), 'campos faltando'
for x in d:
    if x.get('is_setup'):
        print(x['ticker'], x['setup_type'], x['grade'], 'score', x['score'],
              'below', x['below_avgs'], 'vol_rising', x['vol_rising'])
EOF
```

Expected: nenhum assert; setups listados com os campos novos; scores de Pullback/Reversão ≥ aos da execução anterior quando `below_avgs > 0` ou `vol_rising`.

- [ ] **Step 3: Commit**

```bash
git add src/backend/data/swing_data.json
git commit -m "chore(swing): regenera swing_data.json com fatores de desconto/volume"
```

---

### Task 6: Documentação (brain_calculations.md)

**Files:**
- Modify: `src/brain/brain_calculations.md` — §7.12.1 (~linha 425), §7.12.5 (~linha 528), §7.12.7 (~linha 566), tabela de limiares (~linha 930)

- [ ] **Step 1: §7.12.1 — tabela de indicadores base**

Adicionar duas linhas à tabela (após a linha do `vol_confirm`):

```markdown
| Desconto vs. médias (`below_avgs`) | `_below_avg_count` | preço < SMA de 21/63/126 pregões (conta 0–3; média indisponível não conta) |
| Volume crescente (`vol_rising`) | `_vol_rising` | média vol(21) > média vol(63) |
```

- [ ] **Step 2: §7.12.5 — nota A/B/C**

Na tabela de fatores, adicionar:

```markdown
| Desconto: por média (1m/3m/6m) abaixo — só PULLBACK/REVERSAL | `W_BELOW_AVG_PER` | 4 cada (máx. 12) |
| Volume crescente (méd. 1m > méd. 3m) — todos os setups | `W_VOL_RISING` | 8 |
```

E atualizar a fórmula para:

```python
score = (trend_points) + (min(strength, 3) × W_TRIGGER_PER)
      + (W_VOLUME se vol_confirm) + (W_RR_HIGH ou W_RR_OK)
      + (below_avgs × W_BELOW_AVG_PER se setup != BREAKOUT)
      + (W_VOL_RISING se vol_rising)
score = clamp(score, 0, 100)
```

Anotar que a assinatura é `grade_setup(setup, levels, ctx)`.

- [ ] **Step 3: §7.12.7 — schema**

No JSON de exemplo, adicionar `"below_avgs": 2,` e `"vol_rising": true,` (antes de `"updated_at"`), e na tabela de campos:

```markdown
| `below_avgs` | int | Quantas médias de preço (21/63/126 pregões) o fechamento está abaixo (0–3) |
| `vol_rising` | bool | Média de volume 21p > média 63p (acumulação) |
```

- [ ] **Step 4: Tabela "Swing Trade — Setups, Risco e Nota" (~linha 930)**

Na seção **Volume**, adicionar:

```markdown
| Janela curta preço/volume (1m) | 21 pregões | `PRICE_AVG_SHORT_DAYS = 21` |
| Janela média preço/volume (3m) | 63 pregões | `PRICE_AVG_MID_DAYS = 63` |
| Janela longa preço (6m) | 126 pregões | `PRICE_AVG_LONG_DAYS = 126` |
```

Na seção **Nota A/B/C**, adicionar:

```markdown
| Peso por média de preço abaixo (não-BREAKOUT) | 4 (máx. 12) | `W_BELOW_AVG_PER = 4` |
| Peso volume crescente | 8 | `W_VOL_RISING = 8` |
```

- [ ] **Step 5: Commit**

```bash
git add src/brain/brain_calculations.md
git commit -m "docs(brain): fatores de desconto e volume crescente na nota swing"
```

---

## Self-review (feito na escrita)

- **Cobertura da spec:** §1→Task 2, §2→Task 1, §3→Task 3, §4→Task 4, testes→Tasks 2-4, regen→Task 5, docs→Task 6. Fora de escopo respeitado (detectores/níveis/frontend intocados).
- **Consistência de tipos:** `grade_setup(setup, levels, ctx)` usado igual nas Tasks 3 e no caller; `below_avgs`/`vol_rising` mesmos nomes em ctx, schema e testes.
- **Python 3.8:** sem walrus, sem f-strings complexas no código novo.
