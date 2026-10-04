"""
Testes de portfolio_service.load_tickers — lista leve dos tickers em custódia.

Usada pelo Screening para destacar as linhas dos ativos que estão na carteira,
sem o custo de load() (que busca preços e cruza valuations).

Cobertura:
  1. retorna os tickers com quantidade > 0, em maiúsculas, sem duplicatas
  2. ignora cabeçalho, linhas malformadas e posições zeradas
  3. sem arquivo B3, devolve lista vazia em vez de quebrar
"""

from services import portfolio_service


class _FakeSheet:
    def __init__(self, rows):
        self._rows = rows
        self.nrows = len(rows)

    def row_values(self, i):
        return self._rows[i]


class _FakeBook:
    def __init__(self, rows):
        self._sheet = _FakeSheet(rows)

    def sheet_by_index(self, i):
        return self._sheet


def _patch_b3(monkeypatch, rows):
    monkeypatch.setattr(portfolio_service, "_find_b3_file", lambda: "/fake/custodia.xls")
    monkeypatch.setattr(portfolio_service.xlrd, "open_workbook", lambda path: _FakeBook(rows))


def test_returns_held_tickers_deduplicated(monkeypatch):
    _patch_b3(monkeypatch, [
        ["Produto", "Inst", "Código", "Qtd", "PM", "Total", "Ret"],
        ["", "", "pomo4", 100.0, 4.0, 400.0, 33.0],
        ["", "", "BRAP4", 50.0, 20.0, 1000.0, 38.0],
        ["", "", "POMO4", 20.0, 4.2, 84.0, 2.6],     # mesma ação em outra corretora
        ["", "", "MXRF11", 10.0, 10.0, 100.0, 0.0],  # FII também está em custódia
    ])
    assert portfolio_service.load_tickers() == ["BRAP4", "MXRF11", "POMO4"]


def test_skips_invalid_and_zeroed_rows(monkeypatch):
    _patch_b3(monkeypatch, [
        ["Produto", "Inst", "Código", "Qtd", "PM", "Total", "Ret"],
        ["", "", "UNIP6", 0.0, 50.0, 0.0, 0.0],       # posição zerada
        ["", "", "", 10.0, 5.0, 50.0, 0.0],            # sem ticker
        ["", "", "VALE3", "n/d", 70.0, 0.0, 0.0],      # quantidade inválida
        ["Total"],                                      # linha curta
        ["", "", "LREN3", 30.0, 11.0, 330.0, 10.0],
    ])
    assert portfolio_service.load_tickers() == ["LREN3"]


def test_no_b3_file_returns_empty(monkeypatch):
    monkeypatch.setattr(portfolio_service, "_find_b3_file", lambda: None)
    assert portfolio_service.load_tickers() == []
