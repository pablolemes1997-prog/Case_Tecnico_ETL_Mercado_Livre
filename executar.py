"""Ponto de entrada do ETL.

Uso:
    python executar.py                          # pipeline completo
    python executar.py --etapa extracao         # só extração  -> grava 1_extracao.json
    python executar.py --etapa transformacao    # só transformação -> grava 2_transformacao.json
    python executar.py --etapa carga            # só carga no banco
    python executar.py --etapa consultas        # roda as consultas SQL e grava os resultados
"""
import caminhos_projeto  # noqa: F401  (registra as pastas numeradas)

import argparse
import logging
import sys
from datetime import datetime

from arquivos import ler_json, salvar_json
from autenticacao_oauth import garantir_tokens
from carga_publicacoes import carregar_tabelas
from configuracoes import (
    ARQUIVO_EXTRACAO, ARQUIVO_TRANSFORMACAO, DOMINIO_PRODUTO, IDENTIFICADOR_SITE,
    LIMITE_TOTAL_REGISTROS, MOEDA_DESTINO, TAMANHO_PAGINA, TERMO_BUSCA,
)
from criacao_tabelas import criar_tabelas
from excecoes import ErroPipeline
from executar_consultas import gerar_resultados
from extracao_itens import extrair_detalhes_itens, mesclar_detalhes
from extracao_moedas import obter_taxas_conversao, validar_moedas
from extracao_publicacoes import extrair_publicacoes
from logs import configurar_logs
from transformacao_publicacoes import transformar_publicacoes
from validacao_publicacoes import validar_tabelas

REGISTRO = logging.getLogger("etl")

CODIGO_SUCESSO = 0
CODIGO_ERRO = 1


def extrair(data_execucao):
    """Etapa 1 - Extração: busca publicações, detalhes e taxas de câmbio na API."""
    garantir_tokens()
    publicacoes = extrair_publicacoes(
        TERMO_BUSCA, IDENTIFICADOR_SITE, DOMINIO_PRODUTO, TAMANHO_PAGINA, LIMITE_TOTAL_REGISTROS
    )
    if not publicacoes:
        return None

    detalhes_por_item = extrair_detalhes_itens([publicacao["item_id"] for publicacao in publicacoes])
    mesclar_detalhes(publicacoes, detalhes_por_item)

    moedas = {publicacao["currency_id"] for publicacao in publicacoes if publicacao.get("currency_id")}
    validar_moedas(moedas | {MOEDA_DESTINO})
    return {
        "data_execucao": data_execucao.isoformat(),
        "publicacoes": publicacoes,
        "taxas_conversao": obter_taxas_conversao(moedas, MOEDA_DESTINO),
    }


def transformar(dados_extraidos):
    """Etapa 2 - Transformação: monta as tabelas e valida a qualidade dos dados."""
    tabelas = transformar_publicacoes(
        dados_extraidos["publicacoes"],
        dados_extraidos["taxas_conversao"],
        datetime.fromisoformat(dados_extraidos["data_execucao"]),
    )
    return validar_tabelas(tabelas)


def carregar(tabelas):
    """Etapa 3 - Carga: cria as tabelas (se preciso) e grava os dados no banco."""
    criar_tabelas()
    return carregar_tabelas(tabelas)


def executar_etapa(nome_etapa):
    """Executa a etapa pedida (ou o pipeline completo)."""
    data_execucao = datetime.now()  # vira o JOB_RUN de toda a execução

    if nome_etapa in ("completo", "extracao"):
        dados_extraidos = extrair(data_execucao)
        if dados_extraidos is None:
            REGISTRO.error("Nenhuma publicação extraída; nada será carregado.")
            return CODIGO_ERRO
        if nome_etapa == "extracao":
            REGISTRO.info("Extração salva em %s", salvar_json(dados_extraidos, ARQUIVO_EXTRACAO))
            return CODIGO_SUCESSO

    if nome_etapa == "transformacao":
        dados_extraidos = ler_json(ARQUIVO_EXTRACAO)

    if nome_etapa in ("completo", "transformacao"):
        tabelas = transformar(dados_extraidos)
        if nome_etapa == "transformacao":
            REGISTRO.info("Transformação salva em %s", salvar_json(tabelas, ARQUIVO_TRANSFORMACAO))
            return CODIGO_SUCESSO

    if nome_etapa == "carga":
        tabelas = ler_json(ARQUIVO_TRANSFORMACAO)

    if nome_etapa in ("completo", "carga"):
        total = carregar(tabelas)
        REGISTRO.info("Carga concluída: %s publicações (JOB_RUN=%s).", total,
                      tabelas["publicacoes"][0]["JOB_RUN"] if total else "-")

    if nome_etapa == "consultas":
        REGISTRO.info("Resultados gravados em %s", gerar_resultados())
    return CODIGO_SUCESSO


def principal():
    configurar_logs()
    leitor_argumentos = argparse.ArgumentParser(description="ETL Mercado Livre")
    leitor_argumentos.add_argument(
        "--etapa", default="completo",
        choices=["completo", "extracao", "transformacao", "carga", "consultas"],
        help="etapa a executar (padrão: completo)",
    )
    argumentos = leitor_argumentos.parse_args()
    try:
        return executar_etapa(argumentos.etapa)
    except ErroPipeline as erro:
        REGISTRO.error("Execução interrompida: %s", erro)
        return CODIGO_ERRO


if __name__ == "__main__":
    sys.exit(principal())
