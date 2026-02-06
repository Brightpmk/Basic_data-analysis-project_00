-- Segment customers based on total spending
-- ใช้ CASE WHEN เพื่อสร้าง business logic
SELECT
    customer_unique_id, total_spent,
    CASE
        WHEN total_spent >= 1000 THEN 'High Value'
        WHEN total_spent BETWEEN 500 AND 999 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS customer_segment
FROM (
    SELECT
        customer_unique_id, SUM(revenue) AS total_spent
    FROM olist
    GROUP BY customer_unique_id
) t
ORDER BY total_spent DESC;
