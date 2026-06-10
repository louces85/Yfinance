# Swing — Saldo total nas sub-abas Minhas Operações e Histórico

**Data:** 2026-06-10
**Objetivo:** exibir o saldo total (positivo/negativo) das operações de swing: P&L não
realizado somado em "Minhas Operações" e resultado realizado somado em "Histórico".
Decisão do usuário: **chip na toolbar** (não linha de total na tabela).

## Contexto

As posições chegam prontas de `GET /api/swing/positions` (`swing_journal_service`):
abertas com `unrealized_pl` (P&L ao vivo, `null` quando não há preço atual) e vendidas
com `realized_pl`. Mudança 100% frontend em `src/frontend/index.html`
(`renderSwOpen()` / `renderSwHist()`); helpers de formatação `_swPnlHtml`/`_swMoney`
já existem.

## Mudanças

1. **Helper `_swSaldoTotal(rows, field)`** — soma o campo ignorando `null`; retorna
   `null` se nenhuma linha tem o campo (sem dado ≠ saldo zero).
2. **Minhas Operações** — o contador `#swOpenCount` (toolbar existente) passa de
   `textContent` para `innerHTML`: `"2 abertas · Saldo: +R$ 43,00"`, valor via
   `_swPnlHtml` (verde > 0, vermelho < 0, cinza 0). Lista vazia: só `"0 abertas"`.
3. **Histórico** — ganha toolbar no padrão `.swing-toolbar` com span `#swHistCount`:
   `"N vendas · Saldo: +R$ X"` somando `realized_pl` de **todas** as vendas (recorte
   mensal já existe no card de DARF). Lista vazia: `"Nenhuma venda"`.
4. **Doc** — uma linha no §9.5.1 de `src/brain/brain_frontend.md`.

## Fora do escopo

Backend, card de DARF, linha de total na tabela, saldo percentual.

## Restrição de versionamento

O diário de swing no `index.html`/`brain_frontend.md` ainda é WIP **não commitado** do
usuário (não existe em HEAD). As edições desta feature ficam no working tree, sem
commit, para não arrastar o WIP — serão commitadas junto com o diário pelo usuário.
