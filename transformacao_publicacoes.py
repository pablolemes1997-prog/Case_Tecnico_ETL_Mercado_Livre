"""Transformação: publicações brutas da API -> tabelas no formato do banco de dados."""
from regras_garantia import extrair_texto_garantia, possui_garantia

COLUNAS_PRODUTOS = ["JOB_RUN", "product_id", "product_name"]
COLUNAS_COTACOES = ["JOB_RUN", "currency_id", "usd_rate"]
COLUNAS_PUBLICACOES = [
    "JOB_RUN", "item_id", "product_id", "seller_id", "price", "currency_id", "price_usd",
    "condition", "warranty", "has_warranty", "listing_type_id", "shipping_mode",
    "shipping_logistic_type", "shipping_free", "sold_quantity",
]


def formatar_job_run(data_execucao):
    """Texto padrão do JOB_RUN (mesmo valor para todos os registros da execução)."""
    return data_execucao.isoformat(sep=" ", timespec="seconds")


def transformar_publicacoes(publicacoes, taxas_conversao, data_execucao):
    """Gera as listas de registros das tabelas produtos, cotações e publicações."""
    job_run = formatar_job_run(data_execucao)
    produtos_por_identificador = {}
    registros_publicacoes = []

    # Percorre as publicações brutas
    for publicacao in publicacoes:
        identificador_produto = publicacao.get("product_id")
        produtos_por_identificador.setdefault(identificador_produto, {
            "JOB_RUN": job_run,
            "product_id": identificador_produto,
            "product_name": publicacao.get("product_name"),
        })

        dados_envio = publicacao.get("shipping") or {}
        texto_garantia = extrair_texto_garantia(publicacao)
        preco = publicacao.get("price")
        moeda = publicacao.get("currency_id")
        taxa_conversao = taxas_conversao.get(moeda)
        preco_em_dolar = round(preco * taxa_conversao, 2) if preco is not None and taxa_conversao is not None else None

        registros_publicacoes.append({
            "JOB_RUN": job_run,
            "item_id": publicacao.get("item_id"),
            "product_id": identificador_produto,
            "seller_id": publicacao.get("seller_id"),
            "price": preco,
            "currency_id": moeda,
            "price_usd": preco_em_dolar,
            "condition": publicacao.get("condition"),
            "warranty": texto_garantia,
            "has_warranty": int(possui_garantia(texto_garantia)),
            "listing_type_id": publicacao.get("listing_type_id"),
            "shipping_mode": dados_envio.get("mode"),
            "shipping_logistic_type": dados_envio.get("logistic_type"),
            "shipping_free": dados_envio.get("free_shipping"),
            "sold_quantity": publicacao.get("sold_quantity"),
        })

    cotacoes = [
        {"JOB_RUN": job_run, "currency_id": moeda, "usd_rate": taxa}
        for moeda, taxa in taxas_conversao.items() if moeda
    ]
    return {
        "produtos": list(produtos_por_identificador.values()),
        "cotacoes": cotacoes,
        "publicacoes": registros_publicacoes,
    }
