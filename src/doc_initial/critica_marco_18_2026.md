# Análise Crítica da Aplicação — 18/03/2026
> Visão de um investidor experiente no estilo Luiz Barsi

---

## PONTOS POSITIVOS

### 1. Fundamento correto: precificação por dividendo
A base do sistema é impecável: `preço_alvo = dividendo_médio / yield_alvo`. É exatamente o que Barsi chama de "preço justo". O sistema entende que ação é sócia de empresa, não papel para especular.

### 2. Pré-qualificação rigorosa
Exigir **5 anos de dividendos + 5 anos de lucro positivo** antes de entrar na análise elimina empresas que pagaram dividendo extraordinário uma vez. Correto.

### 3. Três zonas de preço-alvo (5%, 6%, 8%)
A hierarquia `COMPRA_FORTE → COMPRA → MONITORAR → CARO` é um modelo prático e didático. A lógica de `p_now_p_min` como trigger de entrada é inteligente.

### 4. Piotroski F-Score
Boa escolha. Os 9 sinais cobrem rentabilidade, alavancagem e eficiência operacional. FORTE (≥7) como indicador de qualidade é academicamente sólido.

### 5. Acumulação Silenciosa
Detectar dias com preço + volume abaixo da média (smart money entrando quieto) é um conceito avançado. Poucos sistemas de varejo têm isso.

### 6. Arquitetura Limpa
Repository pattern, separação de serviços, cache por camadas (30min preço, 7 dias histórico). O pipeline de dados está bem pensado.

### 7. Testes Unitários do PriceService
Cobertura real com mocks: cache, force update, falha parcial, normalização de ticker. 22 testes cobrindo todos os cenários relevantes do serviço de preços.

---

## PONTOS NEGATIVOS — COM EXEMPLOS PRÁTICOS

---

### CRÍTICA 1: TGMA3 aparece como COMPRA com Payout de 104,32%

**O dado real** (`data/decision_stocks.json`):
```json
"ticker": "TGMA3",
"zone": "COMPRA",
"dy_real": 7.2,
"payout": 104.32
```

**O problema:** Payout > 100% significa que a empresa pagou **mais dividendo do que lucrou**. Ela usou reservas ou fez dívida para pagar dividendos. Barsi diria na hora: *"Empresa que paga dividendo com capital de giro não é empresa saudável, é uma bomba-relógio."*

A flag `payout_ok` fica `False` (reduz 1 ponto no rank), mas **a zona continua COMPRA**. Um investidor inexperiente vê "COMPRA + DY 7,2%" e compra sem saber que o dividendo é insustentável.

**Teste que deveria existir — e falharia hoje:**
```python
# Nenhuma empresa com payout > 100% pode ter zone = COMPRA ou COMPRA_FORTE
for stock in decision_stocks:
    assert stock["zone"] not in ("COMPRA", "COMPRA_FORTE") or stock["payout"] <= 100
# Resultado: FALHA para TGMA3 (payout=104.32, zone=COMPRA)
```

**Correção necessária:** Adicionar à pré-qualificação: `payout <= 100` (ou `<= 95`) como hard filter, não apenas critério de pontuação.

---

### CRÍTICA 2: Stocks com zona CARO poluem a lista de decisão

**Os dados reais** (`data/decision_stocks.json`):

| Ticker | Zone | DY Real | p_now_p_min | Posição na lista |
|--------|------|---------|-------------|-----------------|
| MDIA3  | CARO | 3,94%   | 1.0027      | 2ª              |
| TOTS3  | CARO | 1,22%   | 1.0070      | 3ª              |

A lista é ordenada por `p_now_p_min` (melhor ponto de entrada pelo preço mínimo de 6 meses). MDIA3 está no **2º lugar** — quase no mínimo de 6 meses. Um usuário olha e pensa: *"ótima entrada"*. Mas:

- DY real de 3,94% → o próprio sistema considera válido apenas acima de 6%
- Zona CARO → pelo critério interno, o papel está caro

A lista de decisão está **misturando oportunidades com armadilhas de preço baixo**. Preço no mínimo histórico de uma empresa cara ainda é caro.

---

### CRÍTICA 3: LIQUIDEZ_CORRENTE_MIN = 2.0 elimina sistematicamente bancos

**A regra** (`config/rules.py`):
```python
LIQUIDEZ_CORRENTE_MIN = 2.0   # Liquidez corrente mínima (Graham: >= 2.0)
```

O padrão Graham de 2.0 foi criado para **empresas industriais e comerciais**. Bancos, seguradoras e financeiras têm liquidez corrente próxima de 0.5–1.0 por design — os depósitos de clientes são passivos circulantes, mas os ativos correspondentes são empréstimos de longo prazo.

**Consequência:** BBAS3, ITUB4, ABCB4 **falham** sistematicamente em `liquidez_corrente_ok`. Exatamente as empresas que Barsi mais ama — ele acumulou fortuna em BBAS3 e ITSA4 ao longo de décadas.

**O que acontece na prática:**
```python
# ABCB4: liquidez_corrente ≈ 0.8 (normal para banco)
# O critério marca como FALHA → penaliza 2 pontos no weighted_score
# Um banco sólido com ROE=15%, DY=10%, Piotroski FORTE perde pontos
# por uma métrica que não se aplica ao seu modelo de negócio
```

**Correção:** Usar `liquidez_corrente_ok = True` automaticamente para o setor Financeiro, ou substituir pelo critério de `passivo_ativo` nesses casos.

---

### CRÍTICA 4: `avg_dividends_5y` = média simples distorce os preços-alvo

**Exemplo com ABCB4** (`data/stock_history.json`):
```
2021: R$ 0.98
2022: R$ 1.25
2023: R$ 1.19
2024: R$ 2.39
2025: R$ 2.62
Média simples 5 anos: R$ 1.69
```

A média R$1.69 gera `price_target_6pct = R$28.16`.
Mas o dividendo atual real é R$2.62 → que geraria target de R$43.67.

O preço-alvo baseado na média está **35% abaixo** do que deveria ser com o dividendo vigente. Isso faz o sistema mostrar zone=COMPRA quando a empresa pode estar em COMPRA_FORTE, ou subestima o potencial real da oportunidade.

Barsi sempre olha a **tendência crescente** — peso maior nos anos recentes é mais realista do que tratar 2021 igual a 2025.

---

### CRÍTICA 5: `dividend_growing` é binário e muito punitivo

**A lógica atual:**
```python
dividend_growing = dividendo_ultimo_ano >= max(dividendos_anos_anteriores)
```

Uma empresa que cresceu dividendo por 4 anos consecutivos:
`R$0.50 → R$1.00 → R$1.50 → R$2.00 → R$1.90` (queda de 5% no último ano)
recebe `dividend_growing = False` e perde **2 pontos** de peso no score.

**O problema:** Barsi segura ação por 20 anos. Uma queda pontual de 5% num único ano não invalida uma empresa com tendência estrutural de crescimento de dividendos.

**Demonstração:**
```python
dividendos = [0.50, 1.00, 1.50, 2.00, 1.90]
max_anterior = max(dividendos[:-1])   # = 2.0
ultimo = dividendos[-1]               # = 1.9
dividend_growing = ultimo >= max_anterior  # False — PENALIZA empresa excelente
```

**Sugestão:** Verificar tendência linear (regressão simples) ou ao menos exigir que a média dos 2 últimos anos supere a média dos 2 anteriores.

---

### CRÍTICA 6: TOTS3 (tech) na lista de decisão — ausência de filtro por setor

**O dado** (`data/decision_stocks.json`):
```json
"ticker": "TOTS3",
"dy_real": 1.22,
"zone": "CARO",
"sector": "Tecnologia"
```

TOTS3 é a Totvs, uma empresa de software. DY de 1,22%. Barsi em diversas entrevistas: *"Empresa de tecnologia não é pra mim. Não sei o que vai acontecer com ela daqui a 10 anos."*

O sistema não tem filtro de setor nem bloqueio mínimo de DY na saída da lista de decisão. Uma empresa de tech cara com dividendo irrisório aparece ao lado de bancos e utilities sólidos.

---

### CRÍTICA 7: `PASSIVO_ATIVO_MAX = 1.0` é praticamente inútil

**A regra** (`config/rules.py`):
```python
PASSIVO_ATIVO_MAX = 1.0   # Passivo / Ativo máximo
```

Passivo/Ativo = 1.0 significa **patrimônio líquido = zero** — empresa tecnicamente insolvente. Um threshold de 100% não filtra quase nada na prática.

O usual para empresas não-financeiras é 0.6 ou 0.7. O próprio arquivo usa 0.4 para o Piotroski (`PIOTROSKI_PASSIVO_ATIVO_MAX = 0.4`) — **inconsistência interna** usando métricas diferentes para o mesmo conceito.

---

### CRÍTICA 8: Os serviços mais críticos não têm testes

Você tem testes para o `PriceService` (infraestrutura). Mas os serviços que fazem a **decisão de compra** não têm nenhuma cobertura:

| Serviço | Testes |
|---------|--------|
| `services/price_service.py` | ✅ 22 testes |
| `services/valuation_calculator.py` | ❌ zero |
| `services/decision_service.py` | ❌ zero |
| `services/portfolio_service.py` | ❌ zero |

Barsi diria: *"Você testou o placar do jogo mas não testou as regras."*

Os cálculos de `price_target_6pct`, `is_gold`, `weighted_score`, `zone` e `recommendation` nunca foram validados automaticamente. Um bug silencioso nos critérios de compra pode custar dinheiro real.

**Exemplos de testes que deveriam existir:**
```python
# Zona correta para cada faixa de preço
def test_zone_compra_forte():
    # preço abaixo do target 8% → COMPRA_FORTE
    assert calc_zone(price=20.0, target_8pct=21.0) == "COMPRA_FORTE"

def test_is_gold_requer_abaixo_vpa():
    # is_gold = False se price > VPA, mesmo com outros critérios ok
    assert not calc_is_gold(price=30.0, vpa=25.0, target_6pct=32.0)

def test_payout_acima_100_nao_qualifica():
    assert not pre_qualify(payout=104.32)
```

---

### CRÍTICA 9: Price fetching por scraping HTML — frágil por design

O `price_service.py` busca preço pelo seletor CSS `class="YMlKec fxKbKc"` do Google Finance.

Google muda classes CSS rotineiramente. Quando isso acontece, **todos os 122 tickers** param de atualizar preço silenciosamente — o sistema continua servindo preços stale sem alertar o usuário.

Não há monitoramento de quando o último fetch real aconteceu. Um preço de 3 dias atrás aparece igual a um preço de 10 minutos atrás na interface.

---

### CRÍTICA 10: `all_indicators.json` sem verificação de freshness

Todo o `weighted_score`, Piotroski e os 21 critérios são calculados com base neste arquivo (fundamentais do StatusInvest). Não há validação no código de quando ele foi gerado.

Se o arquivo tiver 3 meses de defasagem, você está analisando **balanços do trimestre passado com preços de hoje** — uma combinação perigosa para decisão de compra. Uma empresa pode ter piorado os fundamentos e o sistema ainda mostra COMPRA_FORTE.

---

## RESUMO EXECUTIVO

| Dimensão | Nota | Observação |
|----------|------|------------|
| Metodologia | 8/10 | Base Barsi/Bazin sólida, bem implementada |
| Dados | 4/10 | Scraping frágil, freshness desconhecido |
| Critérios | 5/10 | Thresholds genéricos ignoram setor financeiro |
| Decisões | 6/10 | Lista de decisão polui com stocks zona CARO |
| Testes | 4/10 | Só infraestrutura testada, lógica de negócio não |
| Arquitetura | 8/10 | Pipeline, repository pattern e cache bem feitos |

---

## PRIORIDADE DE CORREÇÃO

1. **Urgente** — Filtrar `payout > 100%` na pré-qualificação (impacto direto na confiabilidade das recomendações)
2. **Urgente** — Remover ou segregar stocks zona CARO da lista principal de decisão
3. **Alta** — Exceção de `liquidez_corrente` para setor Financeiro
4. **Alta** — Testes unitários para `valuation_calculator.py` (pelo menos zona, is_gold e weighted_score)
5. **Média** — Média ponderada para `avg_dividends_5y` (anos recentes com peso maior)
6. **Média** — Corrigir `PASSIVO_ATIVO_MAX` de 1.0 para 0.65 (empresas não-financeiras)
7. **Baixa** — Substituir scraping por API oficial de cotações com fallback explícito
