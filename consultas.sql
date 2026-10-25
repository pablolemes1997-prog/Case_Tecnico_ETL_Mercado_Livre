-- Consultas do desafio. Todas usam apenas a última execução (JOB_RUN mais recente).

-- QUESTÃO 1 | ¿Hay algún vendedor con múltiples publicaciones? ¿Con cuántas?
SELECT seller_id, COUNT(*) AS publication_count
FROM etl_publications
WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications)
GROUP BY seller_id
HAVING COUNT(*) > 1
ORDER BY publication_count DESC;

-- QUESTÃO 1 (complemento) | Quantidade de publicações por vendedor
SELECT seller_id, COUNT(*) AS publication_count
FROM etl_publications
WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications)
GROUP BY seller_id
ORDER BY publication_count DESC, seller_id;

-- QUESTÃO 2 | ¿Promedio de ventas por seller?
-- Publicações com sold_quantity nulo (API sem permissão) ficam fora da média.
SELECT seller_id, ROUND(AVG(sold_quantity), 2) AS average_sales
FROM etl_publications
WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications)
  AND sold_quantity IS NOT NULL
GROUP BY seller_id
ORDER BY average_sales DESC;

-- QUESTÃO 3 | ¿Cuál es el precio promedio en dólares?
SELECT ROUND(AVG(price_usd), 2) AS average_price_usd
FROM etl_publications
WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications)
  AND price_usd IS NOT NULL;

-- QUESTÃO 4 | ¿Porcentaje de artículos con garantía?
SELECT ROUND(100.0 * SUM(has_warranty) / COUNT(*), 2) AS warranty_percentage
FROM etl_publications
WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications);

-- QUESTÃO 5 | ¿Métodos de Shipping que ofrecen?
SELECT shipping_mode, shipping_logistic_type, shipping_free, COUNT(*) AS publication_count
FROM etl_publications
WHERE JOB_RUN = (SELECT MAX(JOB_RUN) FROM etl_publications)
GROUP BY shipping_mode, shipping_logistic_type, shipping_free
ORDER BY publication_count DESC;
