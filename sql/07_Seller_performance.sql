-- Identify high-performing sellers
-- ใช้ HAVING เพื่อ filter หลัง aggregate
SELECT
    seller_id,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(revenue) AS total_revenue
FROM olist
GROUP BY seller_id
HAVING total_orders >= 50
ORDER BY total_revenue DESC;
