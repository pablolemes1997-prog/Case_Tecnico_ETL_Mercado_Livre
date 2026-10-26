-- Modelo de dados do ETL Mercado Livre (SQLite).


-- Produtos do catálogo encontrados na busca.
CREATE TABLE IF NOT EXISTS etl_products (
    JOB_RUN      DATETIME NOT NULL,
    product_id   TEXT     NOT NULL,
    product_name TEXT,
    PRIMARY KEY (JOB_RUN, product_id)
);

-- Taxa de conversão para USD usada na execução (uma linha por moeda).
CREATE TABLE IF NOT EXISTS etl_currency_rates (
    JOB_RUN     DATETIME NOT NULL,
    currency_id TEXT     NOT NULL,
    usd_rate    REAL,
    PRIMARY KEY (JOB_RUN, currency_id)
);

-- Publicações (anúncios). Tabela central para responder às perguntas do desafio.
CREATE TABLE IF NOT EXISTS etl_publications (
    JOB_RUN                DATETIME NOT NULL,
    item_id                TEXT     NOT NULL,
    product_id             TEXT     NOT NULL,
    seller_id              INTEGER  NOT NULL,
    price                  REAL,
    currency_id            TEXT,
    price_usd              REAL,
    condition              TEXT,
    warranty               TEXT,
    has_warranty           INTEGER  NOT NULL CHECK (has_warranty IN (0, 1)),
    listing_type_id        TEXT,
    shipping_mode          TEXT,
    shipping_logistic_type TEXT,
    shipping_free          INTEGER  CHECK (shipping_free IN (0, 1)),
    sold_quantity          INTEGER,
    PRIMARY KEY (JOB_RUN, item_id),
    FOREIGN KEY (JOB_RUN, product_id)  REFERENCES etl_products (JOB_RUN, product_id),
    FOREIGN KEY (JOB_RUN, currency_id) REFERENCES etl_currency_rates (JOB_RUN, currency_id)
);

-- Índices que apoiam as consultas por vendedor e por produto dentro de uma execução.
CREATE INDEX IF NOT EXISTS idx_publications_seller  ON etl_publications (JOB_RUN, seller_id);
CREATE INDEX IF NOT EXISTS idx_publications_product ON etl_publications (JOB_RUN, product_id);
