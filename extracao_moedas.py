"""Moedas (/currencies) e taxas de conversão (/currency_conversions)."""
import logging

from cliente_api import buscar_json
from configuracoes import (
    ENDPOINT_BUSCA, ENDPOINT_CONVERSAO_MOEDAS, ENDPOINT_MOEDAS, URL_BASE_API,
)
from excecoes import ErroApi

REGISTRO = logging.getLogger(__name__)


def listar_moedas():
    """Lista as moedas suportadas pelo Mercado Livre."""
    return buscar_json(f"{URL_BASE_API}/{ENDPOINT_MOEDAS}")


def validar_moedas(identificadores_moedas):
    """Avisa (sem interromper) se alguma moeda não constar em /currencies."""
    try:
        moedas_validas = {moeda["id"] for moeda in listar_moedas()}
    except (ErroApi, KeyError, TypeError) as erro:
        REGISTRO.warning("Não foi possível validar as moedas: %s", erro)
        return
    for identificador_moeda in identificadores_moedas:
        if identificador_moeda not in moedas_validas:
            REGISTRO.warning("Moeda %s não consta em /currencies.", identificador_moeda)


def obter_taxa_conversao(moeda_origem, moeda_destino):
    """Taxa de conversão de uma moeda para outra (None se estiver indisponível)."""
    if moeda_origem == moeda_destino:
        return 1.0
    url = f"{URL_BASE_API}/{ENDPOINT_CONVERSAO_MOEDAS}/{ENDPOINT_BUSCA}"
    try:
        dados = buscar_json(url, {"from": moeda_origem, "to": moeda_destino})
    except ErroApi as erro:
        REGISTRO.warning("Sem taxa %s -> %s: %s", moeda_origem, moeda_destino, erro)
        return None
    taxa = dados.get("rate", dados.get("ratio"))
    return float(taxa) if taxa is not None else None


def obter_taxas_conversao(moedas_origem, moeda_destino):
    """Busca uma taxa para cada moeda distinta (uma chamada por moeda)."""
    return {moeda: obter_taxa_conversao(moeda, moeda_destino) for moeda in set(moedas_origem)}
