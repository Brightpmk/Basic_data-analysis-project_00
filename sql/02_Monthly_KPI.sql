-- Monthly business performance overview
-- ใช้ CTE เพื่อแยก logic ให้ชัดเจนและอ่านง่าย
WITH monthly_orders AS (
    SELECT
        order_month,
        order_id,
        revenue
    FROM olist
)

SELECT
    order_month,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(revenue) AS total_revenue,
    ROUND(AVG(revenue), 2) AS avg_item_revenue
FROM monthly_orders
GROUP BY order_month
ORDER BY order_month;
