"""Exceções do projeto, organizadas em uma única hierarquia."""


class ErroPipeline(Exception):
    """Erro base do pipeline ETL."""


class ErroConfiguracao(ErroPipeline):
    """Variável de ambiente ausente ou inválida."""


class ErroAutenticacao(ErroPipeline):
    """Falha ao obter ou renovar os tokens de acesso."""


class ErroBancoDados(ErroPipeline):
    """Falha de acesso ao banco de dados."""


class ErroEtapaAnterior(ErroPipeline):
    """Arquivo intermediário da etapa anterior não encontrado."""


class ErroApi(ErroPipeline):
    """Falha em chamada à API do Mercado Livre."""

    def __init__(self, url, codigo_http=None, detalhe=""):
        self.url = url
        self.codigo_http = codigo_http
        self.detalhe = detalhe
        super().__init__(f"Falha na API (HTTP {codigo_http}) em {url}: {detalhe}")
