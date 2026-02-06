WITH order_totals AS (
  SELECT
    order_id, SUM(revenue) AS order_revenue
  FROM olist
  GROUP BY order_id
)
SELECT
  ROUND(AVG(order_revenue), 2) AS avg_order_value
FROM order_totals;