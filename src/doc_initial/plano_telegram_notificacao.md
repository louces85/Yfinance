# Plano: Notificação Telegram — Ativos de Compra

## Context
O usuário quer receber no Telegram uma mensagem formatada diariamente com os ativos nas zonas COMPRA_FORTE e COMPRA, mostrando ticker, preço atual, alvo Bazin e potencial de ganho. O envio deve funcionar de duas formas: rodar manualmente via CLI e ser chamado automaticamente pelo api_server.py uma vez por dia.

---

## Como funciona o Telegram Bot (explicação)

1. **Criar o bot**: no Telegram, abrir conversa com `@BotFather`, digitar `/newbot`, seguir as instruções. Ele entrega um **token** (ex: `7123456789:AAFxxxxxx`).
2. **Obter o chat_id**: enviar qualquer mensagem para o bot, depois acessar `https://api.telegram.org/bot{TOKEN}/getUpdates` no browser. O campo `"chat": {"id": ...}` é o chat_id. Para grupo: adicionar o bot ao grupo e fazer o mesmo.
3. **Enviar mensagem**: uma chamada HTTP POST para `https://api.telegram.org/bot{TOKEN}/sendMessage` com `chat_id` e `text`. Suporta formatação Markdown.

Não precisa de nenhuma biblioteca especial — a stdlib `urllib` basta, mas usaremos `requests` (já disponível no projeto via yfinance).

---

## Arquivos a criar/modificar

| Arquivo | Ação |
|---------|------|
| `backend/.env` | Criar — guarda TELEGRAM_TOKEN e TELEGRAM_CHAT_ID |
| `backend/services/telegram_service.py` | Criar — lógica de formatação e envio |
| `backend/notify_telegram.py` | Criar — entry point CLI standalone |
| `backend/api_server.py` | Modificar — adicionar scheduler diário e endpoint opcional |

`.env` já está no `.gitignore` (verificar). Se não estiver, adicionar.

---

## Formato da mensagem

```
📊 *YFINANCE — Oportunidades* · 17/03/2026 14:00

🟢 *COMPRA FORTE* (3)
• RAPT4  R$ 4,80 → alvo R$ 7,72  (+60,8%)
• XXXX3  R$ 9,10 → alvo R$ 12,30 (+35,2%)
• YYYY4  R$ 3,20 → alvo R$ 4,80  (+50,0%)

🟡 *COMPRA* (5)
• ZZZZ3  R$ 11,50 → alvo R$ 13,20 (+14,8%)
...

_Score mínimo exibido: todos_
```

Usar `parse_mode=Markdown` na API do Telegram.

---

## Implementação

### 1. `backend/.env`
```
TELEGRAM_TOKEN=SEU_TOKEN_AQUI
TELEGRAM_CHAT_ID=SEU_CHAT_ID_AQUI
```

### 2. `backend/services/telegram_service.py`
- Função `send_opportunities()`:
  - Lê `data/decision_stocks.json` diretamente (sem chamar a API HTTP — leitura direta do arquivo)
  - Filtra `zone in ("COMPRA_FORTE", "COMPRA")`
  - Ordena por `gain_pct` desc
  - Monta texto formatado com Markdown
  - POST para `https://api.telegram.org/bot{TOKEN}/sendMessage`
  - Retorna `{"ok": True, "count": N}` ou lança exceção com mensagem de erro
- Lê token e chat_id via `os.getenv()` (carregado do .env)

### 3. `backend/notify_telegram.py` (CLI)
```python
# uso: python notify_telegram.py
from dotenv import load_dotenv
load_dotenv()
from services.telegram_service import send_opportunities
result = send_opportunities()
print(f"✅ Enviado! {result['count']} ativos")
```

### 4. `backend/api_server.py` (modificações)
- Importar `python-dotenv` e chamar `load_dotenv()` no início
- No scheduler existente, adicionar job diário às 9h (horário Brasil):
  ```python
  # executa todo dia às 9:00
  scheduler.every().day.at("09:00").do(telegram_service.send_opportunities)
  ```
  OBS: o scheduler atual usa `threading` + `time.sleep` com loop. Adaptar para verificar hora ou usar `schedule` lib.
- Adicionar endpoint opcional: `POST /api/notify/telegram` → chama `send_opportunities()` manualmente (útil para testar sem CLI)

---

## Dependências a instalar
```bash
pip install python-dotenv schedule
```
`requests` já está disponível (dependência do yfinance).

---

## Verificação / Como testar

1. Criar bot no BotFather e preencher `.env`
2. Rodar manualmente: `cd backend && python notify_telegram.py`
3. Checar mensagem chegou no Telegram
4. Testar endpoint: `curl -X POST http://localhost:5000/api/notify/telegram`
5. Verificar log do servidor quando scheduler disparar
