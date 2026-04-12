WITH customer_summary AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(revenue) AS total_revenue,
        AVG(revenue) AS avg_revenue_per_item
    FROM olist
    GROUP BY customer_unique_id
),
ranked AS (
    SELECT
        customer_unique_id,
        total_orders,
        total_revenue,
        avg_revenue_per_item,
        NTILE(4) OVER (ORDER BY total_revenue DESC) AS revenue_quartile,
        NTILE(4) OVER (ORDER BY total_orders DESC) AS frequency_quartile
    FROM customer_summary
)

SELECT
    customer_unique_id,
    total_orders,
    total_revenue,
    avg_revenue_per_item,
    revenue_quartile,
    frequency_quartile,
    CASE
        WHEN revenue_quartile = 1 AND frequency_quartile = 1 THEN 'Top Customers'
        WHEN revenue_quartile IN (1, 2) AND frequency_quartile IN (1, 2) THEN 'High Potential'
        WHEN revenue_quartile IN (3, 4) AND frequency_quartile IN (1, 2) THEN 'Frequent Low Spend'
        ELSE 'Low Engagement'
    END AS customer_segment
FROM ranked
ORDER BY total_revenue DESC;