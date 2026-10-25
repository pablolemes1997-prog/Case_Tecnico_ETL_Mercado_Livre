"""Autenticação OAuth 2.0 com o Mercado Livre.

Concentra tudo sobre credenciais: troca do code por tokens (1ª vez), renovação
do access token com o refresh token e gravação dos tokens no arquivo .env.
"""
import logging
import os
from urllib.parse import quote

import requests
from dotenv import set_key, unset_key

from configuracoes import (
    ARQUIVO_AMBIENTE, ENDPOINT_AUTENTICACAO, TEMPO_LIMITE_SEGUNDOS,
    URL_AUTORIZACAO, URL_BASE_API, obter_variavel_ambiente,
)
from excecoes import ErroAutenticacao

REGISTRO = logging.getLogger(__name__)


def gerar_url_autorizacao(uri_redirecionamento):
    """Monta a URL em que o usuário autoriza a aplicação e recebe o code."""
    identificador_aplicacao = obter_variavel_ambiente("ML_APP_ID", obrigatoria=True)
    return (
        f"{URL_AUTORIZACAO}?response_type=code&client_id={identificador_aplicacao}"
        f"&redirect_uri={quote(uri_redirecionamento, safe='')}"
    )


def limpar_codigo_autorizacao(codigo):
    """Remove parâmetros extras colados da URL (ex.: '&zx=...') e espaços."""
    return codigo.split("&")[0].strip()


def _gravar_tokens(resposta_api):
    """Grava os tokens no .env (uso futuro) e no ambiente do processo (uso imediato)."""
    campos = (("ML_ACCESS_TOKEN", "access_token"), ("ML_REFRESH_TOKEN", "refresh_token"))
    for nome_variavel, campo_resposta in campos:
        valor = resposta_api.get(campo_resposta)
        if valor:
            os.environ[nome_variavel] = valor
            set_key(str(ARQUIVO_AMBIENTE), nome_variavel, valor)


def _solicitar_token(corpo_requisicao):
    """Envia o pedido de token à API e grava o resultado."""
    url = f"{URL_BASE_API}/{ENDPOINT_AUTENTICACAO}"
    cabecalhos = {"accept": "application/json", "content-type": "application/x-www-form-urlencoded"}
    try:
        resposta = requests.post(
            url, headers=cabecalhos, data=corpo_requisicao, timeout=TEMPO_LIMITE_SEGUNDOS
        )
    except requests.RequestException as erro:
        raise ErroAutenticacao(f"Falha de rede ao obter o token: {erro}") from erro
    if not resposta.ok:
        raise ErroAutenticacao(f"HTTP {resposta.status_code}: {resposta.text[:300]}")
    dados = resposta.json()
    _gravar_tokens(dados)
    return dados


def trocar_codigo_por_tokens(codigo, uri_redirecionamento=None):
    """Primeira autenticação. O code é de uso único e expira em poucos minutos."""
    corpo_requisicao = {
        "grant_type": "authorization_code",
        "client_id": obter_variavel_ambiente("ML_APP_ID", obrigatoria=True),
        "client_secret": obter_variavel_ambiente("ML_CLIENT_SECRET", obrigatoria=True),
        "code": limpar_codigo_autorizacao(codigo),
    }
    if uri_redirecionamento:
        corpo_requisicao["redirect_uri"] = uri_redirecionamento
    return _solicitar_token(corpo_requisicao)


def renovar_token():
    """Renova o access token; o refresh token também é trocado a cada renovação."""
    dados = _solicitar_token({
        "grant_type": "refresh_token",
        "client_id": obter_variavel_ambiente("ML_APP_ID", obrigatoria=True),
        "client_secret": obter_variavel_ambiente("ML_CLIENT_SECRET", obrigatoria=True),
        "refresh_token": obter_variavel_ambiente("ML_REFRESH_TOKEN", obrigatoria=True),
    })
    REGISTRO.info("Token renovado.")
    return dados


def _consumir_codigo_autorizacao():
    """Troca o ML_CODE do .env por tokens e remove o code, que só vale uma vez."""
    dados = trocar_codigo_por_tokens(
        obter_variavel_ambiente("ML_CODE"), obter_variavel_ambiente("ML_REDIRECT_URI")
    )
    unset_key(str(ARQUIVO_AMBIENTE), "ML_CODE")
    os.environ.pop("ML_CODE", None)
    REGISTRO.info("Primeira autenticação concluída com o code.")
    return dados


def garantir_tokens():
    """Deixa um token válido: renova se houver refresh token; senão usa o ML_CODE."""
    if obter_variavel_ambiente("ML_REFRESH_TOKEN"):
        try:
            return renovar_token()
        except ErroAutenticacao:
            if not obter_variavel_ambiente("ML_CODE"):
                raise
            REGISTRO.warning("Renovação falhou; tentando o ML_CODE.")
            return _consumir_codigo_autorizacao()
    if obter_variavel_ambiente("ML_CODE"):
        return _consumir_codigo_autorizacao()
    raise ErroAutenticacao(
        "Sem ML_REFRESH_TOKEN nem ML_CODE no .env. Gere um code com: python autenticar.py --url"
    )
