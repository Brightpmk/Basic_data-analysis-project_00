SELECT
    CASE
        WHEN delivery_delay_days > 0 THEN 'Late'
        WHEN delivery_delay_days <= 0 THEN 'On Time / Early'
        ELSE 'Unknown'
    END AS delivery_bucket,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(AVG(revenue), 2) AS avg_item_revenue
FROM olist
GROUP BY delivery_bucket
ORDER BY total_orders DESC;