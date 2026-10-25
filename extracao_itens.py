"""Enriquecimento das publicações com os detalhes do item (ex.: quantidade vendida)."""
import logging

from cliente_api import buscar_json
from configuracoes import ENDPOINT_ITENS, URL_BASE_API
from excecoes import ErroApi

REGISTRO = logging.getLogger(__name__)

TAMANHO_LOTE_ITENS = 20  # máximo de itens por chamada
CAMPOS_DETALHE_ITEM = (
    "id,seller_id,price,currency_id,sold_quantity,listing_type_id,shipping,sale_terms,warranty"
)


def extrair_detalhes_itens(identificadores_itens):
    """Busca os detalhes em lotes. Retorna {item_id: detalhes}; vazio se não houver permissão."""
    detalhes_por_item = {}
    for inicio in range(0, len(identificadores_itens), TAMANHO_LOTE_ITENS):
        lote = identificadores_itens[inicio:inicio + TAMANHO_LOTE_ITENS]
        try:
            respostas = buscar_json(
                f"{URL_BASE_API}/{ENDPOINT_ITENS}",
                {"ids": ",".join(lote), "attributes": CAMPOS_DETALHE_ITEM},
            )
        except ErroApi as erro:
            REGISTRO.warning("Detalhes de itens indisponíveis: %s", erro)
            if erro.codigo_http in (401, 403):
                REGISTRO.warning("Sem permissão em /items; a quantidade vendida ficará nula.")
                break  # evita repetir chamadas que falhariam do mesmo jeito
            continue

        # Guarda apenas os itens retornados com sucesso
        for resposta in respostas:
            corpo = resposta.get("body") or {}
            if resposta.get("code") == 200 and corpo.get("id"):
                detalhes_por_item[corpo["id"]] = corpo

    REGISTRO.info("Detalhes obtidos: %s de %s itens", len(detalhes_por_item), len(identificadores_itens))
    return detalhes_por_item


def mesclar_detalhes(publicacoes, detalhes_por_item):
    """Complementa cada publicação com os campos não nulos do detalhe do item."""
    for publicacao in publicacoes:
        detalhe = detalhes_por_item.get(publicacao["item_id"], {})
        publicacao.update({
            campo: valor for campo, valor in detalhe.items()
            if valor is not None and campo != "id"
        })
    return publicacoes
