"""
API server para o frontend YFINANCE.

Serve os dados JSON do backend e dados de gráfico via yfinance.

Endpoints:
    GET /                     → frontend/index.html
    GET /api/decision         → decision_stocks.json
    GET /api/valuation/<t>    → valuations.json[ticker]
    GET /api/history/<t>      → stock_history.json[ticker]
    GET /api/chart/<t>        → OHLCV 6 meses via yfinance

Uso:
    cd YFINANCE_REFACTOR/backend
    python api_server.py
    Acesse: http://localhost:5000
"""

import json
import math
import os
import sys
import threading
import time
from datetime import datetime

import yfinance
from flask import Flask, jsonify, request, send_from_directory

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repositories import stock_repository as repo
from services import decision_service
from services import portfolio_service
from services import valuation_calculator
from services.price_service import PriceService as _PriceService

_price_svc = _PriceService()

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")
DATA_DIR     = os.path.join(BASE_DIR, "data")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="/static")


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


# ---------------------------------------------------------------------------
# API — decision_stocks.json
# ---------------------------------------------------------------------------

@app.route("/api/sectors")
def sectors():
    path = os.path.join(DATA_DIR, "all_sectors.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


@app.route("/api/decision")
def decision():
    path = os.path.join(DATA_DIR, "decision_stocks.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


# ---------------------------------------------------------------------------
# API — valuation detalhado
# ---------------------------------------------------------------------------

@app.route("/api/valuation/<ticker>")
def valuation(ticker):
    t = ticker.upper()
    entry = repo.get_valuation(t)
    if entry is None:
        # Fallback: calcula sem restrições (para ativos da carteira fora do screening)
        entry = valuation_calculator.calculate(t, force=True)
        if entry is None:
            return jsonify({"error": "not found"}), 404
    ind = repo.get_indicators_by_ticker(t) or {}
    entry = dict(entry)
    entry["companyname"] = ind.get("companyname", "")
    return jsonify(entry)


# ---------------------------------------------------------------------------
# API — histórico (dividendos por ano, lucro)
# ---------------------------------------------------------------------------

@app.route("/api/history/<ticker>")
def history(ticker):
    entry = repo.get_history(ticker.upper())
    if entry is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(entry)


# ---------------------------------------------------------------------------
# API — dividendos pagos no ano corrente (YTD)
# ---------------------------------------------------------------------------

@app.route("/api/dividends_ytd/<ticker>")
def dividends_ytd(ticker):
    current_year = datetime.now().year
    try:
        yf_ticker = yfinance.Ticker(f"{ticker.upper()}.SA")
        divs = yf_ticker.dividends
        ytd = float(divs[divs.index.year == current_year].sum())
        return jsonify({"year": current_year, "paid": round(ytd, 4)})
    except Exception as e:
        return jsonify({"year": current_year, "paid": 0.0})


# ---------------------------------------------------------------------------
# API — carteira B3
# ---------------------------------------------------------------------------

@app.route("/api/portfolio")
def portfolio():
    return jsonify(portfolio_service.load())


# ---------------------------------------------------------------------------
# API — favoritos
# ---------------------------------------------------------------------------

_FAV_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "favoritos.json")
_RADAR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "radar.json")


def _load_favoritos():
    try:
        with open(_FAV_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"tickers": []}


def _save_favoritos(data):
    import tempfile
    dir_name = os.path.dirname(_FAV_PATH)
    fd, tmp = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, _FAV_PATH)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _load_radar():
    try:
        with open(_RADAR_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"items": [], "dismissed": []}


def _save_radar(data):
    import tempfile
    dir_name = os.path.dirname(_RADAR_PATH)
    fd, tmp = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, _RADAR_PATH)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


@app.route("/api/favoritos")
def get_favoritos():
    return jsonify(_load_favoritos())


@app.route("/api/favoritos", methods=["POST"])
def save_favoritos():
    body = request.get_json(force=True)
    tickers = body.get("tickers", [])
    data = {"tickers": [t.upper() for t in tickers], "last_updated": datetime.now().isoformat()}
    _save_favoritos(data)
    return jsonify(data)


# ---------------------------------------------------------------------------
# API — radar
# ---------------------------------------------------------------------------

@app.route("/api/radar")
def get_radar():
    return jsonify(_load_radar())


@app.route("/api/radar", methods=["POST"])
def save_radar():
    body = request.get_json(force=True)
    data = _load_radar()
    data["items"] = body.get("items", [])
    data["last_updated"] = datetime.now().isoformat()
    _save_radar(data)
    return jsonify(data)


@app.route("/api/radar/alerts")
def get_radar_alerts():
    data = _load_radar()
    now = datetime.now()
    dismissed = {(d["ticker"], d["type"]): d["until"] for d in data.get("dismissed", [])}
    alerts = []
    prices = {}
    for item in data.get("items", []):
        ticker = item["ticker"]
        price  = repo.get_price(ticker)
        if price is None:
            price = _price_svc.fetch_from_google(ticker)
            if price is not None:
                repo.save_price(ticker, price)
        if price is not None:
            prices[ticker] = round(price, 2)
        else:
            continue
        for atype, threshold, triggered in [
            ("buy",  item.get("price_buy"),  item.get("price_buy")  is not None and price <= item.get("price_buy")),
            ("sell", item.get("price_sell"), item.get("price_sell") is not None and price >= item.get("price_sell")),
        ]:
            if not triggered:
                continue
            until_str = dismissed.get((ticker, atype))
            if until_str:
                try:
                    if datetime.fromisoformat(until_str) > now:
                        continue
                except ValueError:
                    pass
            alerts.append({"ticker": ticker, "type": atype, "price": round(price, 2), "threshold": round(threshold, 2)})
    return jsonify({"alerts": alerts, "prices": prices})


@app.route("/api/radar/dismiss", methods=["POST"])
def dismiss_radar_alert():
    from datetime import timedelta
    body   = request.get_json(force=True)
    ticker = body.get("ticker", "").upper()
    atype  = body.get("type", "")
    data   = _load_radar()
    until_dt = datetime.now() + timedelta(hours=24)
    data["dismissed"] = [d for d in data.get("dismissed", []) if not (d["ticker"] == ticker and d["type"] == atype)]
    data["dismissed"].append({"ticker": ticker, "type": atype, "until": until_dt.isoformat(timespec="seconds")})
    data["last_updated"] = datetime.now().isoformat()
    _save_radar(data)
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# API — gráfico OHLCV 6 meses
# ---------------------------------------------------------------------------

@app.route("/api/chart/<ticker>")
def chart(ticker):
    yf_ticker_str = f"{ticker.upper()}.SA"
    try:
        yf = yfinance.Ticker(yf_ticker_str)
        hist = yf.history(period="6mo")

        if hist.empty:
            return jsonify({"error": "no data"}), 404

        def safe_float(v):
            try:
                f = float(v)
                return None if math.isnan(f) else round(f, 2)
            except Exception:
                return None

        def safe_int(v):
            try:
                f = float(v)
                return 0 if math.isnan(f) else int(f)
            except Exception:
                return 0

        dates   = [d.strftime("%Y-%m-%d") for d in hist.index]
        closes  = [safe_float(v) for v in hist["Close"]]
        highs   = [safe_float(v) for v in hist["High"]]
        lows    = [safe_float(v) for v in hist["Low"]]
        volumes = [safe_int(v) for v in hist["Volume"]]

        return jsonify({
            "dates":   dates,
            "closes":  closes,
            "highs":   highs,
            "lows":    lows,
            "volumes": volumes,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Scheduler — roda decision_service a cada 1 hora em background
# ---------------------------------------------------------------------------

REFRESH_INTERVAL_HOURS = 0.5

def _run_decision():
    """Executa o decision_service e registra o horário."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[scheduler] {now} — iniciando decision_service...")
    try:
        decision_service.run()
        print(f"[scheduler] {now} — decision_service concluído.")
    except Exception as e:
        print(f"[scheduler] ERRO em decision_service: {e}")


def _scheduler_loop():
    """Loop de background: executa imediatamente e depois a cada REFRESH_INTERVAL_HOURS."""
    _run_decision()
    while True:
        time.sleep(REFRESH_INTERVAL_HOURS * 3600)
        _run_decision()


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    t = threading.Thread(target=_scheduler_loop, daemon=True, name="decision-scheduler")
    t.start()
    print(f"\n  YFINANCE API  →  http://localhost:{port}")
    print(f"  Frontend      →  {FRONTEND_DIR}")
    print(f"  Scheduler     →  decision_service a cada {REFRESH_INTERVAL_HOURS}h\n")
    app.run(host="0.0.0.0", port=port, debug=False)
