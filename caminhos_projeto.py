"""Registra as pastas numeradas no caminho de importação do Python.

As pastas "[001] - Configuracoes", "[002] - Autenticacao API" etc. têm colchetes e
espaços no nome, então não podem ser importadas como pacotes. Por isso cada
pasta é adicionada ao caminho de importação e os módulos são importados
diretamente pelo nome do arquivo (ex.: `from configuracoes import URL_BASE_API`).
"""
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent


def registrar_pastas_do_projeto():
    """Adiciona cada pasta numerada ao caminho de importação."""
    for pasta in sorted(RAIZ_PROJETO.glob("[[]0*] - *")):
        if pasta.is_dir() and str(pasta) not in sys.path:
            sys.path.insert(0, str(pasta))


registrar_pastas_do_projeto()
