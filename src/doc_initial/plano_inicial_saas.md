# Plano Inicial: Transformar YFINANCE_REFACTOR em SaaS B2C

## Contexto

O produto atual é um screener sofisticado de ações B3 com scoring multi-metodologia (Barsi, Bazin, Graham, Lynch, Buffett), análise de moat, Piotroski F-Score e integração de portfólio. O algoritmo de 21 critérios ponderados **é o diferencial competitivo real** — não existe combinação equivalente no mercado brasileiro (StatusInvest, Investidor10, Fundamentus são básicos).

**O que já está pronto (≈70%):** algoritmo core, engine de scoring, UI, pipeline de dados, integração yfinance/StatusInvest, análise de portfólio, 4.179 linhas de Python funcional.

**O que falta (≈30%):** infraestrutura para múltiplos usuários, autenticação, banco de dados, deployment, pagamento, compliance legal.

---

## Diagnóstico das Lacunas

### Crítico (bloqueia o lançamento)

| Lacuna | Estado Atual | Impacto |
|--------|-------------|---------|
| Autenticação | Zero — todos os endpoints abertos | Qualquer pessoa vê dados de portfólio de qualquer usuário |
| Multi-tenância | Não existe — arquitetura single-user | Impossível ter múltiplos usuários com portfólios separados |
| Banco de dados | JSON sem file locking | Race condition entre scheduler e leituras; corrupção de dados em concurrent access |
| Deployment | Nenhum config (sem requirements.txt, Dockerfile, .env) | Não dá para fazer deploy em nenhuma plataforma cloud |
| Compliance CVM | Zero disclaimers | Risco regulatório: o produto gera sinais "COMPRA_FORTE" sem aviso de que não é recomendação |

### Alto (necessário antes de abrir para pagantes)

| Lacuna | Estado Atual | Impacto |
|--------|-------------|---------|
| Scheduler resiliente | Daemon thread que morre com o processo | Sem restart automático em produção |
| Rate limiting | Ausente | Abuse, bots, scraping da própria API |
| CORS | Ausente | Frontend em domínio separado não funciona |
| Logging estruturado | print() apenas | Impossível debugar em produção |
| Upload de arquivo B3 por usuário | Caminho hardcoded no filesystem | Portfólio pessoal não pode ser per-user |
| Payment | Não existe | Sem monetização |

### Médio (pode vir após lançamento)

- Greenblatt Magic Formula (dados já existem, falta cálculo)
- Alertas Telegram (planejado em `ideias.txt`, não implementado)
- Mobile responsivo
- Landing page

---

## Arquitetura Alvo

### Modelo de dados: Compartilhado vs. Por-usuário

```
Dados de mercado (COMPARTILHADOS — um fetch serve todos):
  screener_results, stock_prices, stock_history,
  valuations, financials_history, sectors, validity

Dados do usuário (POR-USUÁRIO):
  users, portfolio_snapshots, watchlists, alert_preferences
```

Isso é uma **vantagem arquitetural**: o custo de scraping (StatusInvest, yfinance) não escala com usuários. Um job a cada 30min atende 1 ou 10.000 usuários igualmente.

### Stack de produção recomendada

```
Backend:    Flask + Flask-JWT-Extended (manter Flask)
Database:   PostgreSQL (Railway free tier: 500MB grátis)
Jobs:       APScheduler persistente (substituir daemon thread)
Deploy:     Railway ou Render
Auth:       JWT (access token 15min + refresh token 7d)
Files:      Supabase Storage (upload XLS do portfólio por usuário)
Payment:    Pagar.me (PIX + cartão, nativo brasileiro)
Email:      Resend (free tier generoso)
```

### Migração JSON → PostgreSQL

O arquivo `stock_repository.py` é a camada de acesso a dados centralizada — **toda lógica de negócio já passa por ele**. A migração é trocar as implementações `_load()`/`_save()` por queries PostgreSQL sem tocar nos services. A interface pública do repositório permanece idêntica.

---

## Modelo de Negócio

### Freemium

| Tier | Preço | Acesso |
|------|-------|--------|
| Grátis | R$0 | Top 10 do screener, sem portfólio, sem Buffett |
| Pro | R$39/mês ou R$390/ano | Screener completo, portfólio B3, análise Buffett, Piotroski, alertas |

**Posicionamento:** "O único screener brasileiro que combina Barsi + Graham + Buffett num score único"

**Concorrentes e gap:**
- StatusInvest: mostra os indicadores, não toma decisão
- Investidor10: filtros básicos, sem metodologia combinada
- **Este produto:** ranking metodológico com score ponderado, sinal de acumulação Barsi, moat Buffett, Piotroski — tudo junto numa visão

---

## Compliance Legal (não negociável)

1. **Disclaimer permanente e visível:** "Esta ferramenta é educacional e não constitui recomendação de investimento. Os resultados não garantem rentabilidade futura. Consulte um assessor de investimentos habilitado."
2. **Substituir linguagem de "COMPRA_FORTE"** por "Forte Alinhamento Técnico" — evitar parecer recomendação de investimento
3. **Política de Privacidade + Termos de Uso** (obrigatório LGPD)
4. **CNPJ** (MEI ou ME) para emissão de nota fiscal e recebimento via Pagar.me
5. **Dados sensíveis:** arquivos XLS B3 contêm dados financeiros — criptografar em repouso, deletar após processamento

---

## Roadmap em 3 Fases

### Fase 1 — Infraestrutura (4–5 semanas)
*Objetivo: tornar a aplicação deployável e multi-usuário*

1. `requirements.txt` com versões fixadas
2. `Dockerfile` + `docker-compose.yml` (app + postgres)
3. Migrar `stock_repository.py`: JSON → PostgreSQL
   - Tabelas de mercado (compartilhadas): `screener_results`, `stock_prices`, `valuations`, `stock_history`, `sectors`
   - Tabelas de usuário: `users`, `portfolio_files`, `watchlists`
4. Autenticação JWT: `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/refresh`
5. Middleware de auth nas rotas sensíveis (`/api/portfolio`, valuation detalhada)
6. Substituir daemon thread por APScheduler com job store no PostgreSQL
7. CORS configurado corretamente
8. Variáveis de ambiente via `.env`

**Arquivos críticos:**
- `backend/repositories/stock_repository.py` — swap JSON → Postgres
- `backend/api_server.py` — adicionar auth, CORS, APScheduler
- Novos: `backend/models/user.py`, `backend/auth/routes.py`, `backend/db/migrations/`

### Fase 2 — Produto (4–5 semanas)
*Objetivo: primeiro usuário pagante possível*

1. Upload de arquivo B3 por usuário (multipart → Supabase Storage)
2. Feature gating: Freemium vs. Pro (decorator `@require_plan('pro')`)
3. Integração Pagar.me (webhook de pagamento → atualiza plano no banco)
4. Disclaimers legais na UI + Termos e Política de Privacidade
5. CNPJ e conta jurídica configurados
6. Deploy em Railway com domínio customizado + HTTPS
7. Alertas por email (top 5 sinais diários para usuários Pro)

### Fase 3 — Crescimento (ongoing)
*Objetivo: reduzir churn, aumentar conversão*

1. Alertas Telegram (bot já planejado em `ideias.txt`)
2. Landing page (co-fundador não-técnico pode liderar)
3. Greenblatt Magic Formula (os dados já existem, é só calcular)
4. Consistência de dividendos (5 anos consecutivos — Barsi flag)
5. Mobile responsivo
6. Onboarding guiado

---

## Riscos

| Risco | Probabilidade | Mitigação |
|-------|--------------|-----------|
| StatusInvest bloqueia scraping em escala | Alta | Rate limiting + cache 7 dias + BRAPI como fallback |
| yfinance rate limit | Baixa | Dados compartilhados — um fetch serve todos os usuários |
| Portfólio XLS B3 muda formato | Média | Parser defensivo + testes com múltiplos formatos |
| CVM questiona o produto | Baixa com disclaimers | Linguagem cuidadosa, não chamar de "recomendação" |

---

## Critérios de Pronto por Fase

**Fase 1 concluída quando:**
- `docker-compose up` inicia a aplicação zerada em qualquer máquina
- Dois usuários com emails diferentes têm portfólios separados e isolados
- Scheduler continua rodando após restart do processo Flask
- `GET /api/portfolio` retorna 401 sem token válido

**Fase 2 concluída quando:**
- Usuário consegue se registrar, pagar via PIX e acessar o screener completo
- Arquivo XLS B3 enviado por um usuário não é visível para outro
- Disclaimer legal aparece em todas as páginas
- Deploy funcionando em Railway com HTTPS

**Fase 3 concluída quando:**
- Score do ranking inclui Magic Formula como critério adicional
- Usuário Pro recebe alerta Telegram quando ticker entra em "Forte Alinhamento Técnico"
