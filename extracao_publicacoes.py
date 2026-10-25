"""Extração dos produtos de catálogo e de suas publicações (somente novas)."""
import logging

from cliente_api import percorrer_paginas
from configuracoes import (
    ENDPOINT_BUSCA, ENDPOINT_ITENS, ENDPOINT_PRODUTOS, URL_BASE_API,
)
from excecoes import ErroApi

REGISTRO = logging.getLogger(__name__)


def extrair_publicacoes(termo_busca, identificador_site, dominio_produto,
                        tamanho_pagina, limite_total_registros=0):
    """Retorna as publicações novas dos produtos que correspondem ao termo e ao domínio."""
    publicacoes = []
    itens_ja_vistos = set()
    url_busca_produtos = f"{URL_BASE_API}/{ENDPOINT_PRODUTOS}/{ENDPOINT_BUSCA}"
    parametros_busca = {"status": "active", "q": termo_busca, "site_id": identificador_site}

    # Percorre os produtos do catálogo
    for produto in percorrer_paginas(url_busca_produtos, parametros_busca, tamanho_pagina):
        if produto.get("domain_id") != dominio_produto:
            continue

        identificador_produto = produto["id"]
        url_itens_do_produto = f"{URL_BASE_API}/{ENDPOINT_PRODUTOS}/{identificador_produto}/{ENDPOINT_ITENS}"
        try:
            # Percorre as publicações de cada produto
            for item in percorrer_paginas(url_itens_do_produto, {}, tamanho_pagina):
                identificador_item = item.get("item_id")
                eh_produto_novo = item.get("condition") == "new"
                if not eh_produto_novo or not identificador_item or identificador_item in itens_ja_vistos:
                    continue
                itens_ja_vistos.add(identificador_item)
                publicacoes.append({
                    "product_id": identificador_produto,
                    "product_name": produto.get("name"),
                    "item_id": identificador_item,
                    "seller_id": item.get("seller_id"),
                    "price": item.get("price"),
                    "currency_id": item.get("currency_id"),
                    "condition": item.get("condition"),
                    "warranty": item.get("warranty"),
                    "listing_type_id": item.get("listing_type_id"),
                    "shipping": item.get("shipping"),
                    "sale_terms": item.get("sale_terms"),
                })
                if limite_total_registros and len(publicacoes) >= limite_total_registros:
                    REGISTRO.info("Limite de %s registros atingido.", limite_total_registros)
                    return publicacoes
        except ErroApi as erro:
            REGISTRO.warning("Produto %s ignorado: %s", identificador_produto, erro)

    REGISTRO.info("Publicações novas extraídas: %s", len(publicacoes))
    return publicacoes
