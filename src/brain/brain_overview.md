# Brain YFinance — Visão Geral e Filosofias

> Parte 1/4 do brain. Para arquitetura/código → `brain_architecture.md`. Para cálculos/fórmulas → `brain_calculations.md`. Para UI/dados/limitações → `brain_frontend.md`.

---

## 1. Visão Geral

### O que é

Uma aplicação de **screening e gestão de investimentos em ações da B3**, construída como ferramenta pessoal para auxiliar na tomada de decisão com base em múltiplas filosofias de investimento em renda variável.

A aplicação combina, em tempo real, dados fundamentalistas, histórico de dividendos, análise técnica simplificada e critérios de qualidade para **rankear e classificar ações brasileiras**, destacando as melhores oportunidades de entrada.

### O que faz

- **Screening**: exibe todas as ações monitoradas com pontuação, zona de compra, potencial de valorização e distância do suporte
- **Carteira**: acompanha posições reais com retorno, DY sobre preço médio e análise fundamentalista integrada
- **Favoritos**: lista personalizada de ativos com visualização rápida em cards ou tabela
- **Radar**: alertas de preço configuráveis por ativo (compra e venda)

### Stack Técnica

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.8 |
| API | Flask (REST) |
| Dados de mercado | yfinance (Yahoo Finance), Google Finance (scraping) |
| Dados fundamentalistas | StatusInvest (API não oficial) |
| Custódia | B3 XLS (xlrd) |
| Cálculos numéricos | numpy (regressão linear para tendências) |
| Persistência | JSON com atomic writes (sem banco de dados) |
| Frontend | HTML + JavaScript vanilla (sem framework) |
| Agendamento | Daemon thread Flask |

### Filosofia Híbrida

```
Barsi   → Quando comprar (yield, setor, acumulação silenciosa)
Bazin   → Quanto vale (preço justo via dividendo médio / 6%)
Graham  → Margem de segurança (P/L, P/VP, VPA, liquidez, dívida)
Buffett → Qualidade do negócio (moat, FCF, owner earnings)
```

---

## 2. Filosofias de Investimento Implementadas

### 2.1 Luiz Barsi Filho — "A Galinha dos Ovos de Ouro"

**Filosofia central:** Comprar empresas como quem compra um negócio. O objetivo é acumular renda, não especular com preço. *"Compre a galinha, não o ovo."*

O que mais importa para Barsi:
- A empresa **paga dividendos consistentemente** há no mínimo 5 anos
- O **preço atual está abaixo do preço que entrega pelo menos 6% de yield**
- A empresa opera em **setores essenciais e defensivos** (BEST: Bancos, Elétricas, Seguros, Saneamento, Transmissão)
- **Comprar quando ninguém quer**: quando preço E volume estão abaixo da média, é sinal de acumulação silenciosa — o momento ideal de entrar

**O que foi implementado da filosofia Barsi:**
- ✅ DY ≥ 6% (critério de compra)
- ✅ Preço abaixo do alvo 6% (Bazin)
- ✅ Três zonas de preço: 5% (monitorar), 6% (compra), 8% (compra forte)
- ✅ Acumulação silenciosa: score de dias com preço E volume abaixo da média 6m
- ✅ Filtro BEST por setor
- ✅ Consistência de dividendos (5 anos)
- ✅ Dividendo crescente (flag)

---

### 2.2 Décio Bazin — "Faça Fortuna com Ações" (1992)

**Filosofia central:** Ações são pedaços de um negócio. O preço justo é determinado pela renda que o negócio gera. Se o dividendo é consistente, o preço justo pode ser calculado matematicamente.

**Fórmula do Preço Justo (Bazin):**
```
Preço Justo = Média de Dividendos (últimos 5 anos, ponderado) / 0.06
```

**6 Critérios de Bazin:**

| # | Critério | Limiar | Implementado |
|---|---------|--------|-------------|
| 1 | Dividend Yield | ≥ 6% | ✅ |
| 2 | Consistência de dividendos | ≥ 5 anos sem interrupção | ✅ |
| 3 | Payout Ratio | 40% a 80% | ✅ |
| 4 | Dívida Líq./PL | ≤ 1.0 | ✅ |
| 5 | Liquidez diária | ≥ R$200k/dia | ✅ |
| 6 | Setores defensivos | Utilities, bancos | ✅ (filtro BEST) |

**Detalhe crítico do Payout:**
- Payout **< 40%**: empresa retém demais (má alocação ou problema escondido)
- Payout **> 80%**: dividendo insustentável (paga mais do que ganha)
- Faixa saudável: **40% a 80%**

---

### 2.3 Benjamin Graham — "O Investidor Inteligente"

**Filosofia:** Comprar com margem de segurança. O mercado é Mr. Market — um sócio maníaco-depressivo. Compre quando ele está deprimido.

**Critérios do Investidor Defensivo implementados:**

| # | Critério | Limiar Graham | Implementado |
|---|---------|--------------|-------------|
| 1 | P/L moderado | ≤ 15 (média 3 anos) | ✅ |
| 2 | P/VP moderado | ≤ 1.5 | ✅ |
| 3 | Regra combinada | P/L × P/VP ≤ 22.5 | ✅ |
| 4 | Preço ≤ VPA | Preço ≤ Valor Patrimonial por Ação | ✅ (flags de medalha) |
| 5 | Liquidez corrente | ≥ 2.0 | ✅ |
| 6 | Dívida/Ativos | ≤ 65% | ✅ |
| 7 | Crescimento de EPS | ≥ 5% CAGR 5a | ✅ |

**Regra Combinada de Graham:**
```
P/L × P/VP ≤ 22.5

Exemplo: P/L = 12 e P/VP = 1.8 → 12 × 1.8 = 21.6  ✅ (aprovado)
Exemplo: P/L = 15 e P/VP = 1.6 → 15 × 1.6 = 24.0  ❌ (reprovado)
```
Esta regra permite que uma empresa com P/VP alto (premium de qualidade) ainda passe se o P/L for baixo.

---

### 2.4 Warren Buffett — Moat, FCF e Owner Earnings

**Filosofia:** "É muito melhor comprar uma empresa maravilhosa a um preço justo do que uma empresa justa a um preço maravilhoso."

Buffett busca **vantagens competitivas duráveis (moat)** que protejam os lucros no longo prazo.

**O que foi implementado da filosofia Buffett:**

**Buffett Moat Score (0-10)** — mede a durabilidade da vantagem competitiva:
- Margem Bruta ≥ 40% → **pricing power** (peso 2)
- ROE ≥ 20% → **eficiência de capital** (peso 2)
- Margem Líquida ≥ 20% → lucro real após todos os custos
- ROIC ≥ 15% → retorno sobre capital investido
- DL/PL ≤ 0.5 → empresa com moat não precisa de muita dívida
- CAGR Lucro ≥ 10% e CAGR Receita ≥ 5% → crescimento consistente
- Dividendo crescente → sinal de geração de caixa sustentável

**FCF (Free Cash Flow):** `FCO - |CapEx|`
> Filtro de qualidade de lucro: lucro contábil vs. caixa real gerado

**Owner Earnings (Buffett's true profit):** `Lucro Líquido + D&A - |CapEx|`
> O verdadeiro lucro disponível para o dono do negócio

**FCF/Lucro ≥ 80%:** se menos de 80% do lucro vira caixa real, há risco de manipulação contábil ou consumo excessivo de capital de giro.

**Tendências históricas (4-10 anos):** Margem Bruta, ROE e FCF em queda sugerem que o moat está se deteriorando — penalidade no score.
