"""Conexão com o banco SQLite, com commit e rollback automáticos."""
import sqlite3
from contextlib import contextmanager

import configuracoes
from excecoes import ErroBancoDados


@contextmanager
def conectar_banco():
    """Abre a conexão, confirma as alterações ao final e desfaz tudo em caso de erro."""
    caminho_banco = configuracoes.CAMINHO_BANCO_DADOS
    try:
        caminho_banco.parent.mkdir(parents=True, exist_ok=True)
        conexao = sqlite3.connect(caminho_banco)
        conexao.execute("PRAGMA foreign_keys = ON")  # faz o SQLite respeitar as chaves estrangeiras
    except (sqlite3.Error, OSError) as erro:
        raise ErroBancoDados(f"Não foi possível abrir {caminho_banco}: {erro}") from erro
    try:
        yield conexao
        conexao.commit()
    except sqlite3.Error as erro:
        conexao.rollback()
        raise ErroBancoDados(str(erro)) from erro
    finally:
        conexao.close()
