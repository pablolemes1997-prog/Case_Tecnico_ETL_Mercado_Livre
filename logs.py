"""Configuração de logs: console e arquivo com rotação."""
import logging
from logging.handlers import RotatingFileHandler

from configuracoes import PASTA_LOGS


def configurar_logs():
    """Envia as mensagens de log para o console e para o arquivo etl.log."""
    registrador_raiz = logging.getLogger()
    if registrador_raiz.handlers:  # evita duplicar mensagens
        return
    PASTA_LOGS.mkdir(parents=True, exist_ok=True)
    formato = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
    destinos = [
        logging.StreamHandler(),
        RotatingFileHandler(PASTA_LOGS / "etl.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"),
    ]
    for destino in destinos:
        destino.setFormatter(formato)
        registrador_raiz.addHandler(destino)
    registrador_raiz.setLevel(logging.INFO)
