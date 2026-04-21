"""
Busca e persiste demonstrativos financeiros históricos (até 10 anos):
  - DRE via StatusInvest getdre
  - Balanço Patrimonial via StatusInvest getativos
  - Fluxo de Caixa via yfinance (até 4 anos — StatusInvest não tem endpoint de DFC)

Processa apenas tickers válidos conforme stock_validity.json.
Respeita intervalo de FINANCIALS_UPDATE_INTERVAL_DAYS (30 dias) — rode quando quiser.

Uso:
    python financials_fetcher.py                  # todos os válidos
    python financials_fetcher.py BBAS3 PETR4      # tickers específicos
    python financials_fetcher.py --force          # força reprocessamento de todos os válidos
    python financials_fetcher.py BBAS3 --force    # força ticker específico
    python financials_fetcher.py --update         # atualiza apenas tickers defasados (>= 2 anos), respeitando intervalo de 30 dias
    python financials_fetcher.py --update --force # força reprocessamento de todos os defasados, ignorando intervalo
"""

import math
import sys
import os
import time
from datetime import datetime, timedelta
from typing import List, Optional

import httpx
import yfinance

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories import stock_repository as repo
from config.rules import FINANCIALS_UPDATE_INTERVAL_DAYS, FINANCIALS_YEARS

_SI_HEADERS = {
    "accept": "*/*",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    ),
}
_SI_DELAY = 1.5  # segundos entre chamadas ao StatusInvest

# Mapeamento: nome exato retornado pelo StatusInvest -> chave interna snake_case
_DRE_FIELD_MAP = {
    "Receita Líquida - (R$)":              "receita_liquida",
    "Custos - (R$)":                       "custos",
    "Lucro Bruto - (R$)":                  "lucro_bruto",
    "Despesas/Receitas Operacionais - (R$)": "despesas_operacionais",
    "EBITDA - (R$)":                       "ebitda",
    "Amortização/Depreciação":             "depreciacao",
    "EBIT - (R$)":                         "ebit",
    "Resultado não operacional - (R$)":    "resultado_nao_operacional",
    "Resultado Financeiro - (R$)":         "resultado_financeiro",
    "Impostos - (R$)":                     "impostos",
    "Lucro Líquido - (R$)":               "lucro_liquido",
    # capex removido: StatusInvest sempre retorna 0,00 neste endpoint (não confiável)
    # Use fluxo_caixa.capex (yfinance) para dados de CAPEX
    "Dívida Bruta - (R$)":                "divida_bruta",
    "Dívida Líquida - (R$)":              "divida_liquida",
    "ROE - (%)":                           "roe",
    "ROIC - (%)":                          "roic",
    "Margem Bruta - (%)":                  "margem_bruta",
    "Margem Ebitda - (%)":                 "margem_ebitda",
    "Margem Líquida - (%)":               "margem_liquida",
    "Dívida Líquida/Ebitda":              "dl_ebitda",
}

_FLUXO_CAIXA_FIELD_MAP = {
    "Caixa Líquido Atividades Operacionais - (R$)":    "fco",
    "Depreciação e Amortização - (R$)":                "da",
    "Fluxo de Caixa Livre - (R$)":                     "fcf_livre",
    "Caixa Líquido Atividades de Investimento - (R$)": "investing",
    "Caixa Líquido Atividades de Financiamento - (R$)": "financing",
    "Lucro Líquido - (R$)":                            "lucro_liquido_cf",
    "Variações nos Ativos e Passivos - (R$)":          "variacao_capital_giro",
    "Saldo Final de Caixa e Equivalentes - (R$)":      "saldo_final_caixa",
    "Aumento de Caixa e Equivalentes - (R$)":          "variacao_caixa",
}

_BALANCO_FIELD_MAP = {
    "Ativo Total - (R$)":                          "ativo_total",
    "Ativo Circulante - (R$)":                     "ativo_circulante",
    "Aplicações Financeiras - (R$)":               "aplicacoes_financeiras",
    "Caixa e Equivalentes de Caixa - (R$)":        "caixa_equivalentes",
    "Contas a Receber - (R$)":                     "contas_a_receber",
    "Estoque - (R$)":                              "estoque",
    "Ativo Não Circulante - (R$)":                 "ativo_nao_circulante",
    "Ativo Realizável a Longo Prazo - (R$)":       "ativo_realizavel_lp",
    "Investimentos - (R$)":                        "investimentos",
    "Imobilizado - (R$)":                          "imobilizado",
    "Intangível - (R$)":                           "intangivel",
    "Passivo Total - (R$)":                        "passivo_total",
    "Passivo Circulante - (R$)":                   "passivo_circulante",
    "Passivo Não Circulante - (R$)":               "passivo_nao_circulante",
    "Patrimônio Líquido Consolidado - (R$)":       "patrimonio_liquido",
    "Capital Social Realizado - (R$)":             "capital_social",
    "Reserva Capital - (R$)":                      "reserva_capital",
    "Reserva Lucros - (R$)":                       "reserva_lucros",
    "Participação dos Não Controladores":          "participacao_nao_controladores",
}


# ---------------------------------------------------------------------------
# Parser de valores do StatusInvest
# ---------------------------------------------------------------------------

def parse_statusinvest_value(val_str: str) -> Optional[float]:
    """
    Converte string do StatusInvest para float.

    Exemplos:
        "3.938,54 M" -> 3938540000.0
        "-9,80"      -> -9.8
        "-"          -> None
    """
    if not val_str or val_str.strip() in ("-", "", "N/A"):
        return None

    multipliers = {" B": 1_000_000_000, " M": 1_000_000, " K": 1_000}
    s = val_str.strip()

    # Campos percentuais (ROE, ROIC, margens) vêm com "%" no valor: "10,07%" → 10.07
    s = s.rstrip("%")

    multiplier = 1
    for suffix, mult in multipliers.items():
        if s.endswith(suffix):
            multiplier = mult
            s = s[: -len(suffix)]
            break

    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s) * multiplier
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Fetch StatusInvest (DRE e Balanço)
# ---------------------------------------------------------------------------

def _fetch_statusinvest(ticker: str, endpoint: str, year_min: int, year_max: int) -> dict:
    """
    Busca dados históricos do StatusInvest para um endpoint ('getdre' ou 'getativos').

    Retorna dict: { nome_indicador_raw: { "ano_str": valor_float_ou_None, ... } }
    ou {} em caso de qualquer falha.

    Estrutura da resposta: data.grid com linhas isHeader/isData e colunas DATA/AH/AV.
    """
    url = f"https://statusinvest.com.br/acao/{endpoint}"
    params = {
        "code": ticker.lower(),
        "type": 0,
        "futureData": "false",
        "range.min": year_min,
        "range.max": year_max,
    }
    headers = {
        **_SI_HEADERS,
        "referer": f"https://statusinvest.com.br/acoes/{ticker.lower()}",
    }
    try:
        timeout = httpx.Timeout(8.0, read=20.0)
        with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url, params=params)

        if resp.status_code != 200:
            return {}

        payload = resp.json()
        if not payload.get("success"):
            return {}

        grid = payload.get("data", {}).get("grid", [])

        # Mapeia coluna -> ano usando a linha de cabeçalho (isHeader=True)
        header = next((r for r in grid if r.get("isHeader")), None)
        if not header:
            return {}

        # Mapeia coluna -> chave temporal.
        # Chaves de ano são dígitos ("2024", "2023", ...).
        # A coluna "Últ. 12M" do getdre (primeiro DATA com valor não-numérico)
        # é mapeada como "ttm" — útil para campos como divida_liquida e dl_ebitda
        # que o StatusInvest só popula no período corrente, não nos anos históricos.
        year_col_map: dict = {}  # "2024" | "ttm" -> col_index
        for idx, col in enumerate(header.get("columns", [])):
            if col.get("name") == "DATA":
                val = col.get("value", "")
                if val.isdigit():
                    year_col_map[val] = idx
                elif val.strip() and "ttm" not in year_col_map:
                    year_col_map["ttm"] = idx  # primeira coluna não-ano = TTM

        if not year_col_map:
            return {}

        result: dict = {}
        for item in grid:
            if item.get("isHeader"):
                continue
            cols = item.get("columns", [])
            if not cols:
                continue
            indicator_name = cols[0].get("value", "").strip()
            if not indicator_name:
                continue

            year_dict: dict = {}
            for year_str, col_idx in year_col_map.items():
                if col_idx < len(cols):
                    raw = cols[col_idx].get("value", "")
                    year_dict[year_str] = parse_statusinvest_value(raw)
            result[indicator_name] = year_dict

        return result

    except Exception:
        return {}


def _map_fields(raw: dict, field_map: dict) -> dict:
    """Aplica field_map ao dict raw, retornando apenas os campos mapeados."""
    return {key: raw[raw_name] for raw_name, key in field_map.items() if raw_name in raw}


def _fetch_dre(ticker: str, year_min: int, year_max: int) -> dict:
    """
    Busca DRE histórica do StatusInvest.
    Retorna dict com campos snake_case + '_source', ou {} em caso de falha.
    """
    raw = _fetch_statusinvest(ticker, "getdre", year_min, year_max)
    if not raw:
        return {}
    mapped = _map_fields(raw, _DRE_FIELD_MAP)
    if mapped:
        mapped["_source"] = "statusinvest"
    return mapped


def _fetch_balanco(ticker: str, year_min: int, year_max: int) -> dict:
    """
    Busca Balanço Patrimonial do StatusInvest.
    Retorna dict com campos snake_case + '_source', ou {} em caso de falha.
    """
    raw = _fetch_statusinvest(ticker, "getativos", year_min, year_max)
    if not raw:
        return {}
    mapped = _map_fields(raw, _BALANCO_FIELD_MAP)
    if mapped:
        mapped["_source"] = "statusinvest"
    return mapped


# ---------------------------------------------------------------------------
# Fetch Fluxo de Caixa
# ---------------------------------------------------------------------------

def _fetch_fluxo_caixa_si(ticker: str, year_min: int, year_max: int) -> dict:
    """
    Busca Fluxo de Caixa do StatusInvest (getfluxocaixa) — até 10+ anos históricos.

    Campos principais:
        fco           — Caixa Líquido Atividades Operacionais
        da            — Depreciação e Amortização
        fcf_livre     — Fluxo de Caixa Livre (FCO - Investimentos, já calculado pelo SI)
        investing     — Caixa Líquido Atividades de Investimento (total, inclui CAPEX + aquisições)
        financing     — Caixa Líquido Atividades de Financiamento
        lucro_liquido_cf      — Lucro Líquido no DFC
        variacao_capital_giro — Variações nos Ativos e Passivos
        saldo_final_caixa     — Saldo Final de Caixa e Equivalentes
        variacao_caixa        — Aumento/Diminuição de Caixa

    Nota: 'fcf_livre' usa total de investimentos (≠ CAPEX puro). Para FCF = FCO - CAPEX,
    use 'fcf' (calculado com 'capex' do yfinance).
    """
    raw = _fetch_statusinvest(ticker, "getfluxocaixa", year_min, year_max)
    if not raw:
        return {}
    mapped = _map_fields(raw, _FLUXO_CAIXA_FIELD_MAP)
    if mapped:
        mapped["_source"] = "statusinvest+yfinance"
    return mapped


def _fetch_capex_yf(ticker: str) -> dict:
    """
    Busca apenas CAPEX via yfinance (4-5 anos).
    O StatusInvest não tem linha dedicada de CAPEX no getfluxocaixa.

    Retorna dict { "ano_str": valor_negativo } ou {} em caso de falha.
    CAPEX é negativo no yfinance (saída de caixa).
    """
    try:
        yft = yfinance.Ticker(f"{ticker.upper()}.SA")
        cf = yft.cashflow
        if cf is None or cf.empty or "Capital Expenditure" not in cf.index:
            return {}
        result: dict = {}
        for i, col in enumerate(cf.columns):
            try:
                ano = str(col.year)
                val = float(cf.loc["Capital Expenditure"].iloc[i])
                result[ano] = None if math.isnan(val) else val
            except (AttributeError, TypeError, ValueError, IndexError):
                pass
        return result
    except Exception:
        return {}


def _fetch_cashflow_yf_fallback(ticker: str) -> dict:
    """
    Fallback completo para yfinance quando StatusInvest falhar.
    Retorna fco, capex, da, fcf (4-5 anos).
    """
    try:
        yft = yfinance.Ticker(f"{ticker.upper()}.SA")
        cf = yft.cashflow
        if cf is None or cf.empty:
            return {}

        anos = [str(col.year) for col in cf.columns]
        result: dict = {"_source": "yfinance"}

        for yf_field, key in [
            ("Operating Cash Flow",           "fco"),
            ("Capital Expenditure",            "capex"),
            ("Depreciation And Amortization",  "da"),
        ]:
            if yf_field not in cf.index:
                continue
            year_dict: dict = {}
            for i, ano in enumerate(anos):
                try:
                    val = float(cf.loc[yf_field].iloc[i])
                    year_dict[ano] = None if math.isnan(val) else val
                except (TypeError, ValueError, IndexError):
                    year_dict[ano] = None
            result[key] = year_dict

        if "fco" in result and "capex" in result:
            result["fcf"] = {
                ano: round(result["fco"][ano] + result["capex"][ano])
                if result["fco"].get(ano) is not None and result["capex"].get(ano) is not None
                else None
                for ano in anos
            }

        return result
    except Exception:
        return {}


def _fetch_fluxo_caixa(ticker: str, year_min: int, year_max: int) -> dict:
    """
    Fluxo de Caixa combinado:
      - Fonte primária: StatusInvest getfluxocaixa (10+ anos)
        → fco, da, fcf_livre, investing, financing, etc.
      - Complemento: yfinance para 'capex' (linha dedicada, 4-5 anos)
        + 'fcf' calculado como FCO - |capex|

    Fallback para yfinance completo se StatusInvest falhar.
    """
    si_data = _fetch_fluxo_caixa_si(ticker, year_min, year_max)

    if _has_data(si_data):
        # Adiciona CAPEX do yfinance (mais preciso que 'investing' total)
        capex_yf = _fetch_capex_yf(ticker)
        if capex_yf:
            si_data["capex"] = capex_yf
            # FCF = FCO - |capex| para anos com ambos disponíveis
            fco = si_data.get("fco", {})
            fcf_calc = {
                ano: round(fco[ano] + capex_v)
                for ano, capex_v in capex_yf.items()
                if fco.get(ano) is not None and capex_v is not None
            }
            if fcf_calc:
                si_data["fcf"] = fcf_calc
        return si_data

    # Fallback completo para yfinance
    return _fetch_cashflow_yf_fallback(ticker)


# ---------------------------------------------------------------------------
# Orquestração principal
# ---------------------------------------------------------------------------

def _has_data(d: dict) -> bool:
    """True se o dict tem pelo menos uma chave sem prefixo '_'."""
    return any(k for k in d if not k.startswith("_"))


def _needs_update(ticker: str) -> bool:
    entry = repo.get_financials(ticker)
    if entry is None:
        return True
    last_updated_str = entry.get("last_updated")
    if not last_updated_str:
        return True
    last_updated = datetime.fromisoformat(last_updated_str)
    return datetime.now() - last_updated > timedelta(days=FINANCIALS_UPDATE_INTERVAL_DAYS)


def _latest_dre_year(entry: dict) -> Optional[int]:
    """Retorna o ano mais recente disponível na DRE do ticker (excluindo TTM)."""
    dre = entry.get("dre", {})
    dre_key = next((k for k in dre if not k.startswith("_")), None)
    if not dre_key:
        return None
    anos = []
    for k in dre.get(dre_key, {}):
        try:
            anos.append(int(k))
        except (ValueError, TypeError):
            pass
    return max(anos) if anos else None


def get_stale_tickers(min_gap: int = 2) -> List[tuple]:
    """
    Detecta tickers com dados defasados no financials_history.json.

    Um ticker é considerado defasado quando:
        ano_atual - ultimo_ano_dre >= min_gap

    Exemplo em 2026: dados até 2024 → gap=2 → defasado.
                     dados até 2025 → gap=1 → OK.

    Retorna lista de (ticker, ultimo_ano) ordenada por gap descendente.
    """
    current_year = datetime.now().year
    all_financials = repo.get_all_financials()
    stale = []
    for ticker, entry in all_financials.items():
        latest = _latest_dre_year(entry)
        if latest is None:
            continue
        gap = current_year - latest
        if gap >= min_gap:
            stale.append((ticker, latest))
    stale.sort(key=lambda x: x[1])  # mais antigo primeiro
    return stale


def fetch_financials(ticker: str) -> Optional[dict]:
    """
    Orquestra os três fetches para um ticker com rate limiting entre chamadas SI.

    Fluxo:
        _fetch_dre()          → sleep(1.5s)
        _fetch_balanco()      → sleep(1.5s)
        _fetch_fluxo_caixa()  → sleep(1.5s)  ← StatusInvest (10+ anos) + yfinance CAPEX

    Política de falha parcial: salva qualquer seção que tiver dados.
    Retorna None apenas se todas as três seções falharem.
    """
    current_year = datetime.now().year
    year_min = current_year - FINANCIALS_YEARS
    year_max = current_year

    dre = _fetch_dre(ticker, year_min, year_max)
    time.sleep(_SI_DELAY)
    balanco = _fetch_balanco(ticker, year_min, year_max)
    time.sleep(_SI_DELAY)
    cashflow = _fetch_fluxo_caixa(ticker, year_min, year_max)
    time.sleep(_SI_DELAY)

    if not _has_data(dre) and not _has_data(balanco) and not _has_data(cashflow):
        return None

    return {
        "dre":         dre,
        "balanco":     balanco,
        "fluxo_caixa": cashflow,
    }


def update_ticker(ticker: str, force: bool = False) -> Optional[dict]:
    """
    Busca e persiste demonstrativos de um ticker.
    Retorna o dict de dados, ou None se o ticker for inválido ou os fetches falharem.
    """
    if not repo.is_ticker_valid(ticker):
        return None
    if not force and not _needs_update(ticker):
        return repo.get_financials(ticker)

    data = fetch_financials(ticker)
    if data is not None:
        repo.save_financials(ticker, data)
    return data


def update_all(tickers: Optional[List[str]] = None, force: bool = False) -> dict:
    """
    Atualiza demonstrativos de todos os tickers válidos (ou lista fornecida).

    Progresso impresso por ticker:
        [   1/234] BBAS3        DRE=10anos  CF=4anos  OK
        [   2/234] ABCD3        SKIP (recente)
        [   3/234] XYZW3        FALHA

    Retorna dict {ticker: entry_or_None}.
    """
    if tickers is None:
        tickers = repo.get_valid_tickers()
        if not tickers:
            tickers = repo.get_tickers_list()

    results: dict = {}
    total = len(tickers)

    for i, ticker in enumerate(tickers, 1):
        # Checagem de skip antecipada para evitar chamadas HTTP desnecessárias
        if not force and not _needs_update(ticker):
            results[ticker] = repo.get_financials(ticker)
            print(f"[{i:4d}/{total}] {ticker:<12} SKIP (recente)")
            continue

        entry = update_ticker(ticker, force=force)
        results[ticker] = entry

        if entry:
            dre_data  = entry.get("dre", {})
            # Conta anos disponíveis a partir do primeiro campo de dados da DRE
            dre_key   = next((k for k in dre_data if not k.startswith("_")), None)
            dre_years = len(dre_data.get(dre_key, {})) if dre_key else 0
            cf_years  = len(entry.get("fluxo_caixa", {}).get("fco", {}))
            print(f"[{i:4d}/{total}] {ticker:<12} DRE={dre_years}anos  CF={cf_years}anos  OK")
        else:
            print(f"[{i:4d}/{total}] {ticker:<12} FALHA")

    success = sum(1 for v in results.values() if v is not None)
    print(f"\nConcluído: {success}/{total} demonstrativos atualizados.")
    return results


if __name__ == "__main__":
    flags   = [a for a in sys.argv[1:] if a.startswith("--")]
    args    = [a for a in sys.argv[1:] if not a.startswith("--")]
    force   = "--force" in flags
    do_update = "--update" in flags

    if do_update:
        current_year = datetime.now().year
        stale = get_stale_tickers(min_gap=2)
        if not stale:
            print("Nenhum ticker defasado encontrado (todos com dados ate %d ou mais recente)." % (current_year - 1))
        else:
            skip_note = "" if force else "  (use --force para reprocessar os buscados recentemente)"
            print("Tickers defasados detectados (%d):%s" % (len(stale), skip_note))
            for ticker, ultimo_ano in stale:
                faltam = list(range(ultimo_ano + 1, current_year))
                print("  %-12s ultimo=%d  faltam=%s" % (ticker, ultimo_ano, faltam))
            print("")
            tickers_stale = [t for t, _ in stale]
            update_all(tickers=tickers_stale, force=force)
    else:
        tickers_arg = [t.upper() for t in args] if args else None
        update_all(tickers=tickers_arg, force=force)
