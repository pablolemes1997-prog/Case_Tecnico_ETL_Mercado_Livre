# Dicionário de dados

**Autor: Pablo Felix**

## etl_products
| Campo | Tipo | Descrição |
|---|---|---|
| `JOB_RUN` (PK) | DATETIME | Data/hora da execução |
| `product_id` (PK) | TEXT | Produto de catálogo |
| `product_name` | TEXT | Nome do produto |

## etl_currency_rates
| Campo | Tipo | Descrição |
|---|---|---|
| `JOB_RUN` (PK) | DATETIME | Data/hora da execução |
| `currency_id` (PK) | TEXT | Moeda (ex.: ARS) |
| `usd_rate` | REAL | Taxa de conversão para USD usada na execução (nula se indisponível) |

## etl_publications
| Campo | Tipo | Descrição / regra |
|---|---|---|
| `JOB_RUN` (PK) | DATETIME | Igual para todos os registros da execução |
| `item_id` (PK) | TEXT | Publicação |
| `product_id` (FK) | TEXT | Produto (→ `etl_products`) |
| `seller_id` | INTEGER | Vendedor |
| `price` | REAL | Preço na moeda original |
| `currency_id` (FK) | TEXT | Moeda (→ `etl_currency_rates`) |
| `price_usd` | REAL | `price × usd_rate`, 2 casas; nulo sem taxa |
| `condition` | TEXT | Sempre `new` |
| `warranty` | TEXT | Texto da garantia (`warranty` ou `sale_terms`) |
| `has_warranty` | INTEGER | 1 se há texto e não é "Sin garantía"; senão 0 |
| `listing_type_id` | TEXT | Tipo de publicação |
| `shipping_mode` | TEXT | Modo de envio |
| `shipping_logistic_type` | TEXT | Tipo logístico |
| `shipping_free` | INTEGER | 1 = frete grátis |
| `sold_quantity` | INTEGER | Vendas; nulo se `/items` não é autorizado |

**Índices:** `(JOB_RUN, seller_id)` e `(JOB_RUN, product_id)` em `etl_publications`.
