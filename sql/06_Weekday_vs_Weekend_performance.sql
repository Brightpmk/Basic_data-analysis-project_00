-- Compare weekday vs weekend performance
-- ใช้ CASE เพื่อ map weekday เป็น weekday/weekend
SELECT
    CASE
        WHEN order_weekday IN ('Saturday', 'Sunday') THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(revenue) AS total_revenue
FROM olist
GROUP BY day_type;
