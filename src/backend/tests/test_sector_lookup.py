"""
Testes da classificação setorial derivada do all_indicators.json.

O all_sectors.json foi eliminado: setor/subsetor/segmento saem do próprio
export do StatusInvest, que cobre 100% dos tickers por construção (ticker sem
registro de indicadores é descartado pelo valuation antes do ranking).

Cobertura:
  1. normalização de nomes (rules.SECTOR_NAME_FIXES)
     - ponto usado no lugar de vírgula é corrigido
     - abreviações legítimas ("Máq. e Equip.", "Soc. Crédito") ficam intactas
     - nomes de setor antigos do export mapeados para a nomenclatura da UI
  2. get_all_sectors / get_sector
  3. _is_best sobre a classificação derivada, incluindo os casos que mudaram
     ao abandonar o arquivo curado (ITSA4, RPAD3, OPCT3)
  4. integração com o all_indicators.json real: cobertura total
"""

import pytest

from config import rules
from repositories import stock_repository as repo
from services.decision_service import _is_best, _lookup_sector


def _indicator(ticker, setor, subsetor, segmento):
    return {
        "ticker": ticker,
        "sectorname": setor,
        "subsectorname": subsetor,
        "segmentname": segmento,
    }


FAKE_INDICATORS = [
    _indicator("PETR4", "Petróleo. Gás e Biocombustíveis",
               "Petróleo. Gás e Biocombustíveis", "Exploração. Refino e Distribuição"),
    _indicator("ITUB4", "Financeiro e Outros", "Intermediários Financeiros", "Bancos"),
    _indicator("ITSA4", "Financeiro e Outros", "Intermediários Financeiros", "Bancos"),
    _indicator("RPAD3", "Financeiro e Outros", "Intermediários Financeiros", "Bancos"),
    _indicator("OPCT3", "Bens Industriais", "Transporte", "Transporte Hidroviário"),
    _indicator("VIVT3", "Comunicações", "Telecomunicações", "Telecomunicações"),
    _indicator("TAEE11", "Utilidade Pública", "Energia Elétrica",
               "Energia Elétrica"),
    _indicator("SAPR11", "Utilidade Pública", "Água e Saneamento", "Água e Saneamento"),
    _indicator("PSSA3", "Financeiro e Outros", "Previdência e Seguros", "Seguradoras"),
    _indicator("ROMI3", "Bens Industriais", "Máquinas e Equipamentos",
               "Máq. e Equip. Industriais"),
    _indicator("BRIV4", "Financeiro e Outros", "Intermediários Financeiros",
               "Soc. Crédito e Financiamento"),
    _indicator("GRND3", "Consumo Cíclico", "Tecidos. Vestuário e Calçados", "Calçados"),
]


@pytest.fixture
def indicators(monkeypatch):
    """Substitui o all_indicators.json por um conjunto sintético."""
    monkeypatch.setattr(repo, "get_all_indicators", lambda: list(FAKE_INDICATORS))
    monkeypatch.setattr(
        repo, "get_indicators_by_ticker",
        lambda t: next((i for i in FAKE_INDICATORS
                        if i["ticker"] == t.upper()), None),
    )


# ---------------------------------------------------------------------------
# Normalização de nomes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bruto,esperado", [
    ("Petróleo. Gás e Biocombustíveis",   "Petróleo, Gás e Biocombustíveis"),
    ("Exploração. Refino e Distribuição", "Exploração, Refino e Distribuição"),
    ("Motores . Compressores e Outros",   "Motores, Compressores e Outros"),
    ("Tecidos. Vestuário e Calçados",     "Tecidos, Vestuário e Calçados"),
    ("Jornais. Livros e Revistas",        "Jornais, Livros e Revistas"),
    ("Financeiro e Outros",               "Financeiro"),
    ("Comunicações",                      "Telecomunicações"),
])
def test_corrige_nomes_do_export(bruto, esperado):
    assert repo._fix_sector_name(bruto) == esperado


@pytest.mark.parametrize("nome", [
    "Máq. e Equip. Industriais",          # abreviação legítima
    "Máq. e Equip. Construção e Agrícolas",
    "Soc. Crédito e Financiamento",
    "Bens Industriais",                   # nome sem ponto
    "Energia Elétrica",
])
def test_preserva_nomes_que_nao_devem_mudar(nome):
    assert repo._fix_sector_name(nome) == nome


def test_nome_ausente_vira_string_vazia():
    assert repo._fix_sector_name(None) == ""
    assert repo._fix_sector_name("") == ""


def test_todo_fix_e_idempotente():
    """Aplicar a correção duas vezes não pode alterar o resultado."""
    for bruto in rules.SECTOR_NAME_FIXES:
        uma = repo._fix_sector_name(bruto)
        assert repo._fix_sector_name(uma) == uma


# ---------------------------------------------------------------------------
# get_all_sectors / get_sector
# ---------------------------------------------------------------------------

def test_get_all_sectors_cobre_todos_os_tickers(indicators):
    sectors = repo.get_all_sectors()

    assert len(sectors) == len(FAKE_INDICATORS)
    assert sectors["PETR4"] == {
        "setor":    "Petróleo, Gás e Biocombustíveis",
        "subsetor": "Petróleo, Gás e Biocombustíveis",
        "segmento": "Exploração, Refino e Distribuição",
    }


def test_get_sector_por_ticker(indicators):
    assert repo.get_sector("vivt3") == {
        "setor":    "Telecomunicações",
        "subsetor": "Telecomunicações",
        "segmento": "Telecomunicações",
    }


def test_get_sector_ticker_desconhecido(indicators):
    assert repo.get_sector("NAOEXISTE3") == {}


def test_lookup_sector_e_case_insensitive(indicators):
    sectors = repo.get_all_sectors()

    assert _lookup_sector("itub4", sectors)["segmento"] == "Bancos"
    assert _lookup_sector("NAOEXISTE3", sectors) == {}


# ---------------------------------------------------------------------------
# BEST (Barsi) sobre a classificação derivada
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ticker,esperado", [
    ("ITUB4",  True),   # Bancos
    ("TAEE11", True),   # Energia Elétrica
    ("SAPR11", True),   # Água e Saneamento
    ("PSSA3",  True),   # Previdência e Seguros
    ("ITSA4",  True),   # holding classificada como Banco — decisão do usuário
    ("RPAD3",  True),   # idem
    ("OPCT3",  False),  # marítima: o arquivo curado a marcava como saneamento
    ("PETR4",  False),
    ("GRND3",  False),
])
def test_is_best_sobre_setor_derivado(indicators, ticker, esperado):
    sectors = repo.get_all_sectors()

    assert _is_best(_lookup_sector(ticker, sectors)) is esperado


def test_is_best_sem_setor_e_falso():
    assert _is_best({}) is False


# ---------------------------------------------------------------------------
# Integração com o all_indicators.json real
# ---------------------------------------------------------------------------

class TestArquivoReal:
    """Propriedades que valem para qualquer export, sem travar números."""

    def test_todo_ticker_do_export_tem_setor(self):
        sectors = repo.get_all_sectors()

        assert sectors, "all_indicators.json vazio"
        sem_setor = [t for t, s in sectors.items() if not s.get("setor")]
        assert sem_setor == []

    def test_nenhum_nome_normalizado_sobra_no_resultado(self):
        """Nenhum nome cru do export pode escapar da normalização."""
        sectors = repo.get_all_sectors()

        crus = set(rules.SECTOR_NAME_FIXES)
        usados = set()
        for info in sectors.values():
            usados |= set(info.values())
        assert usados & crus == set()
