SELECT
  order_month, SUM(revenue) AS total_revenue,
  COUNT(DISTINCT order_id) AS total_orders
FROM olist
GROUP BY order_month
ORDER BY order_month;
