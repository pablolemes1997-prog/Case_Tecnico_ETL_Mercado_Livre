# [Respostas] - Desafio ETL Mercado Livre

**Autor: Pablo Felix**

Produto: Samsung Galaxy S24 · Site: MLA (Argentina) · Somente produtos novos · Tabela: `etl_publications`.

## Fonte das evidências

Os resultados abaixo foram obtidos na execução de **07/09/2026**, que carregou **16 publicações** (`JOB_RUN` = `2026-09-07 11:32:10`). Para reproduzir ou atualizar:

```bash
python executar.py                       # executa o ETL
python executar.py --etapa consultas     # grava "Resultados da Ultima Execucao.md" com as evidências
```

Todas as consultas usam somente a última execução: `WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications)`.

---

## Pergunta 1
**¿Hay algún vendedor con múltiples publicaciones? En caso de que sí, ¿con cuántas?**

**Resposta:** Sim. O vendedor `214988544` possui **2 publicações**.

```sql
SELECT seller_id, COUNT(*) AS publication_count
FROM etl_publications
WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications)
GROUP BY seller_id
HAVING COUNT(*) > 1
ORDER BY publication_count DESC;
```

**Lógica:** agrupa as publicações da última execução por vendedor e mantém só os grupos com mais de uma publicação (`HAVING COUNT(*) > 1`).

**Evidência:**

| seller_id | publication_count |
|---|---|
| 214988544 | 2 |

**Complemento — quantidade de publicações por vendedor:**

```sql
SELECT seller_id, COUNT(*) AS publication_count
FROM etl_publications
WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications)
GROUP BY seller_id
ORDER BY publication_count DESC, seller_id;
```

Como apenas um vendedor tem mais de uma publicação entre as 16, os demais vendedores têm 1 publicação cada. O detalhe por vendedor é gerado em `Resultados da Ultima Execucao.md`.

---

## Pergunta 2
**¿Promedio de ventas por seller?**

**Resposta:** **Indisponível** na execução de referência: o endpoint `/items`, que fornece a quantidade vendida (`sold_quantity`), retornou **HTTP 403** com as permissões da aplicação. O campo foi mantido nulo (sem estimativas) e a consulta está pronta para devolver a média por vendedor assim que houver permissão.

```sql
SELECT seller_id, ROUND(AVG(sold_quantity), 2) AS average_sales
FROM etl_publications
WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications)
  AND sold_quantity IS NOT NULL
GROUP BY seller_id
ORDER BY average_sales DESC;
```

**Lógica:** média da quantidade vendida das publicações de cada vendedor. Publicações com valor nulo ficam fora do cálculo para não tratar "sem informação" como "zero vendas".

**Evidência:** consulta retorna 0 linhas; o log da execução registra `Sem permissão em /items` (HTTP 403).

---

## Pergunta 3
**¿Cuál es el precio promedio en dólares?**

**Resposta:** **US$ 1.067,88**.

```sql
SELECT ROUND(AVG(price_usd), 2) AS average_price_usd
FROM etl_publications
WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications)
  AND price_usd IS NOT NULL;
```

**Lógica:** `price_usd` = preço original × taxa de conversão da moeda para USD (`/currency_conversions`, guardada em `etl_currency_rates`). A consulta calcula a média das publicações com preço convertido.

**Evidência:**

| average_price_usd |
|---|
| 1067.88 |

---

## Pergunta 4
**¿Porcentaje de artículos con garantía?**

**Resposta:** **81,25%** (13 de 16 publicações com garantia).

```sql
SELECT ROUND(100.0 * SUM(has_warranty) / COUNT(*), 2) AS warranty_percentage
FROM etl_publications
WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications);
```

**Lógica:** `has_warranty` vale 1 quando existe texto de garantia diferente de "Sin garantía" e 0 caso contrário. A consulta divide as publicações com garantia pelo total.

**Evidência:**

| warranty_percentage |
|---|
| 81.25 |

> ⚠️ Este número foi gerado antes da correção da regra de garantia (versão anterior tratava garantia vazia como "com garantia"). Reexecute o ETL para confirmar o valor com a regra atual.

---

## Pergunta 5
**¿Métodos de Shipping que ofrecen?**

**Resposta:** todas as publicações usam **Mercado Envíos 2 (`me2`)** com **frete grátis**, em três modalidades logísticas: `drop_off` (7), `xd_drop_off` (7) e `cross_docking` (2).

```sql
SELECT shipping_mode, shipping_logistic_type, shipping_free, COUNT(*) AS publication_count
FROM etl_publications
WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications)
GROUP BY shipping_mode, shipping_logistic_type, shipping_free
ORDER BY publication_count DESC;
```

**Lógica:** agrupa pelas três características de envio informadas na publicação (`shipping.mode`, `shipping.logistic_type`, `shipping.free_shipping`) e conta as publicações de cada combinação.

**Evidência:**

| shipping_mode | shipping_logistic_type | shipping_free | publication_count |
|---|---|---|---|
| me2 | drop_off | 1 | 7 |
| me2 | xd_drop_off | 1 | 7 |
| me2 | cross_docking | 1 | 2 |
