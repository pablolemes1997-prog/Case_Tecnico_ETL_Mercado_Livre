"""Cliente HTTP"""

import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from autenticacao_oauth import renovar_token
from configuracoes import TEMPO_LIMITE_SEGUNDOS, obter_variavel_ambiente
from excecoes import ErroApi

REGISTRO = logging.getLogger(__name__)


def _criar_sessao():
    """Cria uma sessão reutilizável que tenta de novo em erros 429 - 5x."""
    politica_novas_tentativas = Retry(
        total=3, backoff_factor=1, raise_on_status=False,
        status_forcelist=(429, 500, 502, 503, 504), allowed_methods=("GET",),
    )
    sessao = requests.Session()
    sessao.mount("https://", HTTPAdapter(max_retries=politica_novas_tentativas))
    return sessao


_SESSAO = _criar_sessao()


def _montar_cabecalhos():
    token_acesso = obter_variavel_ambiente("ML_ACCESS_TOKEN", obrigatoria=True)
    return {"Authorization": f"Bearer {token_acesso}", "Accept": "application/json"}


def buscar_json(url, parametros=None, renovar_se_expirado=True):
    """Faz um GET autenticado; se a API responder 401, renova o token e tenta uma vez mais."""
    try:
        resposta = _SESSAO.get(
            url, headers=_montar_cabecalhos(), params=parametros, timeout=TEMPO_LIMITE_SEGUNDOS
        )
    except requests.RequestException as erro:
        raise ErroApi(url, detalhe=str(erro)) from erro

    if resposta.status_code == 401 and renovar_se_expirado:
        REGISTRO.info("Token expirado; renovando e repetindo a chamada.")
        renovar_token()
        return buscar_json(url, parametros, renovar_se_expirado=False)

    if not resposta.ok:
        raise ErroApi(url, resposta.status_code, resposta.text[:300])
    return resposta.json()


def percorrer_paginas(url, parametros, tamanho_pagina):
    """Devolve os registros de 'results' página a página (limit/offset)."""
    deslocamento = 0
    while True:
        dados = buscar_json(url, {**parametros, "limit": tamanho_pagina, "offset": deslocamento})
        registros_da_pagina = dados.get("results") or []
        yield from registros_da_pagina

        deslocamento += tamanho_pagina
        total_disponivel = (dados.get("paging") or {}).get("total")
        eh_ultima_pagina = len(registros_da_pagina) < tamanho_pagina
        if eh_ultima_pagina or (total_disponivel is not None and deslocamento >= total_disponivel):
            break
