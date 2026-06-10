# Swing: Coluna Valor Atual + Total no Chip — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Coluna "Valor atual (R$)" (`qty × preço atual`) na tabela de Minhas Operações e o valor total no chip da toolbar, para apoiar decisão de venda.

**Architecture:** Mudança 100% frontend em `src/frontend/index.html`: helper `_swValorTotal(rows)` ao lado de `_swSaldoTotal` (linha ~4158), célula nova em `renderSwOpen()` e `<th>` novo no HTML da tabela. Formatação por `_swMoney` (valor neutro, sem cor de P&L). Spec: `docs/superpowers/specs/2026-06-10-swing-valor-total-design.md`.

**Tech Stack:** JS vanilla embutido no `index.html`. Sem testes JS no projeto — verificação por `node --check` + visual. Working tree limpo: commits normais.

---

## File Map

| Arquivo | Ação |
|---------|------|
| `src/frontend/index.html` | Modificar — `<th>` (~linha 1332), linha vazia colspan (~4205), helper (~4158), `renderSwOpen` (chip ~4196 e células ~4224) |
| `src/brain/brain_frontend.md` | Modificar — §9.5.1 (colunas + chip) |

---

### Task 1: Coluna + helper + chip

**Files:**
- Modify: `src/frontend/index.html`

- [ ] **Step 1: `<th>` da coluna nova**

No `<thead>` de `#swOpenTable` (~linha 1332), trocar:

```html
            <th>Preço atual</th>
            <th>P&amp;L (R$)</th>
```

por:

```html
            <th>Preço atual</th>
            <th>Valor atual (R$)</th>
            <th>P&amp;L (R$)</th>
```

- [ ] **Step 2: colspan da linha vazia 11 → 12**

Em `renderSwOpen()` (~linha 4205), trocar:

```javascript
    tb.innerHTML = '<tr><td colspan="11" class="sw-empty">Nenhuma operação aberta. Clique em “+ Adicionar operação” ou em “Comprei” num sinal.</td></tr>';
```

por:

```javascript
    tb.innerHTML = '<tr><td colspan="12" class="sw-empty">Nenhuma operação aberta. Clique em “+ Adicionar operação” ou em “Comprei” num sinal.</td></tr>';
```

- [ ] **Step 3: helper `_swValorTotal`**

Logo após `_swSaldoTotal` (~linha 4164), adicionar:

```javascript
function _swValorTotal(rows) {
  var sum = 0, has = false;
  rows.forEach(function(p) {
    if (p.qty != null && p.current_price != null) { sum += p.qty * p.current_price; has = true; }
  });
  return has ? sum : null;
}
```

- [ ] **Step 4: valor total no chip**

Em `renderSwOpen()` (~linha 4196), trocar:

```javascript
  var openLabel = rows.length + ' aberta' + (rows.length === 1 ? '' : 's');
  var openSaldo = _swSaldoTotal(rows, 'unrealized_pl');
```

por:

```javascript
  var openLabel = rows.length + ' aberta' + (rows.length === 1 ? '' : 's');
  var openValor = _swValorTotal(rows);
  if (rows.length && openValor != null) openLabel += ' · Valor: ' + _swMoney(openValor);
  var openSaldo = _swSaldoTotal(rows, 'unrealized_pl');
```

- [ ] **Step 5: célula da coluna nova**

No `rows.map` de `renderSwOpen()` (~linha 4224), trocar:

```javascript
      '<td>' + _swFmt(p.current_price) + '</td>' +
      '<td>' + _swPnlHtml(p.unrealized_pl) + '</td>' +
```

por:

```javascript
      '<td>' + _swFmt(p.current_price) + '</td>' +
      '<td>' + (p.qty != null && p.current_price != null ? _swMoney(p.qty * p.current_price) : '—') + '</td>' +
      '<td>' + _swPnlHtml(p.unrealized_pl) + '</td>' +
```

---

### Task 2: Verificação, doc e commit

**Files:**
- Modify: `src/brain/brain_frontend.md` (§9.5.1)

- [ ] **Step 1: Sanity check do JS**

```bash
python3 - <<'EOF'
import re, subprocess, tempfile
html = open('src/frontend/index.html', encoding='utf-8').read()
js = '\n'.join(re.findall(r'<script>(.*?)</script>', html, re.S))
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
    f.write(js); path = f.name
print(subprocess.run(['node', '--check', path], capture_output=True, text=True).stderr or 'sintaxe OK')
EOF
```

Expected: `sintaxe OK`

- [ ] **Step 2: Verificação visual**

App rodando: F5 → Swing → Minhas Operações. Conferir coluna "Valor atual (R$)" entre Preço atual e P&L, e chip "N abertas · Valor: R$ X · Saldo: ±R$ Y".

- [ ] **Step 3: Atualizar §9.5.1**

Em `src/brain/brain_frontend.md`, trocar:

```markdown
**Tabela Minhas Operações (`#swOpenTbody`):** Ativo · Qtd · Entrada · Preço atual · P&L (R$) · P&L % · Stop · Alvo · Compra (data) · Dias · ações (Vender / ✎ Editar / ✕ Excluir). Distância % do stop/alvo nos `title` das células Stop/Alvo. P&L verde/vermelho.
```

por:

```markdown
**Tabela Minhas Operações (`#swOpenTbody`):** Ativo · Qtd · Entrada · Preço atual · Valor atual (R$) (`qty × current_price`, "—" sem preço) · P&L (R$) · P&L % · Stop · Alvo · Compra (data) · Dias · ações (Vender / ✎ Editar / ✕ Excluir). Distância % do stop/alvo nos `title` das células Stop/Alvo. P&L verde/vermelho.
```

E no parágrafo **Saldo total (toolbar)**, trocar:

```markdown
**Saldo total (toolbar):** `#swOpenCount` exibe `"N abertas · Saldo: ±R$ X"` (soma de
```

por:

```markdown
**Saldo total (toolbar):** `#swOpenCount` exibe `"N abertas · Valor: R$ V · Saldo: ±R$ X"` (`Valor` = soma de `qty × current_price` via `_swValorTotal`, neutro; saldo = soma de
```

- [ ] **Step 4: Commit**

```bash
git add src/frontend/index.html src/brain/brain_frontend.md
git commit -m "feat(swing): coluna Valor atual e total no chip de Minhas Operações"
```

---

## Self-review (feito na escrita)

- **Cobertura da spec:** mudança 1→Task 1 Steps 1/2/5, mudança 2→Step 3, mudança 3→Step 4, mudança 4→Task 2 Step 3, commits normais→Task 2 Step 4.
- **Consistência:** `_swValorTotal(rows)` mesmo nome nas Tasks 1 e 2; campos `qty`/`current_price` conferidos na resposta real da API.
- **Sem placeholders.**
