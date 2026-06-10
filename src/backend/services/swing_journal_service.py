"""
Swing journal service — diário de operações de swing trade do usuário.

Diferente de ``swing_service`` (que gera SINAIS automáticos), aqui ficam as
operações que o usuário efetivamente registrou: o que comprou (posições abertas)
e o que já vendeu (histórico). Persistido em ``data/swing_positions.json`` via
``stock_repository`` (escrita atômica).

A camada de cálculo é pura e testável isoladamente:
  - ``enrich_open``   → P&L flutuante (preço atual), %, dias na carteira, distância
                        do stop/alvo;
  - ``enrich_closed`` → P&L realizado, %, valor da venda, dias entre compra e venda;
  - ``darf_summary``  → soma das vendas do mês corrente vs. limite de isenção de IR
                        do swing comum (R$ 20.000/mês), com status ok/warn/over.

Só ``list_positions``/``add``/``close``/``update``/``delete`` tocam o repositório.
"""

from datetime import date, datetime

from config import rules
from repositories import stock_repository as repo

REQUIRED_FIELDS = ("ticker", "qty", "entry_price", "entry_date")
EDITABLE_FIELDS = ("qty", "entry_price", "entry_date", "stop", "target", "notes")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def _opt_float(v):
    if v is None or v == "":
        return None
    return float(v)


def _today():
    return date.today()


# ---------------------------------------------------------------------------
# Cálculo puro
# ---------------------------------------------------------------------------

def enrich_open(pos, current_price, today):
    """Enriquece uma posição ABERTA com P&L flutuante e métricas de risco.
    ``current_price`` pode ser None (sem cotação disponível)."""
    qty = float(pos["qty"])
    entry = float(pos["entry_price"])
    stop = pos.get("stop")
    target = pos.get("target")

    out = dict(pos)
    out["current_price"] = current_price
    out["days_held"] = (today - _parse_date(pos["entry_date"])).days

    if current_price is None:
        out["unrealized_pl"] = None
        out["unrealized_pct"] = None
        out["dist_stop_pct"] = None
        out["dist_target_pct"] = None
        return out

    out["unrealized_pl"] = round((current_price - entry) * qty, 2)
    out["unrealized_pct"] = round((current_price / entry - 1) * 100, 2) if entry else None
    out["dist_stop_pct"] = round((current_price / stop - 1) * 100, 2) if stop else None
    out["dist_target_pct"] = round((target / current_price - 1) * 100, 2) if target else None
    return out


def enrich_closed(pos):
    """Enriquece uma posição FECHADA com P&L realizado, valor da venda e dias."""
    qty = float(pos["qty"])
    entry = float(pos["entry_price"])
    exit_price = float(pos["exit_price"])

    out = dict(pos)
    out["realized_pl"] = round((exit_price - entry) * qty, 2)
    out["realized_pct"] = round((exit_price / entry - 1) * 100, 2) if entry else None
    out["sale_value"] = round(exit_price * qty, 2)
    out["days_held"] = (_parse_date(pos["exit_date"]) - _parse_date(pos["entry_date"])).days
    return out


def darf_summary(positions, month):
    """Soma o valor VENDIDO no ``month`` (YYYY-MM) e compara com o limite de
    isenção mensal de IR do swing comum. Considera só posições fechadas cuja
    ``exit_date`` cai no mês pedido."""
    limit = rules.SWING_DARF_MONTHLY_LIMIT
    warn = round(limit * rules.SWING_DARF_WARN_RATIO, 2)
    total = 0.0
    for p in positions:
        if p.get("status") != "closed":
            continue
        ed = p.get("exit_date")
        if not ed or ed[:7] != month:
            continue
        total += float(p["exit_price"]) * float(p["qty"])
    total = round(total, 2)

    if total >= limit:
        status = "over"
    elif total >= warn:
        status = "warn"
    else:
        status = "ok"

    return {
        "month": month,
        "total_sales": total,
        "limit": limit,
        "warn_threshold": warn,
        "pct": round(total / limit * 100, 2) if limit else 0.0,
        "status": status,
    }


def position_alerts(positions, prices):
    """Alertas de stop/alvo p/ posições abertas. ``prices`` é {ticker: preço atual}.
      - ``stop``   → preço <= stop  (cortar a perda);
      - ``target`` → preço >= alvo  (realizar o lucro).
    Posições sem preço disponível são ignoradas. Cada alerta carrega o ``id`` da
    operação (p/ destacar a linha) e o ``threshold`` que foi cruzado."""
    out = []
    for p in positions:
        price = prices.get(p.get("ticker"))
        if price is None:
            continue
        stop = p.get("stop")
        target = p.get("target")
        if stop is not None and price <= stop:
            out.append({"id": p.get("id"), "ticker": p.get("ticker"),
                        "type": "stop", "price": round(price, 2), "threshold": stop})
        if target is not None and price >= target:
            out.append({"id": p.get("id"), "ticker": p.get("ticker"),
                        "type": "target", "price": round(price, 2), "threshold": target})
    return out


def _current_price(ticker, prices, fallback):
    """Preço atual a partir de stock_prices.json; fallback p/ o ``price`` do
    swing_data.json; None se nenhum disponível."""
    t = ticker.upper()
    entry = prices.get(t)
    if entry and entry.get("price_now"):
        return entry["price_now"]
    fb = fallback.get(t)
    return fb if fb else None


# ---------------------------------------------------------------------------
# Orquestração (toca o repositório)
# ---------------------------------------------------------------------------

def list_positions():
    """Lista operações abertas (com P&L ao vivo) e fechadas (histórico), mais o
    resumo de DARF do mês corrente."""
    positions = repo.load_swing_positions()
    prices = repo.get_all_prices()
    fallback = {d.get("ticker"): d.get("price") for d in repo.load_swing_data()}
    today = _today()

    open_list, closed_list = [], []
    for p in positions:
        if p.get("status") == "closed":
            closed_list.append(enrich_closed(p))
        else:
            cur = _current_price(p["ticker"], prices, fallback)
            open_list.append(enrich_open(p, cur, today))

    month = "%04d-%02d" % (today.year, today.month)
    return {
        "open": open_list,
        "closed": closed_list,
        "darf": darf_summary(positions, month),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }


def add_position(payload):
    """Cria uma nova operação ABERTA. Levanta ValueError se faltar campo obrigatório."""
    for f in REQUIRED_FIELDS:
        if payload.get(f) in (None, ""):
            raise ValueError("Campo obrigatorio ausente: %s" % f)

    now = datetime.now()
    ticker = str(payload["ticker"]).upper()
    pos = {
        "id":          now.strftime("%Y%m%d%H%M%S%f") + "-" + ticker,
        "ticker":      ticker,
        "qty":         float(payload["qty"]),
        "entry_date":  str(payload["entry_date"]),
        "entry_price": float(payload["entry_price"]),
        "stop":        _opt_float(payload.get("stop")),
        "target":      _opt_float(payload.get("target")),
        "exit_date":   None,
        "exit_price":  None,
        "status":      "open",
        "source":      payload.get("source", "manual"),
        "notes":       payload.get("notes", ""),
        "created_at":  now.isoformat(timespec="seconds"),
    }
    positions = repo.load_swing_positions()
    positions.append(pos)
    repo.save_swing_positions(positions)
    return pos


def _find(positions, pos_id):
    for p in positions:
        if p.get("id") == pos_id:
            return p
    return None


def close_position(pos_id, exit_price, exit_date):
    """Fecha (vende) uma operação: grava preço/data de saída e muda status p/ closed."""
    if exit_price in (None, "") or not exit_date:
        raise ValueError("exit_price e exit_date sao obrigatorios")
    positions = repo.load_swing_positions()
    found = _find(positions, pos_id)
    if found is None:
        raise KeyError(pos_id)
    found["exit_price"] = float(exit_price)
    found["exit_date"] = str(exit_date)
    found["status"] = "closed"
    repo.save_swing_positions(positions)
    return found


def update_position(pos_id, payload):
    """Edita campos editáveis de uma operação (tipicamente aberta)."""
    positions = repo.load_swing_positions()
    found = _find(positions, pos_id)
    if found is None:
        raise KeyError(pos_id)
    for f in EDITABLE_FIELDS:
        if f in payload:
            if f in ("qty", "entry_price"):
                found[f] = float(payload[f])
            elif f in ("stop", "target"):
                found[f] = _opt_float(payload[f])
            else:
                found[f] = payload[f]
    repo.save_swing_positions(positions)
    return found


def delete_position(pos_id):
    """Remove uma operação. Retorna True se removeu, False se o id não existia."""
    positions = repo.load_swing_positions()
    new_list = [p for p in positions if p.get("id") != pos_id]
    if len(new_list) == len(positions):
        return False
    repo.save_swing_positions(new_list)
    return True
