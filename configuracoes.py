"""Configuração central do projeto.

Lê o arquivo .env (via python-dotenv)
Credenciais nunca ficam no código: vêm somente de variáveis de ambiente.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

from excecoes import ErroConfiguracao

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
ARQUIVO_AMBIENTE = RAIZ_PROJETO / ".env"
load_dotenv(ARQUIVO_AMBIENTE)


def obter_variavel_ambiente(nome, valor_padrao=None, obrigatoria=False):
    """Lê uma variável de ambiente; se for obrigatória e estiver vazia, interrompe com erro claro."""
    valor = os.getenv(nome, valor_padrao)
    if obrigatoria and not valor:
        raise ErroConfiguracao(f"Variável de ambiente ausente: {nome} (defina no arquivo .env)")
    return valor


def _obter_numero_inteiro(nome, valor_padrao):
    """Lê uma variável de ambiente numérica e valida o formato."""
    valor = obter_variavel_ambiente(nome, str(valor_padrao))
    try:
        return int(valor)
    except ValueError as erro:
        raise ErroConfiguracao(f"{nome} deve ser um número inteiro (valor recebido: {valor!r})") from erro


# ----- API do Mercado Livre -----
URL_BASE_API = obter_variavel_ambiente("ML_URL", "https://api.mercadolibre.com")
URL_AUTORIZACAO = obter_variavel_ambiente(
    "ML_URL_AUTORIZACAO", "https://auth.mercadolibre.com.ar/authorization"
)
IDENTIFICADOR_SITE = obter_variavel_ambiente("ML_SITE_ID", "MLA")  # MLA = Argentina
TEMPO_LIMITE_SEGUNDOS = _obter_numero_inteiro("ML_TIMEOUT", 15)

# ----- Endpoints -----
ENDPOINT_AUTENTICACAO = obter_variavel_ambiente("ML_AUTH", "oauth/token")
ENDPOINT_PRODUTOS = obter_variavel_ambiente("ML_PRODUCTS", "products")
ENDPOINT_BUSCA = obter_variavel_ambiente("ML_SEARCH", "search")
ENDPOINT_ITENS = obter_variavel_ambiente("ML_ITEMS", "items")
ENDPOINT_MOEDAS = obter_variavel_ambiente("ML_CURRENCIES", "currencies")
ENDPOINT_CONVERSAO_MOEDAS = obter_variavel_ambiente("ML_CURRENCY", "currency_conversions")

# ----- Produto pesquisado e paginação -----
TERMO_BUSCA = obter_variavel_ambiente("ML_SEARCH_QUERY", "Samsung Galaxy S24")
DOMINIO_PRODUTO = obter_variavel_ambiente("ML_SEARCH_DOMAIN", "MLA-CELLPHONES")
TAMANHO_PAGINA = _obter_numero_inteiro("ML_SEARCH_PAGE_SIZE", 50)  # exigência do desafio: 50
LIMITE_TOTAL_REGISTROS = _obter_numero_inteiro("ML_LIMITE_REGISTROS", 0)  # 0 = sem limite

# ----- Opções do ETL -----
MOEDA_DESTINO = obter_variavel_ambiente("ML_MOEDA_DESTINO", "USD")

# ----- Pastas e arquivos do projeto -----
PASTA_BANCO_DADOS = RAIZ_PROJETO / "[006] - Banco de Dados"
PASTA_INTERMEDIARIOS = PASTA_BANCO_DADOS / "intermediarios"
PASTA_CONSULTAS = RAIZ_PROJETO / "[007] - Consultas SQL"
PASTA_LOGS = RAIZ_PROJETO / "[008] - Utilitarios" / "logs"
PASTA_DOCUMENTACAO = RAIZ_PROJETO / "[009] - Documentacao"

CAMINHO_BANCO_DADOS = PASTA_BANCO_DADOS / obter_variavel_ambiente("ML_DATABASE", "mercado_livre.db")
ARQUIVO_ESQUEMA_SQL = PASTA_BANCO_DADOS / "ddl.sql"
ARQUIVO_CONSULTAS_SQL = PASTA_CONSULTAS / "consultas.sql"
ARQUIVO_RESULTADOS = PASTA_DOCUMENTACAO / "Resultados da Ultima Execucao.md"
ARQUIVO_EXTRACAO = PASTA_INTERMEDIARIOS / "1_extracao.json"
ARQUIVO_TRANSFORMACAO = PASTA_INTERMEDIARIOS / "2_transformacao.json"
