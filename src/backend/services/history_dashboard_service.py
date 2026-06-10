"""
History dashboard service — lê a aba ``Dash`` do Excel de histórico
(``data/History/B3.xlsx``) e calcula o dashboard de proventos da Carteira:

  - série mensal de proventos, acumulado e patrimônio;
  - agregação por ano (total, média mensal, crescimento A/A);
  - agregação por trimestre;
  - marcos de R$10.000 em proventos acumulados (quando cada múltiplo foi atingido);
  - previsão (faixa otimista 6m / conservadora 12m) de quando o próximo marco
    de R$10.000 será alcançado.

A lógica de cálculo (``build_dashboard``) é pura e independente do Excel — recebe
a série mensal ``[(date, value, patrimony)]`` e devolve o dict do dashboard. Só
``load`` toca disco. Assim ficamos imunes a fórmulas desatualizadas / mudança de
layout das tabelas-resumo da planilha: tudo é derivado da série mensal crua.
"""

import math
import os
from datetime import datetime
from typing import List, Optional, Tuple

import openpyxl

from config import rules

HISTORY_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "History"
)

Series = List[Tuple[datetime, float, float]]


# ---------------------------------------------------------------------------
# Helpers de data / arredondamento
# ---------------------------------------------------------------------------

def _ym(dt: datetime) -> str:
    return "%04d-%02d" % (dt.year, dt.month)


def _ym_from(year: int, month: int) -> str:
    return "%04d-%02d" % (year, month)


def _add_months(year: int, month: int, n: int) -> Tuple[int, int]:
    idx = year * 12 + (month - 1) + n
    return idx // 12, idx % 12 + 1


def _month_diff(y1: int, m1: int, y2: int, m2: int) -> int:
    return (y2 - y1) * 12 + (m2 - m1)


def _r(x, n: int = 2) -> float:
    return round(float(x), n)


# ---------------------------------------------------------------------------
# Cálculo puro do dashboard
# ---------------------------------------------------------------------------

def build_dashboard(series: Series) -> dict:
    """Recebe a série mensal ``[(date, value, patrimony)]`` (ordem ascendente)
    e devolve o dict completo do dashboard."""
    series = [(d, float(v), float(p)) for (d, v, p) in series]
    if not series:
        return _empty()

    labels, acumulado, patrimony_s, prov_mes = [], [], [], []
    cum_raw: List[float] = []
    running = 0.0
    for (dt, v, p) in series:
        running += v
        cum_raw.append(running)
        labels.append(_ym(dt))
        acumulado.append(_r(running))
        patrimony_s.append(_r(p))
        prov_mes.append(_r(v))

    total = running
    last_dt = series[-1][0]
    step = rules.DIVIDEND_MILESTONE_STEP

    next_n = int(total // step) + 1
    next_milestone = next_n * step
    prev_value = (next_n - 1) * step
    progress_pct = _r((total - prev_value) / step * 100.0, 2)
    remaining = _r(next_milestone - total, 2)

    summary = {
        "total_proventos": _r(total),
        "patrimony": _r(series[-1][2]),
        "last_month": _ym(last_dt),
        "next_milestone": next_milestone,
        "progress_pct": progress_pct,
        "remaining": remaining,
    }
    summary.update(_ytd(series, last_dt))

    return {
        "currency": "BRL",
        "summary": summary,
        "series": {
            "labels": labels,
            "acumulado": acumulado,
            "patrimony": patrimony_s,
            "proventos_mes": prov_mes,
        },
        "by_year": _by_year(series, last_dt),
        "by_quarter": _by_quarter(series),
        "milestones": _milestones(series, cum_raw, total, step),
    }


def _milestones(series: Series, cum_raw: List[float], total: float, step: float) -> List[dict]:
    next_n = int(total // step) + 1
    out: List[dict] = []
    prev_date = series[0][0]
    for k in range(1, next_n + 1):
        target = k * step
        if total >= target:
            cross_idx = next(i for i, a in enumerate(cum_raw) if a >= target)
            cross_dt = series[cross_idx][0]
            months = _month_diff(prev_date.year, prev_date.month, cross_dt.year, cross_dt.month) + 1
            out.append({
                "n": k,
                "target": target,
                "reached": True,
                "date": _ym(cross_dt),
                "months": months,
            })
            prev_date = cross_dt
        else:
            remaining = _r(target - total, 2)
            out.append({
                "n": k,
                "target": target,
                "reached": False,
                "progress_pct": _r((total - (k - 1) * step) / step * 100.0, 2),
                "remaining": remaining,
                "forecast": _forecast(series, remaining),
            })
    return out


def _forecast(series: Series, remaining: float) -> dict:
    """Projeta o ETA do próximo marco por duas janelas, gerando uma faixa:
      - ``optimistic``  → ritmo recente (média dos últimos 6 meses);
      - ``conservative`` → média longa (últimos 12 meses).
    Como o ritmo recente costuma ser >= o de longo prazo, a janela curta dá o ETA
    mais cedo (otimista). ``eta`` = último mês + ceil(faltante / ritmo)."""
    last_dt = series[-1][0]
    values = [v for (_, v, _) in series]

    def project(window: int) -> dict:
        window_vals = values[-window:] if len(values) >= window else values[:]
        rate = sum(window_vals) / len(window_vals) if window_vals else 0.0
        if rate <= 0:
            return {"window_months": window, "rate": _r(rate), "months": None, "eta": None}
        months_raw = remaining / rate
        y, m = _add_months(last_dt.year, last_dt.month, int(math.ceil(months_raw)))
        return {
            "window_months": window,
            "rate": _r(rate),
            "months": round(months_raw, 1),
            "eta": _ym_from(y, m),
        }

    return {
        "optimistic": project(rules.FORECAST_WINDOW_SHORT_MONTHS),
        "conservative": project(rules.FORECAST_WINDOW_LONG_MONTHS),
    }


def _ytd(series: Series, last_dt: datetime) -> dict:
    cur_year, cur_month = last_dt.year, last_dt.month
    prev_year = cur_year - 1
    cur_sum = sum(v for (dt, v, _) in series if dt.year == cur_year and dt.month <= cur_month)
    prev_sum = sum(v for (dt, v, _) in series if dt.year == prev_year and dt.month <= cur_month)
    growth = round((cur_sum / prev_sum - 1) * 100.0, 1) if prev_sum > 0 else None
    return {
        "ytd_current": {"year": cur_year, "value": _r(cur_sum)},
        "ytd_prev": {"year": prev_year, "value": _r(prev_sum)},
        "ytd_growth_pct": growth,
    }


def _by_year(series: Series, last_dt: datetime) -> List[dict]:
    last_year = last_dt.year
    totals: dict = {}
    counts: dict = {}
    for (dt, v, _) in series:
        totals[dt.year] = totals.get(dt.year, 0.0) + v
        counts[dt.year] = counts.get(dt.year, 0) + 1

    out: List[dict] = []
    prev_total: Optional[float] = None
    for y in sorted(totals):
        t = totals[y]
        # ano corrente (último) → divide pelos meses presentes; anos fechados → /12
        divisor = counts[y] if y == last_year else 12
        growth = round((t / prev_total - 1) * 100.0, 1) if prev_total else None
        out.append({
            "year": y,
            "total": _r(t),
            "monthly_avg": _r(t / divisor) if divisor else 0.0,
            "growth_pct": growth,
        })
        prev_total = t
    return out


def _by_quarter(series: Series) -> List[dict]:
    totals: dict = {}
    for (dt, v, _) in series:
        q = (dt.month - 1) // 3 + 1
        key = (dt.year, q)
        totals[key] = totals.get(key, 0.0) + v
    return [
        {"label": "Q%d %d" % (q, year), "total": _r(totals[(year, q)])}
        for (year, q) in sorted(totals)
    ]


def _empty() -> dict:
    return {
        "currency": "BRL",
        "summary": {},
        "series": {"labels": [], "acumulado": [], "patrimony": [], "proventos_mes": []},
        "by_year": [],
        "by_quarter": [],
        "milestones": [],
    }


# ---------------------------------------------------------------------------
# Leitura do Excel (I/O)
# ---------------------------------------------------------------------------

def _find_history_file() -> Optional[str]:
    """Primeiro .xlsx encontrado em data/History/ (robusto a renome)."""
    try:
        for fname in sorted(os.listdir(HISTORY_DIR)):
            if fname.lower().endswith(".xlsx"):
                return os.path.join(HISTORY_DIR, fname)
    except FileNotFoundError:
        pass
    return None


def _read_series(path: str) -> Series:
    """Lê a aba ``Dash`` → série mensal [(date, value, patrimony)]. As colunas são
    localizadas pelo cabeçalho (linha 1), não pela posição — robusto a reordenação.
    openpyxl (não xlrd): o xlrd 2.x não lê .xlsx.

    O provento mensal é derivado como a **variação do acumulado** (coluna ``STD``,
    a linha de proventos acumulados que o usuário plota), e não da coluna ``Value``.
    A coluna ``STD`` é a fonte autoritativa do dashboard (== ``Total_Div``); a coluna
    ``Value`` não está totalmente reconciliada em alguns anos. Assim todos os
    agregados (anual, trimestral, marcos 10K, YTD) batem com a planilha do usuário."""
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    try:
        ws = wb["Dash"]
        rows = ws.iter_rows(values_only=True)
        header = next(rows)

        def col(name: str) -> Optional[int]:
            for i, h in enumerate(header):
                if h is not None and str(h).strip().lower() == name:
                    return i
            return None

        i_date, i_cum, i_patr = col("date"), col("std"), col("patrimony")
        if i_date is None or i_cum is None:
            return []

        series: Series = []
        prev_cum = 0.0
        for row in rows:
            dt = row[i_date] if i_date < len(row) else None
            if dt is None:
                break  # fim da série
            if not isinstance(dt, datetime):
                continue
            cum = row[i_cum] if i_cum < len(row) else None
            cum = float(cum) if isinstance(cum, (int, float)) else prev_cum
            value = cum - prev_cum  # provento do mês = variação do acumulado
            prev_cum = cum
            p = row[i_patr] if (i_patr is not None and i_patr < len(row)) else None
            p = float(p) if isinstance(p, (int, float)) else 0.0
            series.append((dt, value, p))
        return series
    finally:
        wb.close()


def load() -> dict:
    """Lê o Excel de histórico e devolve o dashboard. Em caso de erro/ausência,
    devolve a estrutura vazia com a chave ``error`` preenchida."""
    path = _find_history_file()
    if not path:
        result = _empty()
        result["error"] = "Arquivo de histórico não encontrado em data/History/"
        return result
    try:
        series = _read_series(path)
    except Exception as e:  # noqa: BLE001 — propaga como mensagem amigável ao frontend
        result = _empty()
        result["error"] = "Falha ao ler %s: %s" % (os.path.basename(path), e)
        return result
    if not series:
        result = _empty()
        result["error"] = "Aba 'Dash' sem dados de série mensal"
        return result

    dashboard = build_dashboard(series)
    dashboard["source_file"] = os.path.basename(path)
    return dashboard
