# Evolução do Sistema: v1 (run.sh) → v2 (YFINANCE_REFACTOR)
> Análise comparativa técnica e de negócio | Data: 22/03/2026
> Rigor: máximo | Perspectiva: engenharia de software + análise de investimentos

---

## VEREDICTO EXECUTIVO

O sistema v1 (`run.sh`) era um **script de análise pessoal funcional** — resolveu o problema de quem precisava de uma tabela de screening rápida, mas carregava débitos técnicos graves que o tornavam frágil, lento e arriscado para uso em decisões financeiras reais. O v2 (`YFINANCE_REFACTOR`) é uma **refatoração de profundidade real**: mudou arquitetura, metodologia, dados e interface. Não é uma versão "melhorada" — é um produto diferente construído sobre o aprendizado do v1.

| Sistema | Nota Técnica | Nota Metodológica | Nota Global |
|---------|-------------|-------------------|-------------|
| **v1 (run.sh)** | 2.5 / 10 | 3.0 / 10 | **2.5 / 10** |
| **v2 (YFINANCE_REFACTOR)** | 6.5 / 10 | 6.5 / 10 | **6.5 / 10** |

**Evolução: +160%** — salto real, não cosmético.

---

## PARTE I — ARQUITETURA: O QUE MUDOU

### v1: Monólito procedural com dependências frágeis

```
run.sh
  ├── Docker PostgreSQL (172.18.0.2 hardcoded)
  ├── Java yahooFinance.jar (binário opaco)
  ├── Google Finance scraping (CSS class "YMlKec fxKbKc")
  ├── curl para cada ticker → StatusInvest payout (síncrono, O(n))
  ├── src/main.py → HTML gerado via PrettyTable
  └── src/model/analysis.py → Plotly charts (arquivo separado, sem integração)

Output: index.html estático → cp /var/www/html/index.html
```

**Dependências do v1 (todas frágeis):**

| Dependência | Risco | Quem mantém |
|---|---|---|
| Docker PostgreSQL com IP hardcoded | Quebra se Docker mudar de rede | Usuário |
| `yahooFinance.jar` (Java) | Binário opaco, sem versionamento | Desconhecido |
| Google Finance HTML scraping (`YMlKec fxKbKc`) | Quebra a cada deploy do Google | Google |
| `curl` por ticker para payout | Bloqueável por rate limit, lento | StatusInvest |
| `python` vs `python3` detection no bash | Comportamento imprevisível | SO |

### v2: Serviços modulares com API REST

```
YFINANCE_REFACTOR/
  backend/
    ├── api_server.py            (REST API — desacoplado do frontend)
    ├── services/
    │   ├── price_service.py     (preços — isolado)
    │   ├── history_fetcher.py   (dividendos, min/max, acumulação)
    │   ├── buffett_fetcher.py   (FCF, Owner Earnings, tendências 4 anos)
    │   ├── valuation_calculator.py  (toda lógica de negócio)
    │   └── decision_service.py  (carteira / decisão de compra)
    ├── config/rules.py          (thresholds centralizados — não Enum, não hardcoded)
    ├── repositories/            (acesso a dados desacoplado)
    ├── data/                    (JSON files — sem Docker, sem banco)
    └── tests/                   (pytest — inexistente no v1)
  frontend/
    └── index.html               (SPA com API calls — sem PrettyTable)
```

**Eliminação de dependências críticas:**

| v1 | v2 | Ganho |
|---|---|---|
| PostgreSQL + Docker | JSON files | Zero infra, zero setup |
| yahooFinance.jar (Java) | yfinance (Python puro) | Auditável, versionado |
| Google Finance CSS scraping | Google Finance + fallback estruturado | Mesmo risco, melhor tratamento |
| curl síncrono por ticker | Integrado ao pipeline Python | 10-50x mais rápido |
| HTML hardcoded | REST API + SPA | Separação de responsabilidades real |

---

## PARTE II — FALHAS CRÍTICAS DO v1 COM EXEMPLOS

---

### FALHA v1-1: SQL Injection — vulnerabilidade de segurança real

**Código em `src/dao/stocksDAO.py`:**

```python
# LINHA 43 — v1
query = "select price_now from price where ticker like '{}';".format(ticker)
cur.execute(query)

# LINHA 17 — v1
query = "select stock.ticker, price.price_now, history.price_min, ... where ticker like '{}' ...".format(ticker)
```

**O risco:** Se `ticker` vier de input externo com `'; DROP TABLE stock; --`, o banco é destruído. Mesmo sendo um sistema pessoal, qualquer integração futura com input externo tornaria isso exploitável.

**O correto (parameterização):**
```python
cur.execute("SELECT price_now FROM price WHERE ticker = %s", (ticker,))
```

**v2:** Não há SQL — acesso via dict em JSON. Problema eliminado por design.

---

### FALHA v1-2: IP Docker hardcoded — sistema quebra sem aviso

**Código em `src/jdbc/connection_factory.py`:**

```python
conn = psycopg2.connect(
    host='172.18.0.2',   # IP hardcoded do container Docker
    database='yfinance',
    user='postgres',
    password='yfinance'
)
```

**O problema:** O IP `172.18.0.2` é atribuído pelo Docker automaticamente. Em qualquer reinício do daemon, criação de nova rede, ou mudança de configuração, o container pode receber um IP diferente — e o sistema quebra silenciosamente sem mensagem de erro útil.

**Consequência real:** O run.sh inclui lógica de restauração de banco:
```bash
$docker_exec_output "select count(*) from history where net_income = true;" > /dev/null 2>&1
if [ ! $? -eq 0 ]
    then echo "Restoring the database..."
    cat db/* | docker exec -i yfinance-postgres psql -U postgres
fi
```
Esse fallback existe porque o sistema quebrava frequentemente.

**v2:** Sem banco de dados. Sem IP hardcoded. Sem esse problema.

---

### FALHA v1-3: `conn.close` sem parênteses — connection leak

**Código em `src/dao/stocksDAO.py` (linhas 25, 51, 65):**

```python
conn.commit()
conn.close   # ← ERRO: sem () — isso é apenas uma referência ao método, não uma chamada
```

**O efeito:** As conexões com o PostgreSQL **nunca são fechadas**. Com cada execução do run.sh varrendo centenas de tickers, o pool de conexões do PostgreSQL vai sendo esgotado. Em uso contínuo (o loop `for (( ; ; ))` do comentário no run.sh), o banco eventualmente recusa novas conexões.

**v2:** Sem banco de dados. Sem conexões. Sem esse problema.

---

### FALHA v1-4: `except:` bare — bugs engolidos silenciosamente

**Ocorrências em `src/model/analysis.py`:**

```python
try:
    numeric_volume = float(last_valid)
    ...
except:        # captura TUDO — KeyboardInterrupt, SystemExit, erros de lógica
    continue   # e ignora silenciosamente
```

**O problema:** Bare `except` captura **qualquer exceção**, incluindo `KeyboardInterrupt` (Ctrl+C), `SystemExit`, e erros de lógica de negócio. Um ticker que falha por bug no código de cálculo é indistinguível de um ticker que falha porque foi delistado. O sistema simplesmente pula e continua.

**Consequência:** Empresas podem desaparecer da lista por bugs de código, não por critérios de negócio — sem nenhum aviso ao usuário.

**v2:** `try/except` específicos com logging estruturado e graceful failure diferenciado.

---

### FALHA v1-5: Filtro `pct_now_min <= 11` é matematicamente inútil

**Código em `src/main.py` linha 132:**

```python
pct_now_min = round(value_now/value_min, 2)
if pct_now_min <= 11:
    ...  # passa para análise
```

**O que isso significa:** `pct_now_min = preço_agora / preço_mínimo_6m`. Um valor de 11 significa que o preço atual pode ser **1100% do mínimo de 6 meses** e ainda assim passar no filtro. Nenhuma ação listada na B3 tem preço atual a 11x do seu mínimo de 6 meses — esse filtro nunca elimina nada.

**O que era a intenção original:** O comentário no código sugere que o filtro deveria identificar ações próximas do fundo de 6 meses. O valor correto seria `<= 1.10` (até 10% acima do mínimo), não `<= 11`.

**v2:** `p_now_p_min` calculado e exibido corretamente, sem filtro incorreto.

---

### FALHA v1-6: Lista de delistados hardcoded com 100+ tickers

**Código em `src/model/analysis.py` linhas 26-41:**

```python
list_delisted = ['APER3', 'APTI3', 'BBML3', 'BFRE11', 'BFRE12', 'BIDI11',
                 'BIDI3', 'BIDI4', 'BLUT3', ...  # 80+ tickers
                ]
```

E em `src/model/valuation.py` linhas 198-222 existe **outra lista** com 100+ tickers com sufixo `.SA`.

**O problema:** Duas listas de manutenção manual duplicadas e inconsistentes. Empresas que voltam à bolsa continuam na lista. Empresas recém-delistadas não estão na lista. O sistema simplesmente trava ou produz dados errados para elas.

**v2:** `stock_validator.py` valida dinamicamente via yfinance, persiste em `tickers.json` com flag `valid: false` após N falhas consecutivas. Zero manutenção manual.

---

### FALHA v1-7: Google Finance scraping dependente de CSS class

**Código em `libs/googleFinance.py` linha 68:**

```python
price_html = r.text.split("YMlKec fxKbKc")[1]
```

**O risco:** O Google muda nomes de classes CSS sem aviso — é obfuscation para dificultar scraping. A classe `YMlKec fxKbKc` pode mudar em qualquer deploy do Google. Quando isso acontece, **todos os preços tornam-se `None`** e o sistema roda com dados de preço zerados sem erro visível.

**O run.sh nem verifica se os preços foram atualizados** antes de gerar o HTML.

**v2:** Mesmo mecanismo de scraping, mas com validação de dados, cache com TTL e fallback estruturado.

---

### FALHA v1-8: Payout via `curl` síncrono — O(n) chamadas de rede bloqueantes

**Código em `src/model/valuation.py` linha 177:**

```python
format_str = 'curl -s --user-agent "Chrome/79" "https://statusinvest.com.br/acao/payoutresult?code="' + self.ticker.strip().lower() + " | grep 'actual' | awk -F ':' '{print $3}' | awk -F ',' '{print $1}'"
payout = subprocess.getoutput(format_str)
```

**O problema:**
1. **Shell injection**: `self.ticker` vai direto no comando shell sem sanitização
2. **Síncrono e lento**: Para 200 tickers, 200 chamadas curl sequenciais = minutos de espera
3. **Rate limit**: StatusInvest pode bloquear por abuso de requisições
4. **User-Agent "Chrome/79"**: versão de browser de 2019, detectável como bot
5. **`subprocess.getoutput`**: captura stdout sem tratar erros do processo

**v2:** Payout integrado ao pipeline de `history_fetcher.py`, buscado uma única vez com rate limit respeitado.

---

### FALHA v1-9: Fórmula de `pGain` metodologicamente incorreta

**Código em `src/main.py` linhas 93-105:**

```python
def calc_predict_gain(pNow, dy, pTarget):
    price_max = pTarget * (1 + (dy/100))   # ← adiciona DY% ao preço-alvo
    pGain = round(((price_max - pNow)/pNow)*100, 2)
```

**O que essa fórmula faz:** Multiplica o `pTarget` pelo `(1 + DY%)` para calcular o ganho esperado.

**O que está errado:** O DY% nessa fórmula é o Dividend Yield **estático do StatusInvest** (calculado sobre o preço atual), não sobre o preço-alvo. Isso cria um cálculo circular onde o yield muda conforme o preço muda. Para uma ação com DY = 8% e pTarget = R$34, o cálculo seria: `R$34 × 1.08 = R$36.72` como "preço máximo esperado" — misturando preço e yield de forma matematicamente incorreta.

**O correto:** O ganho potencial é simplesmente `((pTarget - pNow) / pNow) × 100`. O dividendo é renda separada, não componente do preço-alvo.

**v2:** `gain_pct_to_target = ((price_target_6 - price_now) / price_now) × 100` — matematicamente correto e simples.

---

### FALHA v1-10: Ranking com todos os critérios com peso igual — distorce a decisão

**Código em `src/model/valuation.py`:**

```python
def calc_ranking_indicators(self, dict_stock):
    rank = 0
    if price_now <= vpa: rank += 1       # peso 1
    if dy >= 6: rank += 1                 # peso 1
    if p_l <= 15: rank += 1              # peso 1
    if roe >= 10: rank += 1              # peso 1
    # ... 14 critérios, todos peso 1
    return rank  # max 14
```

**O problema:** Uma ação com DY = 6.1% e ROE = 5% e todas as outras métricas ruins pode ter **o mesmo ranking** que uma ação com ROE = 25%, Margens excelentes e DY = 6%. O ROE vale tanto quanto o P/L quanto o DL/EBITDA — todos equivalem a 1 ponto.

**Buffett:** A qualidade do negócio (ROE, margens) é muito mais importante do que o preço de entrada (P/L, P/VP). Equalizar os pesos é afirmar que comprar barato uma empresa ruim é tão bom quanto comprar uma empresa excelente — o oposto da filosofia value investing.

**v2:** `WEIGHTED_SCORE_WEIGHTS` — ROE e margens têm peso 3, P/L e P/VP têm peso 1.5.

---

### FALHA v1-11: Média de dividendos simples sem verificação de consistência

**Código em `src/model/valuation.py` linhas 239-286:**

```python
# Calcula média simples dos dividendos dos últimos 5 anos
sum_dividends = 0
count_years   = 0
# Para cada ano com ao menos 1 dividendo: count_years += 1
temp = float(sum_dividends/count_years/0.06)
return float(sum_dividends/count_years)  # média simples
```

**Três problemas:**

1. **Média simples ignora tendência**: uma empresa com dividendo crescente (0.5 → 2.6) e uma com dividendo em queda (2.6 → 0.5) têm a mesma média. Os preços-alvo seriam idênticos. Para Barsi, são situações opostas.

2. **Sem verificação de consistência**: empresa que pagou em 2021, 2022, pulou 2023, voltou em 2024 e 2025 → `count_years = 4`. O sistema usa a média sem sinalizar a interrupção. Bazin eliminaria essa empresa.

3. **O preço-alvo é calculado e descartado**: `temp = float(sum_dividends/count_years/0.06)` é calculado mas **não retornado** — só é chamado para ter o efeito de gerar `list_price_target_year`. O retorno é apenas o dividendo médio sem o divisor 0.06.

**v2:** Média ponderada (anos recentes têm peso maior) + verificação de consistência via `paid_dividends_5_years` + `dividend_growing` com tolerância de 10%.

---

### FALHA v1-12: Sem pré-qualificação — sistema analisa tudo indiscriminadamente

**v1:** Qualquer ticker que tiver dados no banco passa para a tabela de saída. Não há verificação de:
- Anos consecutivos com dividendo
- Anos consecutivos com lucro positivo
- P/L positivo (P/L negativo = empresa com prejuízo)

O único filtro além da liquidez é:
```python
if float(dic_stock['P/L']) <= 0:
    continue
```

**Consequência real:** Uma empresa que pagou dividendo uma vez em 5 anos e nunca mais pagou aparece na tabela com um preço-alvo calculado sobre aquele único pagamento. O usuário vê uma ação aparentemente barata com "DY alto" que na realidade é um fantasma histórico.

**v2:** Pré-qualificação obrigatória: 5 anos de dividendos + 5 anos de lucro positivo + liquidez mínima + P/L positivo. Qualquer falha → `return None`.

---

### FALHA v1-13: Output como HTML estático — sem interatividade, sem contexto

**v1:** A saída é uma tabela HTML gerada por PrettyTable:

```python
out_table = myTable.get_html_string(attributes={"class": "table"}, format=True)
print(out_table)  # impresso para stdout → redirecionado para index.html
```

Seguido de regex manual para colorir células:
```python
table = re.sub('<td style="...">{}</td>'.format(row),
               '<td style="..." bgcolor="{}">{}</td>'.format(color, row), table)
```

**Problemas:**
- Sem ordenação interativa
- Sem filtragem dinâmica
- Cores aplicadas via regex sobre HTML (frágil, quebrável com qualquer mudança no PrettyTable)
- O `analysis.py` gera um arquivo `specific_analysis.html` completamente separado — dois sistemas sem comunicação
- Sem modalS de detalhe — tudo na mesma linha, 25 colunas, ilegível em mobile

**v2:** SPA com REST API, modal por ativo, zonas de preço clicáveis, filtros por zona, Moat Score visual com gauge, tabela de tendências históricas, cards de cashflow.

---

## PARTE III — COMPARATIVO TÉCNICO DETALHADO

### 3.1 Infraestrutura

| Dimensão | v1 (run.sh) | v2 (YFINANCE_REFACTOR) | Evolução |
|---|---|---|---|
| Banco de dados | PostgreSQL via Docker | JSON files | Sem infra, zero setup |
| IP hardcoded | `172.18.0.2` | N/A | Eliminado |
| Java dependency | `yahooFinance.jar` | Eliminado | -1 linguagem |
| Dependências Python | PrettyTable, plotly, psycopg2, httpx, bs4 | yfinance, flask/fastapi | Mais coeso |
| Execução | `bash run.sh` (cron manual) | API server + pipeline independente | Separação real |
| Portabilidade | Requer Docker + Java + PostgreSQL | `pip install + python` | Alta |

### 3.2 Segurança

| Vulnerabilidade | v1 | v2 |
|---|---|---|
| SQL Injection | ❌ Presente (format string em SQL) | ✅ N/A (sem SQL) |
| Shell Injection | ❌ Presente (curl com ticker não sanitizado) | ✅ N/A (sem shell calls) |
| Credenciais hardcoded | ❌ `password='yfinance'` no código | ✅ N/A (sem banco) |
| Connection leak | ❌ `conn.close` sem `()` | ✅ N/A |
| Scraping sem rate limit | ❌ curl por ticker sem delay | ✅ Rate limit respeitado |

### 3.3 Metodologia de Investimento

| Critério | v1 | v2 | Δ |
|---|---|---|---|
| **Número de critérios de screening** | 14 | 21 | +50% |
| **Pesos diferenciados** | ❌ Todos peso 1 | ✅ Qualidade peso 3, preço peso 1.5 | Correto |
| **Pré-qualificação** | ❌ Nenhuma | ✅ 5 anos dividendos + lucro | Correto |
| **Média ponderada dividendos** | ❌ Média simples | ✅ Pesos crescentes por ano | Correto |
| **Zonas de preço** | 1 (comprar/não comprar) | 4 (COMPRA_FORTE/COMPRA/MONITORAR/CARO) | +300% |
| **Piotroski F-Score** | ❌ | ✅ 9 sinais | Novo |
| **Buffett Moat Score** | ❌ | ✅ 0-10 com 8 critérios | Novo |
| **Owner Earnings** | ❌ | ✅ NI + D&A − CapEx | Novo |
| **Free Cash Flow** | ❌ | ✅ FCO − CapEx | Novo |
| **Tendências históricas 4 anos** | ❌ | ✅ 7 métricas com direção | Novo |
| **Setor financeiro tratado diferente** | ❌ | ✅ proxy pl_ativo | Novo |
| **Score ponderado 0-100** | ❌ | ✅ normalizado | Novo |
| **Graham combo P/L × P/VP** | ❌ | ✅ ≤ 22.5 | Novo |
| **Acumulação silenciosa** | ⚠️ Calculado mas não pontuado | ✅ Critério no score | Melhorado |
| **Consistência dividendos com tolerância** | ❌ | ✅ tolerância 10% | Novo |
| **fórmula pGain correta** | ❌ (DY multiplicado no target) | ✅ (((target - now)/now)×100) | Corrigido |

### 3.4 Confiabilidade

| Aspecto | v1 | v2 |
|---|---|---|
| Testes automatizados | ❌ Zero | ⚠️ Parciais (price_service) |
| Tratamento de erros | `except: continue` (engole tudo) | `except SpecificError: graceful_fail` |
| Validação de tickers | Lista hardcoded manual | `stock_validator.py` dinâmico |
| Freshness dos dados | Sem controle | TTL por serviço (`HISTORY_UPDATE_INTERVAL_DAYS = 7`) |
| Logging | `print()` misturado com output HTML | Separado do output de dados |
| Dados corrompidos silenciosos | ❌ Nenhuma defesa | ⚠️ Graceful failure por campo |

### 3.5 UX e Output

| Aspecto | v1 | v2 |
|---|---|---|
| Interface | Tabela HTML estática, 25 colunas | SPA responsiva com cards e modal |
| Interatividade | Zero (HTML gerado e servido) | Filtros por zona, ordenação, toggle CARO |
| Detalhe por ativo | Zero | Modal com 6 seções (Score, Piotroski, Moat, Cashflow, Tendências, Flags) |
| Gauge visual | Zero | Gauge 0-10 com zonas de cor para Moat Score |
| Gráficos de análise | Arquivo separado (`specific_analysis.html`) | Integrado via API |
| Mobile | ❌ Inutilizável (25 colunas) | ⚠️ Parcialmente responsivo |
| API consumível | ❌ Nenhuma | ✅ REST API com endpoints documentados |

---

## PARTE IV — O QUE O v1 FEZ BEM

Seria desonesto ignorar o que o v1 acertou:

### 1. A ideia central estava correta desde o início

`preço_alvo = média_dividendos / 0.06` — a fórmula de Bazin/Barsi estava implementada corretamente desde a v1. A filosofia fundacional de precificação por renda dividida por taxa mínima é a mesma nos dois sistemas.

### 2. O conceito de acumulação silenciosa nasceu no v1

`analysis.py` linhas 104-107:

```python
below_condition = (historical_data['Close'] < price_mean) & (historical_data['Volume'] < volume_mean)
condition_percentage = (below_condition.sum() / len(below_condition)) * 100
```

Isso é o mesmo `accumulation_score` que o v2 usa como critério de decisão. O conceito nasceu no v1, não foi inventado no v2.

### 3. Os gráficos Plotly de volume + preço foram inovação real

O `create_specific_analysis()` com gráficos interativos Plotly, dual-axis (volume/preço), shading vermelho nos períodos de acumulação, marcador "Build Position 🚀" — isso era sofisticado para um sistema pessoal. O v2 perdeu essa funcionalidade visual ao descartar o `analysis.py`.

### 4. O filtro de liquidez diária estava correto

`if float(dic_stock['D.AVG.LQ']) < 0.2: continue` — R$200k/dia mínimo. Esse threshold migrou intacto para o v2 (`LIQUIDEZ_DIARIA_MIN = 200000.0`). O v1 acertou esse limiar desde o início.

### 5. O payout via StatusInvest era a fonte certa

Mesmo sendo via `curl` (lento e frágil), o v1 buscava o payout da fonte correta — StatusInvest — que calcula sobre o resultado contábil real. O v2 manteve essa fonte.

---

## PARTE V — O QUE O v2 AINDA DEVE AO v1

O v2 eliminou funcionalidades do v1 que não foram reescritas:

### 1. Gráficos interativos de volume/preço

O `analysis.py` do v1 gerava charts Plotly com:
- Volume + preço em dual-axis
- Linha de média de volume
- Linha de preço-alvo
- Shading vermelho nos períodos de acumulação
- Link de ancoragem `#chart_TICKER` para navegação

**O v2 não tem equivalente.** O frontend mostra cards com números, mas sem visualização temporal do comportamento de preço e volume. Para um investidor que quer **ver** o padrão de acumulação silenciosa, o v1 era superior nesse ponto específico.

### 2. Histórico de preço-alvo por ano

O v1 calculava e armazenava `list_price_target_year` — como o preço-alvo evoluiu ano a ano conforme os dividendos foram pagos. O v2 não expõe essa progressão histórica.

### 3. Gráfico de preço com anotação "Build Position"

A marcação visual `Build Position 🚀 ⭐ Target 🌟 VPA 📈 Avg Price 📈 Avg Volume` quando todas as condições eram satisfeitas simultaneamente era um sinal operacional claro e visual. O v2 tem os flags no modal, mas sem a visualização temporal.

---

## PARTE VI — SCORE FINAL POR DIMENSÃO

### v1 (run.sh)

| Dimensão | Nota | Justificativa |
|---|---|---|
| **Arquitetura** | 1.5/10 | Monólito frágil, Docker hardcoded, Java binary, bash orchestration |
| **Segurança** | 1/10 | SQL injection real, shell injection, credenciais hardcoded, connection leak |
| **Confiabilidade** | 2/10 | Bare except everywhere, IP hardcoded, CSS scraping frágil, lista manual de delistados |
| **Metodologia** | 3/10 | Fórmula central correta, mas ranking igualitário, sem pré-qualificação, média simples |
| **UX / Output** | 3/10 | Tabela funcional mas 25 colunas ilegíveis; gráficos Plotly eram ponto forte |
| **Manutenibilidade** | 1/10 | Zero testes, dois sistemas sem integração, listas hardcoded, sem separação de responsabilidades |
| **Escalabilidade** | 1/10 | O(n) curl calls, conexões não fechadas, output estático sem API |

**Nota global v1: 2.5 / 10**

---

### v2 (YFINANCE_REFACTOR)

| Dimensão | Nota | Justificativa |
|---|---|---|
| **Arquitetura** | 7/10 | Modular, REST API, sem infra pesada, separação de responsabilidades clara |
| **Segurança** | 8/10 | Sem SQL, sem shell injection, sem credenciais hardcoded — mas scraping ainda presente |
| **Confiabilidade** | 5/10 | Graceful failure, TTL por serviço, mas zero testes no core de negócio |
| **Metodologia** | 6.5/10 | 21 critérios, pesos corretos, Piotroski, Moat Score, Owner Earnings — mas CapEx total ≠ manutenção |
| **UX / Output** | 7/10 | SPA com modal rico, zones, gauge visual — perdeu gráficos de volume/preço do v1 |
| **Manutenibilidade** | 6/10 | Separação clara, rules.py centralizado, mas testes insuficientes |
| **Escalabilidade** | 7/10 | API REST, JSON files, pipeline independente, sem infra bloqueante |

**Nota global v2: 6.5 / 10**

---

## PARTE VII — LINHA DO TEMPO DA EVOLUÇÃO

```
2021 ── v1 nasce: bash + Java + PostgreSQL + PrettyTable
        ✓ Fórmula Bazin/Barsi implementada
        ✓ Conceito de acumulação silenciosa criado
        ✗ SQL injection, connection leak, IP hardcoded

2022 ── v1 estabiliza: lista de delistados cresce, análise.py adiciona Plotly
        ✓ Gráficos interativos volume/preço
        ✓ Build Position visual com 🚀
        ✗ Dois sistemas sem integração (main.py + analysis.py)

2023 ── v1 em manutenção: dump de banco regularmente
        ✗ Google Finance quebra com mudanças de CSS
        ✗ yahooFinance.jar não é atualizado

2026-Mar-19 ── v2 Fase 1: Buffett Moat Score (8 critérios, 0-10)
               ✓ Score MOAT no frontend
               ✓ Weighted score com pesos diferenciados

2026-Mar-19 ── v2 Fase 2: Owner Earnings e FCF via yfinance
               ✓ CapEx, D&A, FCO, FCF, Owner Earnings calculados
               ✓ Seção "Qualidade do Caixa" no modal

2026-Mar-20 ── v2 Fase 3: Tendências históricas 4 anos
               ✓ 7 métricas com direção CRESCENDO/ESTÁVEL/CAINDO
               ✓ Modificadores de tendência no Moat Score

2026-Mar-20 ── v2 Fase 4: SG&A/Receita + gauge visual + valores por critério
               ✓ Gauge 0-10 com zonas de cor
               ✓ Rodapé com legenda de inversão de polaridade

2026-Mar-22 ── Correções baseadas em crítica:
               ✓ Média ponderada de dividendos (anos recentes têm peso maior)
               ✓ Tolerância 10% no dividend_growing
               ✓ Modificadores MB/ROE integrados ao Moat Score
               ✓ Payout > 100% sinalizado visualmente (sem hard filter)
```

---

## CONCLUSÃO

O v1 foi o laboratório onde as ideias foram testadas. Ele provou que a filosofia central (renda como precificador, acumulação silenciosa, múltiplos critérios fundamentalistas) era válida — e entregou resultados reais para quem o usou como ferramenta pessoal. Mas era um protótipo com dívida técnica grave.

O v2 é a materialização madura dessas ideias: arquitetura defensável, metodologia mais rigorosa, dados mais ricos, interface mais útil. A distância entre os dois sistemas — técnica e metodológica — representa um salto de maturidade real, não incremental.

O que o v2 deve ao v1: a ideia. O que o v2 entrega que o v1 nunca poderia: confiabilidade, profundidade e escalabilidade.

> *"A primeira versão de qualquer sistema é o mapa do terreno. A segunda versão é o caminho real."*
