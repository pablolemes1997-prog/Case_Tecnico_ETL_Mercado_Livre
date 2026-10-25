"""Gera tokens de acesso quando for necessário (apoio à autenticação).

Uso:
    python autenticar.py --url              # mostra a URL para autorizar a aplicação
    python autenticar.py --codigo TG-xxxx   # troca o code por tokens e grava no .env
"""
import caminhos_projeto  # noqa: F401  (registra as pastas numeradas)

import argparse
import sys

from autenticacao_oauth import gerar_url_autorizacao, trocar_codigo_por_tokens
from configuracoes import obter_variavel_ambiente
from excecoes import ErroPipeline
from logs import configurar_logs


def principal():
    configurar_logs()
    leitor_argumentos = argparse.ArgumentParser(description="Obtém tokens do Mercado Livre")
    leitor_argumentos.add_argument("--url", action="store_true", help="exibe a URL de autorização")
    leitor_argumentos.add_argument("--codigo", help="code retornado após a autorização")
    argumentos = leitor_argumentos.parse_args()

    try:
        uri_redirecionamento = obter_variavel_ambiente("ML_REDIRECT_URI")
        if argumentos.url:
            if not uri_redirecionamento:
                print("Defina ML_REDIRECT_URI no .env para gerar a URL.")
                return 1
            print(gerar_url_autorizacao(uri_redirecionamento))
            return 0
        codigo = argumentos.codigo or obter_variavel_ambiente("ML_CODE") or input("Cole o code: ")
        trocar_codigo_por_tokens(codigo, uri_redirecionamento)
        print("Tokens salvos no .env.")
        return 0
    except ErroPipeline as erro:
        print(f"Erro: {erro}")
        return 1


if __name__ == "__main__":
    sys.exit(principal())
