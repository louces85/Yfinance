# Prompt: Consolidação de Década — BRK Annual Meetings

## Como usar (Claude Code)

Cole este prompt diretamente no Claude Code e ajuste os caminhos na seção `ARQUIVOS`. O Claude vai ler os arquivos do disco automaticamente — não precisa colar conteúdo.

---

## O Prompt

```
## ARQUIVOS A LER

Leia os seguintes arquivos antes de qualquer análise:

- /home/fabiano/Documents/Yfinance/YFINANCE_REFACTOR/knowledge_base/analyzed/1994_BRK_Annual_Meeting_Analysis.md
- /home/fabiano/Documents/Yfinance/YFINANCE_REFACTOR/knowledge_base/analyzed/1995_BRK_Annual_Meeting_Analysis.md
- /home/fabiano/Documents/Yfinance/YFINANCE_REFACTOR/knowledge_base/analyzed/1996_BRK_Annual_Meeting_Analysis.md
- /home/fabiano/Documents/Yfinance/YFINANCE_REFACTOR/knowledge_base/analyzed/1997_BRK_Annual_Meeting_Analysis.md
- /home/fabiano/Documents/Yfinance/YFINANCE_REFACTOR/knowledge_base/analyzed/1998_BRK_Annual_Meeting_Analysis.md
- /home/fabiano/Documents/Yfinance/YFINANCE_REFACTOR/knowledge_base/analyzed/1999_BRK_Annual_Meeting_Analysis.md
- /home/fabiano/Documents/Yfinance/YFINANCE_REFACTOR/knowledge_base/analyzed/2000_BRK_Annual_Meeting_Analysis.md
- /home/fabiano/Documents/Yfinance/YFINANCE_REFACTOR/knowledge_base/analyzed/2001_BRK_Annual_Meeting_Analysis.md
- /home/fabiano/Documents/Yfinance/YFINANCE_REFACTOR/knowledge_base/analyzed/2002_BRK_Annual_Meeting_Analysis.md
- /home/fabiano/Documents/Yfinance/YFINANCE_REFACTOR/knowledge_base/analyzed/2003_BRK_Annual_Meeting_Analysis.md

Leia TODOS os arquivos acima antes de começar a escrever qualquer seção.

---

Sua tarefa é produzir um **Consolidado da Década 1994–2003** — não uma soma dos resumos, mas uma síntese de nível superior que identifique padrões, evolução e os princípios mais duráveis do período.

---

## INSTRUÇÕES DE ANÁLISE

**O que fazer antes de escrever:**
1. Leia todos os arquivos antes de escrever qualquer seção
2. Para cada princípio/ideia, anote em quantas reuniões ele apareceu
3. Identifique onde o pensamento de Buffett/Munger *evoluiu* ou *mudou* — isso é ouro
4. Separe o que é contexto histórico daquilo que é princípio atemporal
5. Para erros e crises: foque nos que geraram aprendizado explícito, não nos episódicos

---

## ESTRUTURA DO DOCUMENTO DE SAÍDA

### Cabeçalho
```
# 🧠 Berkshire Hathaway — Consolidado [ANO_INICIO]–[ANO_FIM]
**Reuniões analisadas:** [ANO_INICIO], [ANO_INICIO+1], ... [ANO_FIM]
**Densidade média do período:** [média das notas individuais]
**Reunião mais rica do período:** [ano + justificativa em 1 linha]
**Tema dominante da década:** [1 parágrafo]
```

---

### 1. 🔁 Princípios Repetidos com Alta Frequência
*Princípios mencionados em 5+ reuniões — o núcleo inabalável do pensamento*

Para cada princípio:
- **[Nome do princípio]**
  Frequência: [N]/[total] reuniões
  Tags: #tag1 #tag2
  Formulação mais precisa encontrada no período: [citar o ano e a formulação exata]
  Por que persiste: [1–2 frases sobre a durabilidade do princípio]
  Aplicação prática destilada: [a versão mais acionável, combinando as melhores formulações do período]

---

### 2. 📈 Evolução do Pensamento ao Longo da Década
*Onde Buffett/Munger refinaram, revisaram ou expandiram suas visões*

Para cada tema que evoluiu:
- **[Tema]**
  Como começou ([ANO_INICIO]–[ANO_INICIO+3]): [formulação inicial]
  Como ficou ([ANO_FIM-2]–[ANO_FIM]): [formulação final]
  O que provocou a mudança: [evento, erro ou insight identificado]
  Implicação para o investidor: [o que muda na prática]

---

### 3. 🏗️ Como Julgar um Bom Negócio — Critérios Consolidados
*Apenas critérios que apareceram em 3+ reuniões e/ou foram articulados com mais profundidade ao longo do período*

Para cada critério:
- **[Nome do critério]**
  Frequência: [N] reuniões
  Tags: #tag1 #tag2
  Formulação consolidada: [melhor síntese das múltiplas formulações]
  Exemplo ou caso concreto mais citado no período: [empresa/situação + ano]
  Red flag oposta: [o que NÃO ter no negócio]

---

### 4. 👔 Qualidade de Gestão — Padrões da Década
*Consolidação dos critérios de avaliação de management mais recorrentes*

Para cada critério:
- **[Critério]**
  Frequência: [N] reuniões
  Formulação consolidada: [melhor síntese]
  Gestor citado como exemplo positivo mais frequente: [nome + empresa]
  Sinal de alerta mais citado: [comportamento negativo específico]

---

### 5. 📊 Valuation — Método Consolidado da Década
*Como o framework de valuation de Buffett/Munger se expressou e evoluiu neste período*

- Método central (VPL dos fluxos futuros): [formulação mais completa encontrada no período]
- Taxa de desconto usada/referenciada: [como variou com o ambiente de juros da época]
- Múltiplos e atalhos aceitáveis: [o que usavam como filtro rápido]
- Armadilhas de valuation mais citadas: [lista numerada]
- Posição sobre value vs. growth: [como articularam no período]

---

### 6. 📅 Quando Comprar e Quando Não Comprar — Regras Consolidadas

#### ✅ Compre quando: (apenas regras com 3+ ocorrências)
- **[Regra]** — [N] reuniões — Tags: #tag
  Raciocínio consolidado: [melhor formulação do período]

#### ❌ Não compre quando: (apenas regras com 3+ ocorrências)
- **[Regra]** — [N] reuniões — Tags: #tag
  Raciocínio consolidado: [melhor formulação do período]

#### 🔒 Nunca venda quando:
- [Regras consolidadas com contexto do período]

---

### 7. 🌪️ Comportamento em Crises — Padrões da Década
*Este período incluiu [listar crises/eventos relevantes — Black Monday aftermath, dot-com, 9/11 etc.]*

Para cada tipo de crise/evento:
- **[Tipo de crise]**
  Como Buffett/Munger responderam na prática (não apenas o que disseram): [o que fizeram]
  Princípio subjacente: [a regra que guiou a ação]
  Contraste com o comportamento médio do mercado: [o que os outros fizeram]
  Aplicação atual: [como usar isso em situação análoga]

---

### 8. 🧠 Modelos Mentais — Os Mais Duráveis da Década
*Apenas os que apareceram em 3+ reuniões e/ou foram elaborados com profundidade crescente*

Para cada modelo:
- **[Nome do modelo mental]**
  Frequência: [N] reuniões
  Tags: #tag1 #tag2
  Formulação mais completa: [melhor versão encontrada no período, com ano]
  Como se aplica ao investimento: [versão prática e direta]
  Relação com outros modelos: [como se conecta com outros da lista]

---

### 9. ❌ Erros e Lições — Padrões da Década
*Erros recorrentes ou que geraram elaboração ao longo de múltiplas reuniões*

Para cada padrão de erro:
- **[Nome/Categoria do erro]**
  Casos citados: [lista com ano]
  Tipo dominante: Comissão / Omissão / Ambos
  Tags: #tag
  Padrão identificado: [o que os erros têm em comum]
  Lição destilada: [formulação mais precisa extraída do período]
  Como evitar: [regra prática]

---

### 10. ⚠️ Riscos Sistêmicos Identificados no Período
*Riscos que Buffett/Munger alertaram repetidamente — não eventos específicos, mas classes de risco*

Para cada classe de risco:
- **[Nome do risco]**
  Frequência: [N] reuniões
  Tags: #tag
  Por que é perigoso: [formulação consolidada]
  Contexto histórico do período: [o que estava acontecendo que tornava esse risco relevante]
  Como evitar: [regra prática]

---

### 11. 🔥 As 10 Melhores Citações da Década
*Seleção das citações de maior densidade — priorizando as que sintetizam princípios duráveis, não apenas as mais famosas*

Para cada citação:
> "[Citação exata]"
> — [Autor], [Ano]

Tags: #tag1 #tag2
Por que está entre as 10: [o que a torna excepcional — não apenas o conteúdo, mas o grau de síntese]
Princípio que encapsula: [ligação com a seção correspondente]

---

### 12. 🧩 Os 3 Clusters Temáticos Dominantes da Década
*Os temas que mais organizaram o pensamento de Buffett/Munger neste período de 10 anos*

Para cada cluster:
- **[Nome do Cluster]**
  Reuniões onde foi central: [lista de anos]
  Ideia-âncora: [a ideia central que une o cluster]
  Ideias satélite: [as que orbitam em torno dela]
  Por que este tema dominou este período: [contexto histórico que o tornou urgente]
  Como o pensamento se desenvolveu ao longo da década: [linha narrativa de evolução]

---

### 13. ❓ As 10 Perguntas Fundamentais da Década
*Não as perguntas feitas na reunião — as perguntas que o investidor deveria fazer para si mesmo, destiladas do período*

Organizadas por categoria (negócio, gestão, valuation, risco):

**Sobre o negócio:**
- [ ] [Pergunta] — *Contexto: por que essa pergunta emergiu neste período?*

**Sobre a gestão:**
- [ ] [Pergunta]

**Sobre valuation:**
- [ ] [Pergunta]

**Sobre risco:**
- [ ] [Pergunta]

---

### 14. 🎯 O Que Fazer Diferente — As 10 Ações Práticas da Década
*Não repetir ações já listadas nos anos individuais — sintetizar e priorizar as mais acionáveis e duráveis*

1. [Ação] — *Frequência: apareceu em [N] reuniões*
2. ...

---

### 15. 📊 Meta-análise da Década

- **Densidade média:** [média das notas individuais] / 10
- **Distribuição de densidade:** [anos com nota 9–10 / 7–8 / abaixo de 7]
- **Reunião mais rica:** [ano] — [justificativa em 2 frases]
- **Reunião menos densa:** [ano] — [o que faltou]
- **Tema que mais evoluiu no período:** [tema + como evoluiu]
- **Tema mais estável (sem evolução):** [tema + por que não mudou]
- **O que Buffett/Munger ainda não articulavam bem no início do período e articulavam bem no final:** [insight sobre a evolução do pensamento]
- **O que mudou no contexto histórico e como isso afetou o pensamento:** [análise do impacto do ambiente nos princípios]
- **Lacunas do período:** [o que eles não discutiram que seria relevante]

---

### 16. 🧠 Interpretação Pessoal *(deixe em branco — para preenchimento posterior)*

- Qual princípio deste período eu mais violo no meu processo atual?
- Qual insight da evolução do pensamento deles mais me surpreendeu?
- O que mudaria no meu checklist de análise após esta consolidação?
- Qual o maior erro que evitaria se tivesse internalizado estes princípios antes?

---

## INSTRUÇÕES DE FORMATO E QUALIDADE

**Tom e estilo:**
- Escreva em português (Brasil)
- Direto, denso, sem introduções longas
- Priorize formulações que podem ser aplicadas, não apenas descritas
- Quando citar uma formulação de uma reunião específica, sempre indique o ano

**O que NÃO fazer:**
- Não repetir o que está nos arquivos individuais sem síntese
- Não listar princípios de forma mecânica — selecione pelos de maior recorrência e durabilidade
- Não incluir eventos históricos que não geraram princípio aplicável
- Não usar linguagem vaga ("é importante considerar...") — seja preciso

**Critério de corte:**
- Princípios em 1–2 reuniões: descarte (a não ser que sejam excepcionalmente densos)
- Princípios em 3–4 reuniões: inclua com nota de frequência
- Princípios em 5+ reuniões: destaque como "núcleo inabalável"

**Sobre citações:**
- Selecione apenas as que sintetizam princípios duráveis
- Prefira as menos conhecidas às mais famosas, se igualmente densas
- Sempre inclua o ano

**Extensão esperada:** 4.000–6.000 palavras
```

---

## Como adaptar para outros períodos

Troque apenas a lista de caminhos na seção `## ARQUIVOS A LER` e os anos no texto do prompt.

**Blocos sugeridos:**

**Período 1 — 1994–2003** (atual, já configurado acima)

**Período 2 — 2004–2013** (quando tiver os arquivos):
```
- .../analyzed/2004_BRK_Annual_Meeting_Analysis.md
- .../analyzed/2005_BRK_Annual_Meeting_Analysis.md
...até 2013
```
Mudar no texto: "Consolidado da Década 2004–2013"

**Período 3 — 2014–2024** (quando tiver os arquivos):
```
- .../analyzed/2014_BRK_Annual_Meeting_Analysis.md
...até 2024
```
Mudar no texto: "Consolidado da Década 2014–2024"

**Consolidado Final — dos 3 períodos:**
Usar os 3 arquivos de consolidado de década como input, com prompt adaptado para síntese de 30 anos.
