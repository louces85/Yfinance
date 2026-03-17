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
from flask import Flask, jsonify, send_from_directory

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repositories import stock_repository as repo
from services import decision_service
from services import portfolio_service

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
    entry = repo.get_valuation(ticker.upper())
    if entry is None:
        return jsonify({"error": "not found"}), 404
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
# API — carteira B3
# ---------------------------------------------------------------------------

@app.route("/api/portfolio")
def portfolio():
    return jsonify(portfolio_service.load())


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

REFRESH_INTERVAL_HOURS = 1

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
