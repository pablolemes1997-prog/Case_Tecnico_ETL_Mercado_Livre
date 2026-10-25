"""Carga dos dados tratados no banco de dados."""
import logging
import sqlite3

from conexao_banco import conectar_banco
from excecoes import ErroBancoDados
from transformacao_publicacoes import COLUNAS_COTACOES, COLUNAS_PRODUTOS, COLUNAS_PUBLICACOES

REGISTRO = logging.getLogger(__name__)

# Ordem importa: tabelas "pai" primeiro, por causa das chaves estrangeiras
TABELAS_DA_CARGA = (
    ("produtos", "etl_products", COLUNAS_PRODUTOS),
    ("cotacoes", "etl_currency_rates", COLUNAS_COTACOES),
    ("publicacoes", "etl_publications", COLUNAS_PUBLICACOES),
)


def _inserir_registros(conexao, nome_tabela, colunas, registros):
    """Insere uma lista de registros em uma tabela, em lote."""
    lista_colunas = ", ".join(colunas)
    parametros = ", ".join(f":{coluna}" for coluna in colunas)
    comando = f"INSERT INTO {nome_tabela} ({lista_colunas}) VALUES ({parametros})"
    conexao.executemany(comando, registros)


def carregar_tabelas(tabelas):
    """Grava produtos, cotações e publicações em uma única transação."""
    try:
        with conectar_banco() as conexao:
            for chave, nome_tabela, colunas in TABELAS_DA_CARGA:
                _inserir_registros(conexao, nome_tabela, colunas, tabelas[chave])
                REGISTRO.info("Tabela %s: %s registros gravados.", nome_tabela, len(tabelas[chave]))
    except ErroBancoDados as erro:
        if "UNIQUE" in str(erro):
            raise ErroBancoDados(
                "Esses dados já foram carregados (mesmo JOB_RUN). "
                "Execute a extração novamente para gerar uma nova execução."
            ) from erro
        raise
    except sqlite3.Error as erro:  # ex.: violação de chave estrangeira
        raise ErroBancoDados(f"Erro ao inserir dados: {erro}") from erro
    return len(tabelas["publicacoes"])
