import os
import pandas as pd


PROCESSED_PATH = "data/processed/clean_olist_data.csv"
MART_DIR = "data/marts"


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    date_df = (
        df[["order_purchase_timestamp", "order_month", "order_year", "order_quarter", "order_weekday", "purchase_hour"]]
        .drop_duplicates()
        .copy()
    )
    date_df["order_purchase_timestamp"] = pd.to_datetime(date_df["order_purchase_timestamp"])
    date_df["date_key"] = date_df["order_purchase_timestamp"].dt.strftime("%Y%m%d").astype(int)
    date_df["order_date"] = date_df["order_purchase_timestamp"].dt.date
    date_df["month_num"] = date_df["order_purchase_timestamp"].dt.month
    return date_df[
        [
            "date_key",
            "order_date",
            "order_month",
            "order_year",
            "order_quarter",
            "month_num",
            "order_weekday",
            "purchase_hour",
        ]
    ].drop_duplicates()


def build_dim_customers(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df[["customer_id", "customer_unique_id", "customer_city", "customer_state"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )


def build_dim_products(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df[["product_id", "product_category_name", "product_category_name_english", "missing_product_category_flag"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )


def build_dim_sellers(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df[["seller_id", "seller_city", "seller_state"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )


def build_fact_sales(df: pd.DataFrame) -> pd.DataFrame:
    fact = df.copy()
    fact["order_purchase_timestamp"] = pd.to_datetime(fact["order_purchase_timestamp"])
    fact["date_key"] = fact["order_purchase_timestamp"].dt.strftime("%Y%m%d").astype(int)

    return fact[
        [
            "order_id",
            "order_item_id",
            "date_key",
            "customer_id",
            "customer_unique_id",
            "product_id",
            "seller_id",
            "order_status",
            "is_delivered",
            "is_canceled",
            "delivery_days",
            "estimated_delivery_days",
            "delivery_delay_days",
            "is_late_delivery",
            "delivery_status",
            "price",
            "freight_value",
            "item_revenue",
            "shipping_revenue",
            "revenue",
            "payment_installments",
            "payment_type_nunique",
            "total_payment_value",
            "review_score",
            "has_review_comment",
            "missing_review_score_flag",
        ]
    ].copy()


def build_customer_rfm_summary(df: pd.DataFrame) -> pd.DataFrame:
    base = df.copy()
    base["order_purchase_timestamp"] = pd.to_datetime(base["order_purchase_timestamp"])

    snapshot_date = base["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

    customer_order = (
        base.groupby("customer_unique_id")
        .agg(
            last_purchase_date=("order_purchase_timestamp", "max"),
            frequency_orders=("order_id", "nunique"),
            monetary_revenue=("revenue", "sum"),
        )
        .reset_index()
    )

    customer_order["recency_days"] = (
        snapshot_date - customer_order["last_purchase_date"]
    ).dt.days

    customer_order["r_rank"] = pd.qcut(
        customer_order["recency_days"].rank(method="first"),
        4,
        labels=[4, 3, 2, 1]
    ).astype(int)

    customer_order["f_rank"] = pd.qcut(
        customer_order["frequency_orders"].rank(method="first"),
        4,
        labels=[1, 2, 3, 4]
    ).astype(int)

    customer_order["m_rank"] = pd.qcut(
        customer_order["monetary_revenue"].rank(method="first"),
        4,
        labels=[1, 2, 3, 4]
    ).astype(int)

    customer_order["rfm_score"] = (
        customer_order["r_rank"].astype(str)
        + customer_order["f_rank"].astype(str)
        + customer_order["m_rank"].astype(str)
    )

    def segment(row) -> str:
        if row["r_rank"] >= 3 and row["f_rank"] >= 3 and row["m_rank"] >= 3:
            return "Champions"
        if row["r_rank"] >= 3 and row["f_rank"] >= 2:
            return "Loyal Customers"
        if row["r_rank"] == 4 and row["f_rank"] == 1:
            return "Promising"
        if row["r_rank"] <= 2 and row["f_rank"] >= 3:
            return "At Risk"
        return "Others"

    customer_order["rfm_segment"] = customer_order.apply(segment, axis=1)

    return customer_order


def build_kpi_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby("order_month")
        .agg(
            total_orders=("order_id", "nunique"),
            total_revenue=("revenue", "sum"),
            avg_order_item_revenue=("revenue", "mean"),
            avg_review_score=("review_score", "mean"),
            late_delivery_rate=("is_late_delivery", "mean"),
        )
        .reset_index()
        .sort_values("order_month")
    )

    monthly["mom_revenue_growth_pct"] = monthly["total_revenue"].pct_change() * 100
    monthly["mom_orders_growth_pct"] = monthly["total_orders"].pct_change() * 100
    return monthly


def main() -> None:
    os.makedirs(MART_DIR, exist_ok=True)

    df = pd.read_csv(PROCESSED_PATH)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])

    fact_sales = build_fact_sales(df)
    dim_customers = build_dim_customers(df)
    dim_products = build_dim_products(df)
    dim_sellers = build_dim_sellers(df)
    dim_date = build_dim_date(df)
    customer_rfm = build_customer_rfm_summary(df)
    monthly_kpi = build_kpi_monthly_summary(df)

    fact_sales.to_csv(os.path.join(MART_DIR, "fact_sales.csv"), index=False)
    dim_customers.to_csv(os.path.join(MART_DIR, "dim_customers.csv"), index=False)
    dim_products.to_csv(os.path.join(MART_DIR, "dim_products.csv"), index=False)
    dim_sellers.to_csv(os.path.join(MART_DIR, "dim_sellers.csv"), index=False)
    dim_date.to_csv(os.path.join(MART_DIR, "dim_date.csv"), index=False)
    customer_rfm.to_csv(os.path.join(MART_DIR, "customer_rfm_summary.csv"), index=False)
    monthly_kpi.to_csv(os.path.join(MART_DIR, "kpi_monthly_summary.csv"), index=False)

    print("Analytics mart tables saved to data/marts/")


if __name__ == "__main__":
    main()