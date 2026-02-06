-- Revenue ของ Top 10 categories
SELECT
  SUM(revenue) AS top10_revenue
FROM (
  SELECT
    product_category_name_english,
    SUM(revenue) AS revenue
  FROM olist
  GROUP BY product_category_name_english
  ORDER BY revenue DESC
  LIMIT 10
);