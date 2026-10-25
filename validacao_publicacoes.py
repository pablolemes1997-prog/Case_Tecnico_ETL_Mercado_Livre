"""Validação de qualidade dos dados antes da carga no banco."""
import logging

REGISTRO = logging.getLogger(__name__)

CAMPOS_OBRIGATORIOS = ("item_id", "product_id", "seller_id")


def validar_tabelas(tabelas):
    """Remove publicações sem campos obrigatórios ou duplicadas e mantém as tabelas coerentes."""
    publicacoes_validas = []
    itens_ja_vistos = set()
    for publicacao in tabelas["publicacoes"]:
        faltam_campos = any(publicacao.get(campo) is None for campo in CAMPOS_OBRIGATORIOS)
        if faltam_campos or publicacao["item_id"] in itens_ja_vistos:
            continue
        itens_ja_vistos.add(publicacao["item_id"])
        publicacoes_validas.append(publicacao)

    descartadas = len(tabelas["publicacoes"]) - len(publicacoes_validas)
    if descartadas:
        REGISTRO.warning("Publicações descartadas na validação: %s", descartadas)

    # Mantém apenas produtos e moedas usados pelas publicações (respeita as chaves estrangeiras)
    produtos_usados = {publicacao["product_id"] for publicacao in publicacoes_validas}
    moedas_usadas = {publicacao["currency_id"] for publicacao in publicacoes_validas}
    return {
        "produtos": [p for p in tabelas["produtos"] if p["product_id"] in produtos_usados],
        "cotacoes": [c for c in tabelas["cotacoes"] if c["currency_id"] in moedas_usadas],
        "publicacoes": publicacoes_validas,
    }
