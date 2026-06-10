# Swing: Saldo Total nas Sub-abas Operações/Histórico — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chip de saldo total (P&L não realizado / resultado realizado) na toolbar das sub-abas "Minhas Operações" e "Histórico" da aba Swing.

**Architecture:** Mudança 100% frontend em `src/frontend/index.html` (JS vanilla). Um helper `_swSaldoTotal()` soma o campo de P&L ignorando `null`; `renderSwOpen()` concatena o saldo no contador existente `#swOpenCount`; a seção Histórico ganha toolbar com `#swHistCount`. Formatação reusa `_swPnlHtml()` (linha ~4146). Spec: `docs/superpowers/specs/2026-06-10-swing-saldo-total-design.md`.

**Tech Stack:** JS vanilla embutido no `index.html` (~4900 linhas). Sem framework, sem testes JS no projeto — verificação manual via app.

**⚠️ Versionamento:** o diário de swing no `index.html` e o §9.5.1 do `brain_frontend.md` são WIP **não commitado** do usuário (não existem em HEAD). **NÃO commitar** esses dois arquivos — as edições ficam no working tree e serão commitadas pelo usuário junto com o diário. Por isso este plano não tem steps de commit de código.

---

## File Map

| Arquivo | Ação |
|---------|------|
| `src/frontend/index.html` | Modificar — helper (~linha 4157), `renderSwOpen` (~4194), `renderSwHist` (~4237), HTML do Histórico (~1348) |
| `src/brain/brain_frontend.md` | Modificar — §9.5.1 |

---

### Task 1: Helper `_swSaldoTotal` + saldo em Minhas Operações

**Files:**
- Modify: `src/frontend/index.html` (helpers ~linha 4157; `renderSwOpen` ~linha 4194)

- [ ] **Step 1: Adicionar o helper**

Logo após `_swPctHtml` (~linha 4157), antes de `_swDateBr`:

```javascript
function _swSaldoTotal(rows, field) {
  var sum = 0, has = false;
  rows.forEach(function(p) {
    if (p[field] != null) { sum += p[field]; has = true; }
  });
  return has ? sum : null;
}
```

- [ ] **Step 2: Concatenar o saldo no contador de Operações**

Em `renderSwOpen()` (~linha 4196), trocar:

```javascript
  document.getElementById('swOpenCount').textContent = rows.length + ' aberta' + (rows.length === 1 ? '' : 's');
```

por:

```javascript
  var openLabel = rows.length + ' aberta' + (rows.length === 1 ? '' : 's');
  var openSaldo = _swSaldoTotal(rows, 'unrealized_pl');
  if (rows.length && openSaldo != null) openLabel += ' · Saldo: ' + _swPnlHtml(openSaldo);
  document.getElementById('swOpenCount').innerHTML = openLabel;
```

(Lista vazia ou sem preço atual em nenhuma posição: chip mostra só "N abertas".)

---

### Task 2: Toolbar + saldo no Histórico

**Files:**
- Modify: `src/frontend/index.html` (HTML ~linha 1348; `renderSwHist` ~linha 4237)

- [ ] **Step 1: Adicionar toolbar à seção Histórico**

Trocar (~linha 1348):

```html
  <!-- ─── Histórico (vendidas) ─── -->
  <div id="swHistoricoSection" style="display:none">
    <div class="table-wrap">
```

por:

```html
  <!-- ─── Histórico (vendidas) ─── -->
  <div id="swHistoricoSection" style="display:none">
    <div class="swing-toolbar">
      <span class="swing-updated" id="swHistCount"></span>
    </div>
    <div class="table-wrap">
```

- [ ] **Step 2: Preencher contador + saldo em `renderSwHist`**

Em `renderSwHist()` (~linha 4237), logo após `var rows = (_swingPositions.closed || []).slice();`:

```javascript
  var histLabel = 'Nenhuma venda';
  if (rows.length) {
    histLabel = rows.length + ' venda' + (rows.length === 1 ? '' : 's');
    var histSaldo = _swSaldoTotal(rows, 'realized_pl');
    if (histSaldo != null) histLabel += ' · Saldo: ' + _swPnlHtml(histSaldo);
  }
  document.getElementById('swHistCount').innerHTML = histLabel;
```

(Soma todas as vendas, todo o período — o recorte mensal já existe no card de DARF.)

---

### Task 3: Verificação manual + doc

**Files:**
- Modify: `src/brain/brain_frontend.md` (§9.5.1)

- [ ] **Step 1: Sanity check do JS**

Run: extrair os blocos `<script>` e validar sintaxe, por exemplo:

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

Subir o app (`python3 src/backend/api_server.py` ou instância já rodando), abrir a aba Swing → "Minhas Operações" e "Histórico" e conferir: chip "N abertas · Saldo: ±R$ X" (verde/vermelho) e "N vendas · Saldo: ±R$ X"; com diário vazio, apenas "0 abertas"/"Nenhuma venda".

- [ ] **Step 3: Atualizar §9.5.1 do brain_frontend.md**

Na descrição das tabelas (§9.5.1), após o parágrafo da **Tabela Minhas Operações**, registrar o chip; SEM commitar (arquivo é WIP do usuário). Adicionar:

```markdown
**Saldo total (toolbar):** `#swOpenCount` exibe `"N abertas · Saldo: ±R$ X"` (soma de
`unrealized_pl`, ignora posições sem preço atual) e o Histórico tem toolbar própria com
`#swHistCount`: `"N vendas · Saldo: ±R$ X"` (soma de `realized_pl`, todo o período).
Valor formatado por `_swPnlHtml` (verde/vermelho); helper `_swSaldoTotal(rows, field)`
retorna `null` quando nenhuma linha tem o campo (chip omite o saldo).
```

---

## Self-review (feito na escrita)

- **Cobertura da spec:** mudança 1→Task 1 Step 1, mudança 2→Task 1 Step 2, mudança 3→Task 2, mudança 4→Task 3 Step 3, restrição de versionamento→header e ausência de commits.
- **Consistência:** `_swSaldoTotal(rows, field)` mesmo nome/assinatura nas Tasks 1, 2 e 3; ids `#swOpenCount`/`#swHistCount` consistentes entre HTML e JS.
- **Sem placeholders:** todo step tem código/comando completo.
