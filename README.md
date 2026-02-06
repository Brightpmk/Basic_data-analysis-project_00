# Olist E-commerce Data Analysis Project

## 📌 Project Overview

This project presents an end-to-end data analysis of the **Olist
Brazilian E-commerce Dataset**, focusing on extracting business-driven
insights from real transactional data.

The goal of this project is to simulate a real-world data analyst
workflow --- from raw data ingestion and cleaning to SQL-based
analytical modeling and insight generation.

The analysis explores revenue dynamics, customer behavior, product
performance, seller efficiency, operational delays, and review patterns.

------------------------------------------------------------------------

## 🎯 Business Questions

This project aims to answer the following analytical questions:

1.  How does revenue evolve over time?
2.  Is revenue concentrated within a small group of product categories?
3.  How do review scores relate to revenue performance?
4.  Who are the high-value customers?
5.  How do weekday and weekend sales compare?
6.  How do delivery delays affect customer satisfaction?
7.  Which sellers generate the highest revenue?

------------------------------------------------------------------------

## 📊 Dataset

The dataset used is the **Olist Brazilian E-commerce Dataset**,
containing transactional data from a Brazilian marketplace.

### Main Tables Used:

-   Orders
-   Order Items
-   Payments
-   Reviews
-   Customers
-   Products
-   Sellers
-   Product Category Translation

After cleaning and transformation, the data was merged into a unified
analytical fact table for SQL-based analysis.

------------------------------------------------------------------------

## 🛠 Tools & Technologies

-   **Python** (pandas, matplotlib)
-   **SQL** (SQLite)
-   **Jupyter Notebook**
-   **VS Code**
-   **Git & GitHub**

------------------------------------------------------------------------

## 🔄 Project Workflow

### 1️⃣ Exploratory Data Analysis (EDA)

-   Inspected schema, data types, and distributions
-   Identified missing values and inconsistencies
-   Assessed initial revenue and review trends

### 2️⃣ Data Cleaning & Feature Engineering

-   Converted date columns to datetime format
-   Created derived features:
    -   Revenue
    -   Order month
    -   Weekday vs weekend
    -   Delivery delay
-   Merged relational tables into a structured analytical dataset

### 3️⃣ SQL-Based Analytical Modeling

Imported cleaned dataset into SQLite and implemented multiple analytical
queries using:

-   Subqueries
-   Common Table Expressions (CTEs)
-   Window functions
-   CASE-based business logic
-   Revenue ranking and segmentation logic

### 4️⃣ Visualization & Insight Generation

-   Built revenue trend analysis
-   Performed Pareto (80/20) revenue concentration analysis
-   Evaluated seller performance
-   Analyzed review-score behavior
-   Examined operational delivery delays

------------------------------------------------------------------------

## 📈 Key Findings

-   Revenue demonstrates strong monthly patterns and seasonality.
-   A small subset of product categories contributes a disproportionate
    share of total revenue (Pareto effect).
-   High-value customers represent a small percentage of the customer
    base but contribute significantly to total revenue.
-   Weekday sales outperform weekend sales in revenue contribution.
-   Some high-revenue categories have lower review scores, indicating
    potential operational improvement areas.
-   Delivery delay distribution is right-skewed, revealing logistical
    outliers.

------------------------------------------------------------------------

## 📂 SQL Analysis Modules

This project contains **10 structured SQL analysis files**, each
focusing on a specific business metric:

1.  Monthly revenue and order trends\
2.  Monthly KPI analysis\
3.  Product category ranking\
4.  Customer segmentation\
5.  Review score analysis\
6.  Weekday vs weekend performance\
7.  Seller performance\
8.  Top 20% revenue concentration (Pareto analysis)\
9.  Total revenue calculation\
10. Revenue from top 10 categories

------------------------------------------------------------------------

## 🚀 Future Improvements

-   Add automated data validation checks
-   Implement reproducible pipeline scripts
-   Explore BI dashboard integration (Power BI / Tableau)
-   Optimize SQL queries using indexing and performance analysis

------------------------------------------------------------------------

📁 Project Structure
```text
Basic_data-analysis-project/
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_cleaning.ipynb
│   └── 03_analysis.ipynb
│
├── sql/
│   ├── 01_Monthly_revenue_and_orders.sql
│   ├── 02_Monthly_KPI.sql
│   ├── 03_Raking_category.sql
│   ├── 04_Customer_segmentation.sql
│   ├── 05_Review_score.sql
│   ├── 06_Weekday_vs_Weekend_performance.sql
│   ├── 07_Seller_performance.sql
│   ├── 08_Top20%.sql
│   ├── 09_Total_revenue.sql
│   └── 10_Revenue_from_top10category.sql
│
├── outputs/
│   ├── figures/
│   └── summary_tables/
│
├── README.md
└── requirements.txt

------------------------------------------------------------------------
