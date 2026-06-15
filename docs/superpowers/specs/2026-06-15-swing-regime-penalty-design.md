# Swing — Penalidade de regime de mercado na nota (filtro de amplitude)

**Data:** 2026-06-15
**Objetivo:** quando o mercado amplo está fraco, rebaixar a nota dos setups de
contra-tendência (REVERSAL fora de ALTA) para que faca-caindo não apareça com nota
alta nem lidere a lista. Decisão do usuário: **rebaixar a nota** (não suprimir o
sinal) — o setup continua na lista (`is_setup=True`), só com score penalizado e
marcado.

## Contexto

Investigação de 2026-06-15: a feature recomendou UGPA3/CLSC4 (REVERSAL, papel LATERAL)
em 10/jun e elas derreteram (UGPA3 stopou −3,4%). O IBOV estava LATERAL e subiu +1,1%
no período — ou seja, **um filtro por índice não pegaria**. A fraqueza estava na
amplitude interna: 71 de 127 ativos (56%) em BAIXA. As opções já entregues nesta
frente:
- **Opção 2 (feita):** bônus `below_avgs` só pontua em ALTA. Corrigiu o ranking, mas
  UGPA3 **continua qualificando** como setup (R:R 2,58; nota 56 ≥ 50 → B).
- **Opção 3 (feita):** quase-setups reprovados aparecem com `reject_reason`.

Esta entrega (opção 1) é a camada que faltava: agir sobre o **regime** de mercado.

## Mudanças

### 1. `rules.py` — constantes novas (nunca hardcode)

| Constante | Valor | Significado |
|-----------|-------|-------------|
| `REGIME_WEAK_BAIXA_RATIO` | 0.50 | fração de ativos em BAIXA a partir da qual o mercado é "fraco" |
| `W_REGIME_PENALTY` | 20 | pontos subtraídos do score de REVERSAL contra-tendência em regime fraco |

### 2. `swing_service.py` — helper de nota extraído

`_grade_from_score(score)` → `"A"`/`"B"`/`"C"` pelos cortes `GRADE_A`/`GRADE_B`.
Usado por `grade_setup` (refatorado para chamá-lo) e pelo pós-passe de regime, para a
regra de corte viver num lugar só.

### 3. `swing_service.py` — `_apply_regime_penalty(entry, baixa_ratio)` (puro, testável)

Aplica a penalidade a uma entrada já montada. Não faz nada e retorna a entrada
inalterada, exceto quando **todas** as condições valem:
- `entry["is_setup"]` é `True`;
- `entry["setup_type"] == "REVERSAL"` (único setup de contra-tendência — PULLBACK exige
  ALTA e BREAKOUT exige preço > MA50, ambos a-favor-da-tendência, ficam de fora);
- `entry["trend"] != "ALTA"` (REVERSAL num papel em ALTA é repique de ação forte — não
  penaliza);
- `baixa_ratio >= REGIME_WEAK_BAIXA_RATIO`.

Efeito: `score = max(0, score − W_REGIME_PENALTY)`, `grade = _grade_from_score(score)`,
`regime_weak = True`.

### 4. `swing_service.py` — pós-passe em `run()`

Depois de montar os ~126 resultados (e **antes** da ordenação), calcula
`baixa_ratio = nº trend=="BAIXA" / total` e aplica `_apply_regime_penalty` a cada
resultado. A amplitude é global; o pós-passe evita refazer o download de dados. A
ordenação final (`is_setup`, `score`, `rr`) passa a refletir o score penalizado.

### 5. Schema `swing_data.json` — campo novo

`regime_weak` (bool) em **toda** entrada (default `False`), como `is_setup`/`vol_rising`.
`True` apenas nos REVERSAL penalizados.

### 6. Frontend (`index.html`, `renderSwingTable`)

Quando `d.is_setup && d.regime_weak`, anexa à coluna **Gatilho** um marcador amarelo
"⚠ regime fraco", para explicar por que a nota caiu (mesmo padrão da opção 3). Sem
coluna nova.

### 7. Fora do escopo (intocados)

Detectores, `calc_levels`/níveis de risco, `RR_MIN`, piso de volatilidade, gate de
qualificação (`_setup_reject_reason`), bônus `below_avgs` (opção 2), diário de operações.
`is_setup` **não** muda — o sinal não é suprimido, só rebaixado.

## Testes (TDD)

- `_grade_from_score`: cortes 70→A, 69→B, 50→B, 49→C.
- `_apply_regime_penalty`:
  - REVERSAL + LATERAL + regime fraco → score −20, grade recalculada, `regime_weak=True`;
  - REVERSAL + ALTA + regime fraco → inalterado (ALTA isenta);
  - PULLBACK + regime fraco → inalterado (não é contra-tendência);
  - REVERSAL + LATERAL + regime saudável (ratio < limiar) → inalterado;
  - não-setup → inalterado.
- `analyze_ticker`: schema contém `regime_weak` (default `False`).

## Documentação

Atualizar `src/brain/brain_calculations.md` §7.12 (nota A/B/C, `_pick_best_setup`/run,
schema, tabela de limiares) e `src/brain/brain_frontend.md` §9.5 (coluna Gatilho).

## Efeito esperado (dados de 2026-06-10, já com opção 2)

baixa_ratio = 56% ≥ 50% → regime fraco. UGPA3/CLSC4 (REVERSAL LATERAL, 56) → 36 → **C**,
caem para o fundo da lista e ganham "⚠ regime fraco". GOAU3/ABEV3 (PULLBACK ALTA) e
qualquer REVERSAL em ALTA: inalterados. Nenhum sinal some.

## Restrições técnicas

- Python 3.8 (sem walrus, sem f-string complexa).
- Persistência sempre via `stock_repository.py` (`save_swing_data`).
- Limiares só em `config/rules.py`.
