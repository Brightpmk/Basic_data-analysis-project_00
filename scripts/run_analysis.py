import os
import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = "data/processed/clean_olist_data.csv"
FIGURE_DIR = "outputs/figures"
TABLE_DIR = "outputs/summary_tables"


def ensure_dirs() -> None:
    os.makedirs(FIGURE_DIR, exist_ok=True)
    os.makedirs(TABLE_DIR, exist_ok=True)


def save_monthly_kpi(df: pd.DataFrame) -> None:
    monthly = (
        df.groupby("order_month")
        .agg(
            total_orders=("order_id", "nunique"),
            total_revenue=("revenue", "sum"),
            avg_review_score=("review_score", "mean"),
            late_delivery_rate=("is_late_delivery", "mean"),
        )
        .reset_index()
        .sort_values("order_month")
    )
    monthly["mom_revenue_growth_pct"] = monthly["total_revenue"].pct_change() * 100
    monthly.to_csv(f"{TABLE_DIR}/monthly_kpi.csv", index=False)

    plt.figure(figsize=(10, 5))
    plt.plot(monthly["order_month"], monthly["total_revenue"])
    plt.xticks(rotation=45)
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Order Month")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig(f"{FIGURE_DIR}/monthly_revenue_trend.png")
    plt.close()


def save_top_categories(df: pd.DataFrame) -> None:
    category = (
        df.groupby("product_category_name_english")
        .agg(
            total_revenue=("revenue", "sum"),
            total_orders=("order_id", "nunique"),
            avg_review_score=("review_score", "mean"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
        .head(10)
    )
    category.to_csv(f"{TABLE_DIR}/top_categories_revenue.csv", index=False)

    plt.figure(figsize=(10, 6))
    plt.barh(category["product_category_name_english"], category["total_revenue"])
    plt.gca().invert_yaxis()
    plt.title("Top 10 Product Categories by Revenue")
    plt.xlabel("Revenue")
    plt.tight_layout()
    plt.savefig(f"{FIGURE_DIR}/top_categories_revenue.png")
    plt.close()


def save_delivery_review_analysis(df: pd.DataFrame) -> None:
    delivery = (
        df.groupby("delivery_status")
        .agg(
            total_orders=("order_id", "nunique"),
            avg_review_score=("review_score", "mean"),
            avg_delivery_delay_days=("delivery_delay_days", "mean"),
        )
        .reset_index()
        .sort_values("total_orders", ascending=False)
    )
    delivery.to_csv(f"{TABLE_DIR}/delivery_review_analysis.csv", index=False)

    plot_df = delivery[delivery["delivery_status"] != "not_delivered"].copy()

    plt.figure(figsize=(8, 5))
    plt.bar(plot_df["delivery_status"], plot_df["avg_review_score"])
    plt.title("Average Review Score by Delivery Status")
    plt.xlabel("Delivery Status")
    plt.ylabel("Average Review Score")
    plt.tight_layout()
    plt.savefig(f"{FIGURE_DIR}/review_by_delivery_status.png")
    plt.close()


def save_weekday_weekend(df: pd.DataFrame) -> None:
    weekday_map = df.copy()
    weekday_map["day_type"] = weekday_map["order_weekday"].apply(
        lambda x: "Weekend" if x in ["Saturday", "Sunday"] else "Weekday"
    )

    summary = (
        weekday_map.groupby("day_type")
        .agg(
            total_orders=("order_id", "nunique"),
            total_revenue=("revenue", "sum"),
            avg_review_score=("review_score", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(f"{TABLE_DIR}/weekday_vs_weekend.csv", index=False)

    plt.figure(figsize=(6, 4))
    plt.bar(summary["day_type"], summary["total_revenue"])
    plt.title("Weekday vs Weekend Revenue")
    plt.xlabel("Day Type")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig(f"{FIGURE_DIR}/weekday_vs_weekend.png")
    plt.close()


def save_customer_repeat_proxy(df: pd.DataFrame) -> None:
    customer_orders = (
        df.groupby("customer_unique_id")
        .agg(
            total_orders=("order_id", "nunique"),
            total_revenue=("revenue", "sum"),
        )
        .reset_index()
    )

    customer_orders["customer_type"] = customer_orders["total_orders"].apply(
        lambda x: "Repeat" if x > 1 else "One-time"
    )

    summary = (
        customer_orders.groupby("customer_type")
        .agg(
            total_customers=("customer_unique_id", "count"),
            avg_customer_revenue=("total_revenue", "mean"),
        )
        .reset_index()
    )
    summary.to_csv(f"{TABLE_DIR}/customer_repeat_proxy.csv", index=False)

    plt.figure(figsize=(6, 4))
    plt.bar(summary["customer_type"], summary["total_customers"])
    plt.title("Customer Repeat Proxy")
    plt.xlabel("Customer Type")
    plt.ylabel("Total Customers")
    plt.tight_layout()
    plt.savefig(f"{FIGURE_DIR}/customer_repeat_proxy.png")
    plt.close()


def main() -> None:
    ensure_dirs()
    df = pd.read_csv(DATA_PATH)

    save_monthly_kpi(df)
    save_top_categories(df)
    save_delivery_review_analysis(df)
    save_weekday_weekend(df)
    save_customer_repeat_proxy(df)

    print("Analysis outputs generated successfully.")


if __name__ == "__main__":
    main()