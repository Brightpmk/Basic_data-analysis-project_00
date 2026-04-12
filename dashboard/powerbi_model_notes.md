# Power BI Data Model Notes

## Tables to import
- data/marts/fact_sales.csv
- data/marts/dim_customers.csv
- data/marts/dim_products.csv
- data/marts/dim_sellers.csv
- data/marts/dim_date.csv
- data/marts/customer_rfm_summary.csv
- data/marts/kpi_monthly_summary.csv

## Relationships
- fact_sales[customer_id] -> dim_customers[customer_id]
- fact_sales[product_id] -> dim_products[product_id]
- fact_sales[seller_id] -> dim_sellers[seller_id]
- fact_sales[date_key] -> dim_date[date_key]

## Core measures
- Total Revenue = SUM(fact_sales[revenue])
- Total Orders = DISTINCTCOUNT(fact_sales[order_id])
- Avg Review Score = AVERAGE(fact_sales[review_score])
- Late Delivery Rate = AVERAGE(fact_sales[is_late_delivery])

## Dashboard Pages
1. Executive Overview
2. Product Performance
3. Delivery & Customer Experience
4. Customer Segmentation