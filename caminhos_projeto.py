"""Registra as pastas numeradas no caminho de importação do Python."""

import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent


def registrar_pastas_do_projeto():
    """Adiciona cada pasta numerada ao caminho de importação."""
    for pasta in sorted(RAIZ_PROJETO.glob("[[]0*] - *")):
        if pasta.is_dir() and str(pasta) not in sys.path:
            sys.path.insert(0, str(pasta))


registrar_pastas_do_projeto()
