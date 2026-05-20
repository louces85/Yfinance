# CLAUDE.md — YFINANCE_REFACTOR

## Antes de começar qualquer tarefa

Leia **apenas o arquivo do brain relevante** para a tarefa. Não leia todos:

| Se a tarefa envolve... | Leia |
|------------------------|------|
| Arquitetura, fluxo de dados, classes, serviços, onde está o código | `src/brain/brain_architecture.md` |
| Fórmulas, cálculos, Score, BRank, Piotroski, Moat, zonas, limiares | `src/brain/brain_calculations.md` |
| Frontend, UI, colunas das tabelas, páginas, APIs externas | `src/brain/brain_frontend.md` |
| Filosofias de investimento (Barsi, Bazin, Graham, Buffett) | `src/brain/brain_overview.md` |

Se a tarefa abrange múltiplas áreas, leia os arquivos relevantes. Evite ler todos de uma vez.

## Estrutura do projeto

```
src/
├── frontend/index.html          ← SPA completo (~3800 linhas, JS vanilla)
├── backend/
│   ├── api_server.py            ← Flask REST + scheduler 30min
│   ├── config/rules.py          ← TODOS os thresholds (nunca magic numbers)
│   ├── repositories/stock_repository.py  ← acesso aos JSONs (sempre via repo)
│   ├── services/
│   │   ├── valuation_calculator.py  ← motor: 21 critérios + 3 scores
│   │   ├── decision_service.py      ← gera decision_stocks.json + BRank
│   │   └── portfolio_service.py     ← lê B3 XLS + unified_rank
│   └── data/
│       ├── decision_stocks.json     ← ~127 ações com unified_rank
│       ├── valuations.json          ← valuation completo por ticker
│       └── B3/Custodia*.xls         ← custódia exportada da B3
└── brain/                       ← documentação técnica (leia antes de explorar)
    ├── brain_architecture.md    ← arquitetura, fluxo, classes, serviços
    ├── brain_calculations.md    ← fórmulas, Score, BRank, Piotroski, Moat
    ├── brain_frontend.md        ← UI, colunas, páginas, APIs externas
    └── brain_overview.md        ← filosofias: Barsi, Bazin, Graham, Buffett
```

## Padrões do projeto

- **Persistência:** sempre atomic write via `stock_repository.py`. Nunca acesse JSONs diretamente nos services.
- **Thresholds:** sempre em `config/rules.py`. Nunca hardcode valores no código.
- **BRank (`unified_rank`):** calculado em `decision_service._calc_unified_rank()`. Fórmula em `brain_calculations.md` seção 7.9.
- **Carteira:** ações qualificadas usam `unified_rank` do `decision_stocks.json`. Ações FORA_CRITERIOS calculam via `_calc_unified_rank()` com dados do `forced_val`.
- **Python 3.8** — sem f-strings com expressões complexas, sem walrus operator (`:=`).
- **Frontend:** JS vanilla, sem framework. Funções de renderização: `renderPortfolioTable()`, `renderScreening()`. Sort via `data-col` (screening) e `data-ptcol` (carteira).

## Graphify MCP (knowledge graph do código)

O grafo está em `./graphify-out/graph.json` e é servido via MCP `graphify-ts`.

**Quando usar em vez de ler arquivos:**

| Situação | Ferramenta |
|----------|-----------|
| Entender estrutura geral do código | `community_overview` → `graph_stats` |
| Responder perguntas sobre o código | `retrieve` (linguagem natural) |
| Antes de alterar um arquivo/função | `impact` (blast radius) |
| Antes de abrir PR | `pr_impact` |
| Rastrear fluxo entre dois pontos | `call_chain` |

**Regra:** use `retrieve` antes de abrir arquivos para exploração.
Abra arquivos apenas para leitura detalhada ou edição.

**Grafo + Brain files são complementares:**
- Grafo (`graphify`) → onde está o código, quem chama quem, dependências estruturais
- Brain files (`src/brain/`) → lógica de negócio, fórmulas de investimento, filosofia
- Para qualquer tarefa: consulte o brain file relevante **e** use `retrieve`/`impact` antes de editar
