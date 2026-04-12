import os
import sqlite3
import pandas as pd


RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "orders": pd.read_csv(os.path.join(RAW_DIR, "olist_orders_dataset.csv")),
        "items": pd.read_csv(os.path.join(RAW_DIR, "olist_order_items_dataset.csv")),
        "payments": pd.read_csv(os.path.join(RAW_DIR, "olist_order_payments_dataset.csv")),
        "reviews": pd.read_csv(os.path.join(RAW_DIR, "olist_order_reviews_dataset.csv")),
        "customers": pd.read_csv(os.path.join(RAW_DIR, "olist_customers_dataset.csv")),
        "products": pd.read_csv(os.path.join(RAW_DIR, "olist_products_dataset.csv")),
        "categories": pd.read_csv(os.path.join(RAW_DIR, "product_category_name_translation.csv")),
        "sellers": pd.read_csv(os.path.join(RAW_DIR, "olist_sellers_dataset.csv")),
    }


def clean_orders(orders: pd.DataFrame) -> pd.DataFrame:
    orders = orders.drop_duplicates().copy()

    datetime_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for col in datetime_cols:
        orders[col] = pd.to_datetime(orders[col], errors="coerce")

    return orders


def clean_items(items: pd.DataFrame) -> pd.DataFrame:
    items = items.drop_duplicates().copy()
    items["price"] = pd.to_numeric(items["price"], errors="coerce")
    items["freight_value"] = pd.to_numeric(items["freight_value"], errors="coerce")
    items["shipping_limit_date"] = pd.to_datetime(items["shipping_limit_date"], errors="coerce")
    return items


def clean_payments(payments: pd.DataFrame) -> pd.DataFrame:
    payments = payments.drop_duplicates().copy()
    payments["payment_value"] = pd.to_numeric(payments["payment_value"], errors="coerce")
    payments["payment_installments"] = pd.to_numeric(
        payments["payment_installments"], errors="coerce"
    )
    return payments


def clean_reviews(reviews: pd.DataFrame) -> pd.DataFrame:
    reviews = reviews.drop_duplicates().copy()
    reviews["review_score"] = pd.to_numeric(reviews["review_score"], errors="coerce")
    reviews["review_creation_date"] = pd.to_datetime(
        reviews["review_creation_date"], errors="coerce"
    )
    reviews["review_answer_timestamp"] = pd.to_datetime(
        reviews["review_answer_timestamp"], errors="coerce"
    )
    return reviews


def clean_customers(customers: pd.DataFrame) -> pd.DataFrame:
    return customers.drop_duplicates().copy()


def clean_products(products: pd.DataFrame) -> pd.DataFrame:
    return products.drop_duplicates().copy()


def clean_categories(categories: pd.DataFrame) -> pd.DataFrame:
    return categories.drop_duplicates().copy()


def clean_sellers(sellers: pd.DataFrame) -> pd.DataFrame:
    return sellers.drop_duplicates().copy()


def build_payment_agg(payments: pd.DataFrame) -> pd.DataFrame:
    return (
        payments.groupby("order_id", as_index=False)
        .agg(
            order_total_payment_value=("payment_value", "sum"),
            payment_installments_max=("payment_installments", "max"),
            payment_type_nunique=("payment_type", "nunique"),
        )
    )


def build_review_agg(reviews: pd.DataFrame) -> pd.DataFrame:
    return (
        reviews.groupby("order_id", as_index=False)
        .agg(
            review_score=("review_score", "mean"),
            has_review_comment=("review_comment_message", lambda x: int(x.notna().any())),
            review_count=("review_id", "nunique"),
        )
    )


def build_processed_dataset(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    orders = clean_orders(data["orders"])
    items = clean_items(data["items"])
    payments = clean_payments(data["payments"])
    reviews = clean_reviews(data["reviews"])
    customers = clean_customers(data["customers"])
    products = clean_products(data["products"])
    categories = clean_categories(data["categories"])
    sellers = clean_sellers(data["sellers"])

    payment_agg = build_payment_agg(payments)
    review_agg = build_review_agg(reviews)

    products_enriched = products.merge(categories, on="product_category_name", how="left")

    df = (
        items.merge(orders, on="order_id", how="left")
        .merge(customers, on="customer_id", how="left")
        .merge(products_enriched, on="product_id", how="left")
        .merge(sellers, on="seller_id", how="left", suffixes=("", "_seller"))
        .merge(payment_agg, on="order_id", how="left")
        .merge(review_agg, on="order_id", how="left")
    )

    df["is_delivered"] = (df["order_status"] == "delivered").astype(int)
    df["is_canceled"] = (df["order_status"] == "canceled").astype(int)

    df["item_revenue"] = df["price"].fillna(0)
    df["shipping_revenue"] = df["freight_value"].fillna(0)
    df["revenue"] = df["item_revenue"] + df["shipping_revenue"]

    purchase_ts = df["order_purchase_timestamp"]
    delivered_ts = df["order_delivered_customer_date"]
    est_delivery_ts = df["order_estimated_delivery_date"]

    df["order_date"] = purchase_ts.dt.date
    df["order_month"] = purchase_ts.dt.to_period("M").astype(str)
    df["order_year"] = purchase_ts.dt.year
    df["order_quarter"] = purchase_ts.dt.to_period("Q").astype(str)
    df["order_weekday"] = purchase_ts.dt.day_name()
    df["purchase_hour"] = purchase_ts.dt.hour

    df["delivery_days"] = (delivered_ts - purchase_ts).dt.days
    df["estimated_delivery_days"] = (est_delivery_ts - purchase_ts).dt.days
    df["delivery_delay_days"] = (delivered_ts - est_delivery_ts).dt.days

    df["is_late_delivery"] = (
        (df["delivery_delay_days"] > 0) & df["delivery_delay_days"].notna()
    ).astype(int)

    df["delivery_status"] = pd.Series("unknown", index=df.index)
    df.loc[
        df["delivery_delay_days"].notna() & (df["delivery_delay_days"] <= 0),
        "delivery_status",
    ] = "on_time_or_early"
    df.loc[
        df["delivery_delay_days"].notna() & (df["delivery_delay_days"] > 0),
        "delivery_status",
    ] = "late"
    df.loc[df["order_status"] != "delivered", "delivery_status"] = "not_delivered"

    df["product_category_name_english"] = df["product_category_name_english"].fillna("unknown")

    df["missing_review_score_flag"] = df["review_score"].isna().astype(int)
    df["missing_product_category_flag"] = df["product_category_name_english"].eq("unknown").astype(int)
    df["missing_delivery_info_flag"] = df["delivery_days"].isna().astype(int)
    df["order_status_delivery_conflict_flag"] = (
        df["order_status"].ne("delivered") & df["order_delivered_customer_date"].notna()
    ).astype(int)

    keep_cols = [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "customer_id",
        "customer_unique_id",
        "customer_city",
        "customer_state",
        "seller_city",
        "seller_state",
        "order_status",
        "is_delivered",
        "is_canceled",
        "order_purchase_timestamp",
        "order_date",
        "order_month",
        "order_year",
        "order_quarter",
        "order_weekday",
        "purchase_hour",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
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
        "product_category_name",
        "product_category_name_english",
        "missing_product_category_flag",
        "missing_delivery_info_flag",
        "order_status_delivery_conflict_flag",
    ]

    return df[keep_cols].copy()


def save_outputs(df: pd.DataFrame) -> None:
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    csv_path = os.path.join(PROCESSED_DIR, "clean_olist_data.csv")
    db_path = os.path.join(PROCESSED_DIR, "olist_analysis.db")

    df.to_csv(csv_path, index=False)

    conn = sqlite3.connect(db_path)
    try:
        df.to_sql("olist", conn, if_exists="replace", index=False)
    finally:
        conn.close()

    print(f"Saved processed CSV to: {csv_path}")
    print(f"Saved SQLite DB to: {db_path}")
    print(f"Dataset shape: {df.shape}")


def main() -> None:
    data = load_data()
    df = build_processed_dataset(data)
    save_outputs(df)


if __name__ == "__main__":
    main()