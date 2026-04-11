-- Analyze relationship between review score and revenue
-- ใช้ aggregation + grouping เชิง behavioral
SELECT
    review_score,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(AVG(revenue), 2) AS avg_revenue_per_item
FROM olist
GROUP BY review_score
ORDER BY review_score;
