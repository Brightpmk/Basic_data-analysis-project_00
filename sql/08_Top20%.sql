-- Pareto analysis: top 20% categories contribution
WITH category_revenue AS (
    SELECT
        product_category_name_english,
        SUM(revenue) AS revenue
    FROM olist
    GROUP BY product_category_name_english
),
ranked AS (
    SELECT
        product_category_name_english, revenue,
        NTILE(5) OVER (ORDER BY revenue DESC) AS revenue_bucket
    FROM category_revenue
)

SELECT SUM(revenue) AS top_20_percent_revenue
FROM ranked
WHERE revenue_bucket = 1;
