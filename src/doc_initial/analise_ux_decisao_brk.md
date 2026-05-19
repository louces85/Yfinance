# Análise Crítica 10/10 — UX e Tomada de Decisão no YFINANCE_REFACTOR

## Contexto

Pedido: auditar a aplicação sob duplo ponto de vista — UX sênior + investidor B3 experiente — cruzando a realidade do código atual com os princípios consolidados do documento Berkshire 1994–2003.

**Estado atual (resumo):**
- Motor de decisão robusto: 21 critérios binários + 3 scores (Piotroski, Moat, BRank) sintetizados em `unified_rank` 0–100.
- UI rica: 4 páginas (Screening, Carteira, Favoritos, Radar), modal de ticker com ~61 tooltips, 10 cards de preço, gráfico com VI (DCF), peers setoriais, medalhas 🥇🥈🥉 e Seal Buffett ⭐.
- Filosofias integradas: Barsi ~100%, Bazin ~90%, Graham ~80%, Buffett ~60%.

**Diagnóstico em uma frase:** o app é excelente a identificar **"resultados passados bons" a preço razoável** (Graham/Barsi/Bazin), mas ainda não operacionaliza o núcleo do método Buffett-Munger maduro: **custo de oportunidade como filtro primário, círculo de competência explícito, moat qualitativo, previsibilidade de fluxos em 10–20 anos, risco de perda permanente, inversão, e erros de omissão**. É a exata transição Graham → Munger descrita na seção 2 do doc Berkshire — que o app ainda não completou.

---

## Diagnóstico — O que falta, por ordem de gravidade

Cada item abaixo é amarrado a um princípio específico do doc Berkshire e a um arquivo/função existente no código.

### TIER S — Mudanças estruturais (alto impacto, alta durabilidade)

#### S1. Custo de oportunidade como filtro primário — hoje ausente
- **Princípio Berkshire:** §1 e §8 — "custo de oportunidade é a única pergunta válida de alocação" (10/10 reuniões).
- **Realidade hoje:** `decision_service._calc_unified_rank()` produz ranking **absoluto** 0–100. O app nunca força a pergunta "prefiro isto a comprar mais da minha régua?".
- **Gap:** não há "posição de referência" configurável pelo usuário (ex: ITSA4 ou BBAS3). Não há comparação automática contra Selic real (pós-impostos/inflação) nem contra o IBOV. `market_data.json` já coleta IBOV/USD/S&P/OURO mas não entra em nenhuma decisão.
- **Proposta:**
  1. Campo no perfil do usuário: **"posição de referência"** (1–3 tickers que o usuário entende profundamente e poderia comprar mais).
  2. Em todo card de ticker: badge "⚖️ vs régua" mostrando diferencial de retorno esperado vs a referência (DCF/preço atual − DCF/preço atual da referência).
  3. Dashboard: mostrar **Selic real** (Selic − IPCA − IR) como hurdle mínimo — qualquer ticker com retorno esperado inferior ao hurdle vira CARO automaticamente, independente de zona.
- **Arquivos:** `backend/config/rules.py` (novo campo `REFERENCE_POSITION`), `backend/services/decision_service.py` (nova função `_calc_opportunity_spread()`), `frontend/index.html` (novo card "vs Régua" no modal).

#### S2. Círculo de competência explícito e círculo de incompetência — hoje inexistente
- **Princípio Berkshire:** §1 — "se você tem dúvidas se algo está no círculo, não está" (10/10 reuniões).
- **Realidade hoje:** app sugere qualquer um dos ~615 tickers coletados. Setor do ticker existe em `sector`/`segmento` mas não é usado como filtro personalizado.
- **Gap:** o usuário recebe recomendação COMPRA_FORTE em setor que ele não entende (semicondutores, fintechs, biotecs) — violação direta do princípio fundador.
- **Proposta:**
  1. Tela **"Meu Círculo"** — usuário marca setores/segmentos como *dentro*, *aprendendo* ou *fora*.
  2. Default do Screening: ocultar setores "fora". Tickers "aprendendo" ganham badge 📘.
  3. Tickers "fora" não disparam alertas no Radar nem entram em recomendações AUMENTAR/COMPRAR_MAIS na Carteira.
  4. Pergunta de verificação antes de cada nova compra: "Você consegue escrever em uma frase onde este negócio estará em 10 anos?" (§13 Perguntas Fundamentais).
- **Arquivos:** `backend/config/rules.py` (novo `CIRCLE_OF_COMPETENCE`), nova view `frontend/index.html` "Perfil", filtro aplicado em `decision_service` e `portfolio_service`.

#### S3. Moat qualitativo — hoje mede resultados, não fontes
- **Princípio Berkshire:** §3 — "moat é o que transforma previsibilidade em convicção" (10/10). Critério: "se um gestor medíocre assumir amanhã, o negócio continua lucrativo?"
- **Realidade hoje:** `buffett_moat_score` (0–10) avalia **consequências** do moat (MB≥40%, ROE≥20%, ML≥20%, ROIC≥15%, FCF/L≥80%, crescimento) — não as **fontes** (marca, switching cost, network effect, escala, IP, localização).
- **Gap crítico:** uma empresa pode ter margens altas hoje por posição cíclica favorável (commodities, construção em boom) e zero moat real. O app dá Seal Buffett ⭐ para casos assim.
- **Proposta:**
  1. **Card "Fontes de Moat"** no modal, 5 dimensões binárias (Marca / Switching / Escala / Network / IP-Localização) — preenchível pelo usuário ou extraído via LLM do knowledge base (PDFs DFP/ITR + transcrições BRK em `knowledge_base/`).
  2. **Teste de adversidade:** seção "Resistência" mostrando pior drawdown de margem EBIT e de ROE nos últimos 10 anos (dados já existem em `financials_history.json`). Moat real mostra-se em crise — AmEx 1964, Coca 1985, GEICO 1976 (§3).
  3. Seal Buffett ⭐ só dispara se ao menos **1 fonte de moat** estiver marcada **E** teste de adversidade passar (drawdown ML < 40%).
- **Arquivos:** `frontend/index.html` (novo card + input), novo JSON `qualitative_moat.json` por ticker, gate adicional em `valuation_calculator` para o Seal.

#### S4. Risco = probabilidade de perda permanente, não volatilidade — hoje subespecificado
- **Princípio Berkshire:** §1 — "beta é loucura. Risco é perda permanente" (9/10).
- **Realidade hoje:** DL/PL≤1, DL/EBITDA≤3, passivo/ativo≤65%, liquidez corrente≥2 são todos **estáticos** — passam ou falham no estado atual.
- **Gap:** não há teste "se EBITDA cair 50%, a empresa paga os juros?" (stress dinâmico), nem cobertura de juros (EBIT/Juros), nem Altman Z-Score, nem "distance to default".
- **Proposta:**
  1. Novo critério #22: **Cobertura de Juros** (EBIT/Juros ≥ 5 ideal, ≥ 3 ok). Peso 2.0. Dados já existem.
  2. Novo componente no BRank: **stress_n** = sobrevivência em cenário EBIT −50% (penalidade multiplicativa se fail, tipo gate).
  3. Card "Risco de Perda Permanente" no modal: 3 indicadores visuais — Cobertura juros, Stress EBIT, Refinanciamento (% dívida vencendo em 12m se disponível).
  4. Remover qualquer métrica de volatilidade que eventualmente seja adicionada (nunca usar beta).
- **Arquivos:** `backend/config/rules.py` (thresholds), `backend/services/valuation_calculator.py` (novo critério), `decision_service._calc_unified_rank()` (gate).

#### S5. Previsibilidade em 10–20 anos — hoje genérica no DCF
- **Princípio Berkshire:** §3 — "coupons futuros" + "negócios de mudança lenta são superiores" (10/10). §6 — "9 em 10 vezes passamos quando vemos muita mudança vindo".
- **Realidade hoje:** DCF usa CAGR histórico × caps por moat + terminal 3.5%. Mesma fórmula para Coca brasileira (ABEV3) e para vale de commodity cíclica.
- **Gap:** não diferencia negócio previsível (utility, seguro, consumo básico) de cíclico (construção, siderurgia, aviação). Erro estrutural.
- **Proposta:**
  1. **Score de previsibilidade** (0–10) baseado em: volatilidade histórica de margem EBIT (10a), volatilidade de receita, tipo setorial (tabela em `rules.py`), consistência do dividendo.
  2. Cap dinâmico no DCF: empresas com previsibilidade <5 ganham desconto de 25% no VI calculado (margem de segurança proporcional à incerteza, §1).
  3. Badge visual no ticker: 🔮 Previsível / 🎲 Cíclico / ⚡ Mudança rápida. Mudança rápida entra em "círculo de incompetência" automaticamente para usuários que marcaram "evitar disrupção".
- **Arquivos:** `backend/services/valuation_calculator.py` (função `_calc_predictability()`), ajuste no DCF, badges em `frontend/index.html`.

---

### TIER A — Melhorias de alto ROI (médio esforço, efeito imediato)

#### A1. Histórico temporal de BRank / zona / score por ticker
- **Princípio:** §1 — "tempo é amigo do negócio excelente" e §9 — reconhecer erros de omissão.
- **Gap hoje:** um ticker pode sair de BRank 75 para 45 overnight sem nenhum registro. Impossível saber "quando o app sugeriu COMPRA_FORTE e quanto custou não agir".
- **Proposta:** persistir snapshot diário de (ticker, BRank, zone, score, price_now) em SQLite leve ou JSON append-only. Gráfico temporal de 12 meses no modal. Alerta "quedas/subidas significativas ≥15 pontos de BRank".
- **Arquivos:** novo `backend/data/history/brank_history.db`, novo endpoint `/api/ticker/<t>/history`, gráfico no modal.

#### A2. Diário de Omissões — o erro invisível da §9
- **Princípio:** §9 — "os erros mais extremos são de omissão. Não aparecem nos nossos números — aparecem no custo de oportunidade" (Munger, 2001).
- **Proposta:** sempre que o app marca um ticker como COMPRA_FORTE por 30 dias consecutivos e o usuário não o adiciona à carteira, registra automaticamente em "omissões". Relatório mensal mostra performance hipotética (se tivesse comprado no dia da primeira marcação, retorno hoje). Torna o erro invisível — visível.
- **Arquivos:** novo `backend/services/omissions_tracker.py`, nova view `frontend/index.html` "Diário de Omissões".

#### A3. Lista de Compra Antecipada (Fat Pitch Playbook) — §6 / §7
- **Princípio:** §7 — "preparamos lista de compra antecipada para agir sem análise emocional durante o caos".
- **Gap hoje:** Radar é isolado e só mira preço. Não considera "o moat sobreviveu? o negócio mudou?".
- **Proposta:**
  1. Por ticker, o usuário define 2 preços-alvo de crise: −30% (normal) e −50% (crash). Preenchidos automaticamente com sugestão baseada em VI × margem de segurança 30%/50%.
  2. Alerta composto: dispara só quando (preço atingido) **E** (moat intacto: Moat≥7 nos últimos 6m) **E** (alavancagem segura: DL/EBITDA≤3). Diferencia **"vendedor forçado"** (oportunidade) de **"negócio destruído"** (armadilha) — §7.
- **Arquivos:** extensão de `radar.json`, lógica composta em `backend/services/radar_service.py` (novo).

#### A4. Carteira com contexto temporal + racional de compra
- **Princípio:** §1, §9 — "paciência ilimitada"; §4 — "o relatório ideal descreve o que aconteceu".
- **Gap hoje:** carteira mostra -15% sem dizer desde quando. Sem data de compra, holding period, nem nota sobre por que comprou.
- **Proposta:**
  1. Extrair data de aquisição do XLS B3 (já existe no arquivo, não usado).
  2. Campo de texto livre **"Tese de compra"** por posição — obrigatório preencher em 1 frase a primeira vez que cada ticker aparece. Revisão anual automática solicita reavaliação.
  3. Coluna "Holding period" na tabela. Ordenação por holding permite ver quem está há mais tempo sem revisão.
- **Arquivos:** `backend/services/portfolio_service.py`, novo `backend/data/portfolio_notes.json`.

#### A5. Drill-down visual do BRank — "por quê?"
- **Princípio:** §4 — honestidade na comunicação; §10 — ajustes contábeis explícitos.
- **Gap:** BRank de 72 — qual componente puxou? Hoje precisa abrir modal, ler 21 critérios, somar manualmente.
- **Proposta:** card "Composição do BRank" com barra empilhada mostrando contribuição exata de cada fator (score, moat, piotroski, dy, fcf, payout). Componentes negativos (gates) em vermelho com delta. Hover revela fórmula exata.
- **Arquivos:** nova função em `frontend/index.html` `renderBRankBreakdown()`.

#### A6. Comparativo side-by-side
- **Princípio:** §1 — "preferíamos este negócio a comprar mais da referência?".
- **Proposta:** botão "⚖️ Comparar" no modal, abre segunda coluna. Todos os 21 critérios, scores, cards, gráfico de preço sobrepostos. Resposta direta à pergunta-mestra de Buffett.
- **Arquivos:** `frontend/index.html` (nova view em modal 2-col).

---

### TIER B — Correções pontuais de alta precisão

#### B1. Ajuste contábil para opções de ações e pensão (§10)
- **Princípio Berkshire:** §10 — "EBITDA = bullshit earnings". "Subtrair custo real de opções emitidas; usar máximo 6–7% real para retorno de fundo de pensão".
- **Hoje:** app já evita EBITDA (✅). Mas lucro reportado **não é ajustado** por opções emitidas nem por premissas de pensão otimistas.
- **Proposta:** novo campo `adjusted_earnings` = lucro − (1/3 × strike × opções emitidas / 10) − ajuste de pensão se disponível. Usar em P/L ajustado e DCF.

#### B2. Separação capital-light vs capital-heavy (§3)
- **Princípio:** §3 — hierarquia See's Candy vs FlightSafety vs companhias aéreas.
- **Proposta:** classificar cada ticker em uma das 3 categorias usando (capex/lucro 10a médio) + (capex/receita 10a médio). Exibir badge no modal. Ticker capital-heavy exige ROIC ≥ 2× WACC para entrar em COMPRA_FORTE.

#### B3. Medalhas com critério visível
- **Gap UX:** usuário vê 🥇 e não sabe o porquê. Tooltip existe mas é textual denso.
- **Proposta:** hover mostra mini-card "Atingiu: P/L 8.2 ≤ 15 ✓, P/VP 0.9 ≤ 1.5 ✓, DY 7.1% ≥ 6% ✓, preço ≤ VPA ✓".

#### B4. Pensamento de segundo nível no modal (§8)
- **Princípio:** §8 — "o mercado está errando em que premissa?".
- **Proposta:** campo de texto livre "Premissa do mercado que esta tese desafia" na tese de compra da Carteira. Não automatizado — força reflexão.

#### B5. Notificações de mudanças estruturais
- **Princípio:** §4 — CEO que não comunica erros é perigoso.
- **Proposta:** detectar (a) queda de BRank >15 pontos em 30d, (b) saída da zona COMPRA para CARO, (c) novo flag de "resultado não-recorrente" detectado pela Fase 3.11 do moat, (d) entrada em zona AVALIAR_VENDA. Centralizar em página "Alertas" com timeline.

#### B6. Benchmark visível no dashboard
- **Princípio:** §2 — "retornos de 15% são matematicamente impossíveis no agregado" (§2 Evolução).
- **Proposta:** card permanente no topo: "Selic real YTD: X%" · "IBOV YTD: Y%" · "Sua carteira YTD: Z%" — força calibração aritmética de expectativas (§2).

---

### TIER C — Longo prazo (alta ambição, alta complexidade)

#### C1. Pipeline LLM sobre knowledge_base
- **Observação:** `knowledge_base/` já tem PDFs de DFP/ITR (ALLD3, GRND3, KEPL3, VULC3), transcrições BRK 1994–2011 e prompts prontos — **sem pipeline de extração**.
- **Proposta (Claude API com prompt caching):** extrator mensal que lê novos DFP/ITR e produz estruturado: (1) qualidade de gestão (honestidade em admitir erros, coerência na comunicação), (2) sinais de alocação de capital (M&A, buybacks a preço atrativo), (3) fontes de moat citadas, (4) riscos reconhecidos. Alimenta `qualitative_moat.json` e novo `management_quality.json`.
- **Reuso:** `anthropic` SDK com caching reduz custo em ~90% para PDFs recorrentes.

#### C2. Risco de concentração setorial na carteira
- **Princípio:** §8 — efeito Lollapalooza, correlações escondidas.
- **Proposta:** heatmap setor × peso da carteira. Alerta se >30% em um setor. Teste "se setor X cair 40%, qual o impacto?".

#### C3. Wizard de compra guiado por checklist Buffett
- **Inspiração:** §13 — "10 perguntas fundamentais da década".
- **Proposta:** antes de qualquer adição à carteira, app apresenta checklist de 10 perguntas (círculo, previsibilidade 10a, moat ativo, gestão, valuation, alavancagem, etc.) que precisam ser respondidas em texto. Resposta é salva como racional de compra (A4).

---

## Resumo visual da priorização

| # | Melhoria | Princípio BRK | Esforço | Impacto |
|---|----------|---------------|---------|---------|
| S1 | Posição de referência + custo de oportunidade | §1, §8 | M | ★★★★★ |
| S2 | Círculo de competência configurável | §1 | S | ★★★★★ |
| S3 | Moat qualitativo + teste de adversidade | §3 | L | ★★★★★ |
| S4 | Risco de perda permanente (stress + cobertura juros) | §1 | M | ★★★★★ |
| S5 | Score de previsibilidade 10a | §3, §6 | M | ★★★★☆ |
| A1 | Histórico temporal de BRank/zona | §9 | M | ★★★★☆ |
| A2 | Diário de omissões automático | §9 | M | ★★★★☆ |
| A3 | Fat Pitch Playbook composto | §7 | S | ★★★★☆ |
| A4 | Data de compra + tese + holding period | §1, §9 | S | ★★★★☆ |
| A5 | Drill-down visual do BRank | §4 | S | ★★★☆☆ |
| A6 | Side-by-side de tickers | §1 | M | ★★★☆☆ |
| B1–B6 | Ajustes pontuais (opções, capital-light, medalhas, etc.) | §10, §3, §4 | S–M | ★★★☆☆ |
| C1 | Pipeline LLM no knowledge_base | §3, §4 | L | ★★★★☆ |
| C2 | Risco de concentração setorial | §8 | M | ★★★☆☆ |
| C3 | Wizard de compra com checklist | §13 | M | ★★★☆☆ |

Esforço: S=pequeno (≤1 dia), M=médio (2–5 dias), L=grande (>1 semana).

---

## Arquivos-chave que seriam tocados (quando implementar)

- [backend/config/rules.py](YFINANCE_REFACTOR/backend/config/rules.py) — novos thresholds (cobertura juros, círculo, referência, previsibilidade setorial)
- [backend/services/valuation_calculator.py](YFINANCE_REFACTOR/backend/services/valuation_calculator.py) — novo critério #22, score de previsibilidade, classificação capital-light
- [backend/services/decision_service.py](YFINANCE_REFACTOR/backend/services/decision_service.py) — nova função `_calc_opportunity_spread()`, novo gate stress no BRank
- [backend/services/portfolio_service.py](YFINANCE_REFACTOR/backend/services/portfolio_service.py) — data de compra, holding period, tese
- [backend/repositories/stock_repository.py](YFINANCE_REFACTOR/backend/repositories/stock_repository.py) — novos JSONs (`qualitative_moat.json`, `portfolio_notes.json`, `omissions_log.json`, `brank_history.db`)
- [frontend/index.html](YFINANCE_REFACTOR/frontend/index.html) — nova view "Meu Perfil", cards (Moat Qualitativo, Risco Permanente, vs Régua, Breakdown BRank), comparador side-by-side, timeline
- [brain/brain_calculations.md](YFINANCE_REFACTOR/brain/brain_calculations.md) e [brain/brain_frontend.md](YFINANCE_REFACTOR/brain/brain_frontend.md) — documentação das novas regras

---

## Verificação (quando implementar)

Este plano é **apenas de análise** — ainda não há implementação. Para validar as mudanças propostas, a cada tier implementado:

1. Rodar backend (`api_server.py`) e abrir o frontend, navegar pelas 4 páginas principais.
2. Escolher 5 tickers de perfis distintos (banco, utility, consumo, cíclico, commodity) e verificar se as novas visualizações e gates disparam corretamente.
3. Comparar BRank antes/depois em amostra de 20 tickers — garantir que mudanças não corrompem ranking existente (nenhum ticker muda mais de 20 pontos sem explicação pelo novo gate).
4. Para o pipeline LLM (C1), validar com 2 DFPs conhecidos que a extração bate com leitura humana.

---

## Próximo passo

Este plano lista 15+ melhorias. **Antes de implementar qualquer coisa**, precisamos decidir o escopo:

- **Opção A (recomendada):** atacar TIER S completo primeiro (S1–S5). É a transição Graham → Munger estrutural — cinco mudanças que sozinhas elevam o app a 9/10 no método Buffett. ~2 semanas.
- **Opção B:** começar por quick wins de TIER A (A3, A4, A5) para ganhar tração de UX em dias. ~3–5 dias.
- **Opção C:** abordagem híbrida — S2 (círculo) + S4 (stress) + A4 (tese) em uma primeira leva, depois o restante.
- **Opção D:** só um item específico que o usuário priorize.
