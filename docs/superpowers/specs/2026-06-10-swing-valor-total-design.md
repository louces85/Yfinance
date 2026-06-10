# Swing — Valor atual por posição e valor total em Minhas Operações

**Data:** 2026-06-10
**Objetivo:** o usuário precisa saber quanto valem as posições abertas (cada uma e o
total) para decidir uma venda. Decisão do usuário: **coluna por posição + total no chip
da toolbar** (sem impacto DARF no tooltip, sem mudança no Histórico).

## Contexto

`GET /api/swing/positions` já entrega `qty` e `current_price` por posição aberta —
valor atual = `qty × current_price`, calculado no frontend. Mudança 100% em
`src/frontend/index.html`; o chip `#swOpenCount` já mostra "N abertas · Saldo: ±R$ X"
(feature anterior, mesma sessão).

## Mudanças

1. **Coluna "Valor atual (R$)"** na tabela `#swOpenTable`, entre "Preço atual" e
   "P&L (R$)": `qty × current_price` via `_swMoney`; "—" quando `qty` ou
   `current_price` for `null`. `colspan` da linha vazia: 11 → 12.
2. **Helper `_swValorTotal(rows)`** — soma `qty × current_price` das posições com
   ambos não-`null`; retorna `null` se nenhuma qualifica.
3. **Chip `#swOpenCount`** vira `"N abertas · Valor: R$ X · Saldo: ±R$ Y"` — valor em
   cor neutra (não é ganho/perda; `_swMoney`), saldo colorido como hoje
   (`_swPnlHtml`). Sem valor calculável, o trecho "Valor:" é omitido.
4. **Doc:** §9.5.1 do `src/brain/brain_frontend.md` — colunas da tabela e chip.

## Fora do escopo

Histórico, backend, card de DARF, valor investido (`qty × entry_price`).

## Versionamento

Working tree limpo (WIP do diário foi commitado em d02e23a) — commits normais.
