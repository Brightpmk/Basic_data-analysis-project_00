import os
import pandas as pd


PROCESSED_PATH = "data/processed/clean_olist_data.csv"
MART_DIR = "data/marts"


def build_order_level_dataset(df: pd.DataFrame) -> pd.DataFrame:
    base = df.copy()
    base["order_purchase_timestamp"] = pd.to_datetime(base["order_purchase_timestamp"])

    order_level = (
        base.sort_values(["order_id", "order_item_id"])
        .groupby("order_id", as_index=False)
        .agg(
            order_purchase_timestamp=("order_purchase_timestamp", "first"),
            order_date=("order_date", "first"),
            order_month=("order_month", "first"),
            order_year=("order_year", "first"),
            order_quarter=("order_quarter", "first"),
            order_weekday=("order_weekday", "first"),
            purchase_hour=("purchase_hour", "first"),
            customer_id=("customer_id", "first"),
            customer_unique_id=("customer_unique_id", "first"),
            order_status=("order_status", "first"),
            is_delivered=("is_delivered", "max"),
            is_canceled=("is_canceled", "max"),
            order_revenue=("revenue", "sum"),
            order_item_revenue=("item_revenue", "sum"),
            order_shipping_revenue=("shipping_revenue", "sum"),
            order_total_payment_value=("order_total_payment_value", "first"),
            payment_installments_max=("payment_installments_max", "first"),
            payment_type_nunique=("payment_type_nunique", "first"),
            review_score=("review_score", "first"),
            has_review_comment=("has_review_comment", "first"),
            review_count=("review_count", "first"),
            delivery_days=("delivery_days", "first"),
            estimated_delivery_days=("estimated_delivery_days", "first"),
            delivery_delay_days=("delivery_delay_days", "first"),
            is_late_delivery=("is_late_delivery", "max"),
            delivery_status=("delivery_status", "first"),
            item_count=("order_item_id", "count"),
            distinct_products=("product_id", "nunique"),
            distinct_sellers=("seller_id", "nunique"),
            missing_review_score_flag=("missing_review_score_flag", "max"),
            missing_delivery_info_flag=("missing_delivery_info_flag", "max"),
            order_status_delivery_conflict_flag=("order_status_delivery_conflict_flag", "max"),
        )
    )

    order_level["date_key"] = order_level["order_purchase_timestamp"].dt.strftime("%Y%m%d").astype(int)
    order_level["is_weekend"] = order_level["order_weekday"].isin(["Saturday", "Sunday"]).astype(int)
    order_level["delivered_revenue"] = order_level["order_revenue"].where(order_level["is_delivered"] == 1, 0)
    return order_level


def build_dim_date(order_level: pd.DataFrame) -> pd.DataFrame:
    dim_date = (
        order_level[["date_key", "order_purchase_timestamp", "order_year", "order_quarter", "order_month", "order_weekday"]]
        .drop_duplicates(subset=["date_key"])
        .copy()
    )
    dim_date["order_date"] = pd.to_datetime(dim_date["order_purchase_timestamp"]).dt.date
    dim_date["month_num"] = pd.to_datetime(dim_date["order_purchase_timestamp"]).dt.month
    dim_date["day_of_month"] = pd.to_datetime(dim_date["order_purchase_timestamp"]).dt.day
    dim_date["is_weekend"] = dim_date["order_weekday"].isin(["Saturday", "Sunday"]).astype(int)

    return dim_date[
        [
            "date_key",
            "order_date",
            "order_year",
            "order_quarter",
            "order_month",
            "month_num",
            "day_of_month",
            "order_weekday",
            "is_weekend",
        ]
    ].sort_values("date_key").reset_index(drop=True)


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
            "payment_installments_max",
            "payment_type_nunique",
            "order_total_payment_value",
            "review_score",
            "review_count",
            "has_review_comment",
            "missing_review_score_flag",
            "order_status_delivery_conflict_flag",
        ]
    ].copy()


def build_customer_rfm_summary(order_level: pd.DataFrame) -> pd.DataFrame:
    base = order_level.copy()
    snapshot_date = base["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

    customer_order = (
        base.groupby("customer_unique_id", as_index=False)
        .agg(
            last_purchase_date=("order_purchase_timestamp", "max"),
            frequency_orders=("order_id", "nunique"),
            monetary_revenue=("delivered_revenue", "sum"),
        )
    )

    customer_order["recency_days"] = (
        snapshot_date - customer_order["last_purchase_date"]
    ).dt.days

    customer_order["r_rank"] = pd.qcut(
        customer_order["recency_days"].rank(method="first"),
        4,
        labels=[4, 3, 2, 1],
    ).astype(int)

    customer_order["f_rank"] = pd.qcut(
        customer_order["frequency_orders"].rank(method="first"),
        4,
        labels=[1, 2, 3, 4],
    ).astype(int)

    customer_order["m_rank"] = pd.qcut(
        customer_order["monetary_revenue"].rank(method="first"),
        4,
        labels=[1, 2, 3, 4],
    ).astype(int)

    customer_order["rfm_score"] = (
        customer_order["r_rank"].astype(str)
        + customer_order["f_rank"].astype(str)
        + customer_order["m_rank"].astype(str)
    )

    def segment(row: pd.Series) -> str:
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


def build_kpi_monthly_summary(order_level: pd.DataFrame) -> pd.DataFrame:
    delivered_orders = order_level[order_level["is_delivered"] == 1].copy()

    monthly = (
        delivered_orders.groupby("order_month", as_index=False)
        .agg(
            total_orders=("order_id", "nunique"),
            total_revenue=("delivered_revenue", "sum"),
            avg_order_value=("delivered_revenue", "mean"),
            avg_review_score=("review_score", "mean"),
            late_delivery_rate=("is_late_delivery", "mean"),
        )
        .sort_values("order_month")
    )

    monthly["mom_revenue_growth_pct"] = monthly["total_revenue"].pct_change() * 100
    monthly["mom_orders_growth_pct"] = monthly["total_orders"].pct_change() * 100
    return monthly


def main() -> None:
    os.makedirs(MART_DIR, exist_ok=True)

    df = pd.read_csv(PROCESSED_PATH)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])

    order_level = build_order_level_dataset(df)
    fact_sales = build_fact_sales(df)
    dim_customers = build_dim_customers(df)
    dim_products = build_dim_products(df)
    dim_sellers = build_dim_sellers(df)
    dim_date = build_dim_date(order_level)
    customer_rfm = build_customer_rfm_summary(order_level)
    monthly_kpi = build_kpi_monthly_summary(order_level)

    fact_sales.to_csv(os.path.join(MART_DIR, "fact_sales.csv"), index=False)
    order_level.to_csv(os.path.join(MART_DIR, "fact_orders.csv"), index=False)
    dim_customers.to_csv(os.path.join(MART_DIR, "dim_customers.csv"), index=False)
    dim_products.to_csv(os.path.join(MART_DIR, "dim_products.csv"), index=False)
    dim_sellers.to_csv(os.path.join(MART_DIR, "dim_sellers.csv"), index=False)
    dim_date.to_csv(os.path.join(MART_DIR, "dim_date.csv"), index=False)
    customer_rfm.to_csv(os.path.join(MART_DIR, "customer_rfm_summary.csv"), index=False)
    monthly_kpi.to_csv(os.path.join(MART_DIR, "kpi_monthly_summary.csv"), index=False)

    print("Analytics mart tables saved to data/marts/")


if __name__ == "__main__":
    main()