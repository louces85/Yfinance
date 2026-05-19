"""
Fixtures compartilhadas entre todos os testes do backend.
"""

import sys
import os

# Garante que o diretório backend está no path para todos os testes
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Imprime resumo estilo JUnit ao final da execução."""
    stats = terminalreporter.stats
    passed  = len(stats.get("passed",  []))
    failed  = len(stats.get("failed",  []))
    error   = len(stats.get("error",   []))
    skipped = len(stats.get("skipped", []))
    total   = passed + failed + error + skipped

    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    print(f"  Tests run : {total}")
    print(f"  Passed    : {passed}")
    print(f"  Failures  : {failed}")
    print(f"  Errors    : {error}")
    print(f"  Skipped   : {skipped}")
    status = "OK" if failed == 0 and error == 0 else "FAILED"
    print(f"  Status    : {status}")
    print("=" * 60)
