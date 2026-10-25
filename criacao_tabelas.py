"""Criação das tabelas a partir do arquivo ddl.sql (fonte única do modelo)."""
from conexao_banco import conectar_banco
from configuracoes import ARQUIVO_ESQUEMA_SQL


def criar_tabelas():
    """Executa o DDL. Pode rodar várias vezes: usa CREATE ... IF NOT EXISTS."""
    with conectar_banco() as conexao:
        conexao.executescript(ARQUIVO_ESQUEMA_SQL.read_text(encoding="utf-8"))
