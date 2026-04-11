-- Rank product categories by total revenue
-- ใช้ window function เพื่อจัดอันดับ
SELECT
    product_category_name_english, total_revenue,
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM (
    SELECT
        product_category_name_english,
        SUM(revenue) AS total_revenue
    FROM olist
    GROUP BY product_category_name_english
) t
ORDER BY revenue_rank
LIMIT 10;
