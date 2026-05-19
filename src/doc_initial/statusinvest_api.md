# StatusInvest — API Não-Oficial de Dados Fundamentalistas

> Documentado em: 2026-03-20
> Testado com: QUAL3, PETR4
> Status: **Funcionando sem autenticação** (apenas headers mínimos obrigatórios)

---

## Visão Geral

O StatusInvest expõe endpoints JSON internos usados pelo próprio site para renderizar as tabelas de dados financeiros históricos. Esses endpoints retornam dados anuais de:

- **Balanço Patrimonial** (`getativos`) — Ativo, Passivo, Patrimônio Líquido
- **DRE / Resultados** (`getdre`) — Receita, EBITDA, Lucro Líquido, Margens, ROE, ROIC, Dívida

A cobertura histórica varia por ticker, mas é comum ter dados desde 2008–2010 até o ano corrente.

---

## Endpoints

### 1. Balanço Patrimonial — `getativos`

```
GET https://statusinvest.com.br/acao/getativos
```

**Query params:**

| Parâmetro    | Tipo    | Descrição                              | Exemplo  |
|--------------|---------|----------------------------------------|----------|
| `code`       | string  | Ticker da ação (minúsculo)             | `qual3`  |
| `type`       | int     | Sempre `0` (outros valores retornam mesmo dado) | `0` |
| `futureData` | bool    | Sempre `false`                         | `false`  |
| `range.min`  | int     | Ano inicial do filtro                  | `2020`   |
| `range.max`  | int     | Ano final do filtro                    | `2025`   |

> **Nota:** `range.min`/`range.max` filtram as colunas retornadas, mas o array `years` na resposta sempre lista **todos** os anos disponíveis no banco. Os dados reais ficam nas colunas conforme o range.

**Indicadores retornados:**
```
Ativo Total
  └─ Ativo Circulante
       ├─ Aplicações Financeiras
       ├─ Caixa e Equivalentes de Caixa
       ├─ Contas a Receber
       └─ Estoque
  └─ Ativo Não Circulante
       ├─ Ativo Realizável a Longo Prazo
       ├─ Investimentos
       ├─ Imobilizado
       └─ Intangível
Passivo Total
  ├─ Passivo Circulante
  ├─ Passivo Não Circulante
  └─ Patrimônio Líquido Consolidado
       ├─ Capital Social Realizado
       ├─ Reserva Capital
       ├─ Reserva Lucros
       └─ Participação dos Não Controladores
```

**Exemplo de requisição (curl):**
```bash
curl 'https://statusinvest.com.br/acao/getativos?code=petr4&type=0&futureData=false&range.min=2020&range.max=2025' \
  -H 'accept: */*' \
  -H 'referer: https://statusinvest.com.br/acoes/petr4' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
```

---

### 2. DRE + Indicadores — `getdre`

```
GET https://statusinvest.com.br/acao/getdre
```

Mesmos parâmetros do `getativos`. Troca apenas o path.

**Indicadores retornados:**
```
Receita Líquida - (R$)
Custos - (R$)
Lucro Bruto - (R$)
Despesas/Receitas Operacionais - (R$)
EBITDA - (R$)                      ← pode estar vazio ("-") dependendo do ticker
Amortização/Depreciação
EBIT - (R$)
Resultado não operacional - (R$)
Resultado Financeiro - (R$)
Impostos - (R$)
Lucro Líquido - (R$)
Lucro atribuído a Controladora
Lucro atribuído a Não Controladores
CAPEX - (R$)
Dívida Bruta - (R$)
Dívida Líquida - (R$)
ROE - (%)
ROIC - (%)
Margem Bruta - (%)
Margem Ebitda - (%)
Margem Líquida - (%)
Dívida Líquida/Ebitda
```

**Exemplo de requisição:**
```bash
curl 'https://statusinvest.com.br/acao/getdre?code=petr4&type=0&futureData=false&range.min=2020&range.max=2025' \
  -H 'accept: */*' \
  -H 'referer: https://statusinvest.com.br/acoes/petr4' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
```

---

## Estrutura da Resposta JSON

```json
{
  "success": true,
  "data": {
    "years": [2010, 2011, 2012, ..., 2025],
    "grid": [
      {
        "isHeader": true,
        "row": 0,
        "spaces": 0,
        "columns": [
          { "value": "#" },
          { "name": "DATA", "title": "Data de referência", "value": "2025" },
          { "name": "AH",   "title": "Análise horizontal", "value": "AH", "symbol": "%" },
          { "name": "AV",   "title": "Análise vertical",   "value": "AV", "symbol": "%" },
          { "name": "DATA", "value": "2024" },
          ...
        ]
      },
      {
        "isHeader": false,
        "row": 1,
        "spaces": 0,
        "columns": [
          { "value": "Ativo Total - (R$)" },
          { "name": "DATA", "value": "3.938,54 M" },
          { "name": "AH",   "value": "-9,80", "symbol": "%" },
          { "name": "AV",   "value": "100,00", "symbol": "%" },
          { "name": "DATA", "value": "4.366,33 M" },
          ...
        ]
      }
    ]
  }
}
```

### Campos do grid

| Campo      | Descrição |
|------------|-----------|
| `isHeader` | `true` na linha de cabeçalho (anos), `false` nas linhas de dados |
| `row`      | Índice da linha (0 = header) |
| `spaces`   | Nível de indentação hierárquica (0 = raiz, 1 = filho, 2 = neto) |
| `columns[0].value` | Nome do indicador |
| `columns[1+i*3].value` | Valor do ano `i` (coluna DATA) |
| `columns[2+i*3].value` | Variação YoY do ano `i` (coluna AH, em %) |
| `columns[3+i*3].value` | Análise vertical do ano `i` (coluna AV, em %) |

> **Atenção:** O índice `i` começa em 0 para o **primeiro ano do range solicitado**, não para o primeiro ano do array `years`.
> Para extrair valores com segurança, **use o header row para mapear coluna → ano** em vez de calcular offsets fixos.

---

## Parser Python

### Converter valores para float

Os valores vêm em formato BR com sufixo de magnitude:

```python
def parse_statusinvest_value(val_str: str) -> float | None:
    """
    Converte string do StatusInvest para float.
    Exemplos: "3.938,54 M" -> 3938540000.0
              "-9,80"      -> -9.8
              "-"          -> None
    """
    if not val_str or val_str.strip() in ['-', '', 'N/A']:
        return None

    multipliers = {' B': 1_000_000_000, ' M': 1_000_000, ' K': 1_000}
    s = val_str.strip()
    multiplier = 1

    for suffix, mult in multipliers.items():
        if s.endswith(suffix):
            multiplier = mult
            s = s[:-len(suffix)]
            break

    # Formato BR: ponto = milhar, vírgula = decimal
    s = s.replace('.', '').replace(',', '.')
    try:
        return float(s) * multiplier
    except ValueError:
        return None
```

### Extrair série histórica completa

```python
import requests

def fetch_statusinvest(ticker: str, endpoint: str = 'getdre',
                        year_min: int = 2010, year_max: int = 2025) -> dict:
    """
    Retorna dict: { nome_indicador: { ano: valor_float, ... }, ... }
    endpoint: 'getativos' ou 'getdre'
    """
    url = f'https://statusinvest.com.br/acao/{endpoint}'
    params = {
        'code': ticker.lower(),
        'type': 0,
        'futureData': 'false',
        'range.min': year_min,
        'range.max': year_max,
    }
    headers = {
        'accept': '*/*',
        'referer': f'https://statusinvest.com.br/acoes/{ticker.lower()}',
        'user-agent': (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
        ),
    }

    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    if not payload.get('success'):
        return {}

    grid  = payload['data']['grid']

    # Mapear coluna -> ano a partir do header
    header = next((r for r in grid if r.get('isHeader')), None)
    if not header:
        return {}

    year_col_map = {}  # ano -> col_index dentro de columns
    for idx, col in enumerate(header['columns']):
        if col.get('name') == 'DATA' and col.get('value', '').isdigit():
            year_col_map[int(col['value'])] = idx

    # Extrair dados
    result = {}
    for item in grid:
        if item.get('isHeader'):
            continue
        cols = item.get('columns', [])
        if not cols:
            continue
        indicator_name = cols[0].get('value', '').strip()
        if not indicator_name:
            continue

        result[indicator_name] = {}
        for year, col_idx in year_col_map.items():
            if col_idx < len(cols):
                raw = cols[col_idx].get('value', '')
                result[indicator_name][year] = parse_statusinvest_value(raw)

    return result


# Uso:
# dre   = fetch_statusinvest('PETR4', 'getdre',    2015, 2025)
# balan = fetch_statusinvest('PETR4', 'getativos', 2015, 2025)
# receita_2024 = dre.get('Receita Líquida - (R$)', {}).get(2024)
```

---

## Headers Obrigatórios

| Header       | Obrigatório? | Notar |
|--------------|-------------|-------|
| `user-agent` | **Sim**     | Sem UA o Cloudflare bloqueia |
| `referer`    | Recomendado | Usar `https://statusinvest.com.br/acoes/{ticker}` |
| `accept`     | Opcional    | `*/*` funciona |
| Cookies      | **Não**     | Testado sem nenhum cookie — retorna 200 com JSON válido |

> Confirmado em 2026-03-20: **não é necessário `cf_clearance` nem nenhum outro cookie** para os endpoints `getativos` e `getdre`. Apenas `user-agent` e `referer` são suficientes.

---

## Limitações e Riscos

| Item | Detalhe |
|------|---------|
| **API não-oficial** | Pode mudar ou ser bloqueada sem aviso |
| **Frequência** | Sem limite documentado; usar com `time.sleep(1~2s)` entre chamadas em batch |
| **Dados anuais** | Não há granularidade trimestral nesses endpoints |
| **Valores ausentes** | Alguns indicadores retornam `"-"` para certos anos/tickers (ex: EBITDA de QUAL3 pós-2017) |
| **Unidade dos valores** | Varia: alguns tickers reportam em milhões (`M`), outros em valor absoluto sem sufixo |
| **Dados duplicados** | O primeiro ano do array `years` às vezes repete o segundo (bug conhecido do StatusInvest) |

---

## Comparação com yfinance

| Critério | StatusInvest | yfinance |
|----------|-------------|---------|
| Cobertura histórica (BR) | 2008–atual | Inconsistente por ticker |
| Balanço Patrimonial | ✅ Completo | ✅ Mas às vezes incompleto para BR |
| DRE + Margens | ✅ Completo | ✅ |
| ROE, ROIC, Dívida/EBITDA | ✅ Pré-calculados | ❌ Calcular manualmente |
| Dados trimestrais | ❌ | ✅ |
| Preço histórico | ❌ | ✅ |
| FCO / Fluxo de Caixa | ❌ (sem endpoint funcional) | ✅ |
| Automação sem cookies | ✅ | ✅ |

**Uso recomendado:** fallback/complemento ao yfinance para dados fundamentalistas anuais históricos de ações brasileiras, especialmente quando yfinance retornar vazio ou incompleto.
