import pandas as pd

from include.validations.enrich_schema import validate_output_enrich_schema
from include.validations.hourly_sales_schema import validate_output_hourly_sales_trend_schema
from include.validations.product_sales_schema import validate_output_product_sales_ranking_schema
from include.validations.product_schema import validate_input_products_schema, validate_output_products_schema
from include.validations.revenue_concentration_schema import validate_output_revenue_concentration_schema
from include.validations.sales_schema import validate_input_sales_schema, validate_output_sales_schema
from include.validations.seasonal_sales_pattern_schema import validate_output_seasonal_sales_pattern_schema


def transform_sales_data(sales_df: pd.DataFrame) -> pd.DataFrame:
    sales_df = validate_input_sales_schema(sales_df)

    sales_df.columns = sales_df.columns.str.strip().str.lower().str.replace(" ", "_")
    sales_df["region"] = sales_df["region"].str.strip().str.lower()
    sales_df["timestamp"] = pd.to_datetime(
        sales_df["timestamp"],
        format="mixed",
        errors="coerce"
    )
    sales_df = sales_df.dropna(subset=["region", "timestamp"])
    sales_df = sales_df[
        (sales_df["price"] > 0) & (sales_df["quantity"] > 0)
    ].copy()
    sales_df["total_sales"] = sales_df["price"] * sales_df["quantity"]

    return validate_output_sales_schema(sales_df)

def transform_products_data(products_df: pd.DataFrame) -> pd.DataFrame:
    products_df = validate_input_products_schema(products_df)

    products_df.columns = products_df.columns.str.strip().str.lower().str.replace(" ", "_")
    products_df["brand"] = products_df["brand"].str.strip().str.upper()
    products_df["category"] = products_df["category"].str.strip().str.lower()
    products_df = products_df.dropna(subset=["product_id", "rating"])
    products_df = products_df.drop_duplicates()

    return validate_output_products_schema(products_df)


def merge_sales_and_products(sales_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    merge_df = sales_df.merge(products_df, how="inner", on="product_id")
    return merge_df

def enrich_merged_data(
    merged_df: pd.DataFrame,
) -> pd.DataFrame:
    merged_df["timestamp"] = pd.to_datetime(merged_df["timestamp"], format="mixed", errors="coerce")
    merged_df["month"] = merged_df["timestamp"].dt.to_period("M").astype(str)
    merged_df["week"] = merged_df["timestamp"].dt.isocalendar().week
    merged_df["weekday"] = merged_df["timestamp"].dt.day_name()
    merged_df["hour"] = merged_df["timestamp"].dt.hour.astype("Int64")
    merged_df["sales_bucket"] = pd.cut(
        merged_df["total_sales"],
        bins=[0, 100, 500, float("inf")],
        labels=["Low", "Medium", "High"],
    )

    return validate_output_enrich_schema(merged_df)


def hourly_sales_trend(enriched_df: pd.DataFrame) -> pd.DataFrame:
    agg = (
        enriched_df.groupby(
            by=["region", "category", "hour"],
            as_index=False
        )
        .agg(hourly_sales_trend=("total_sales", "sum"))
    )

    idx = agg.groupby(["region", "category"])["hourly_sales_trend"].idxmax()

    peaks = agg.loc[idx].reset_index(drop=True)

    return validate_output_hourly_sales_trend_schema(peaks)

def product_sales_ranking_with_brand(enriched_df: pd.DataFrame) -> pd.DataFrame:
    summary = enriched_df.groupby(
        ["product_id", "category", "brand", "rating"], as_index=False
    ).agg(
        revenue=("total_sales", "sum"),
        sales_count=("product_id", "size")
    )

    revenue_rank = summary["revenue"].rank(
        method="average",
        pct=True,
    )

    sales_count_rank = summary["sales_count"].rank(
        method="average",
        pct=True,
    )

    performance_score = revenue_rank * 0.50 + sales_count_rank * 0.50

    summary["value_bucket"] = pd.cut(
        performance_score,
        bins=[0, 0.20, 0.80, 1],
        labels=["Low Performance", "Average", "BestSeller"],
        include_lowest=True,
    )

    return validate_output_product_sales_ranking_schema(summary)


def seasonal_sales_pattern(enriched_df: pd.DataFrame) -> pd.DataFrame:
    seasonal_df = enriched_df.copy()

    seasonal_df["timestamp"] = pd.to_datetime(
        seasonal_df["timestamp"],
        format="mixed",
        errors="coerce",
    )

    seasonal_df["quarter"] = seasonal_df["timestamp"].dt.to_period("Q").astype(str)

    seasonal_patterns = seasonal_df.groupby(
        ["quarter", "category"],
        as_index=False,
    ).agg(
        total_sales=("total_sales", "sum")
    )

    return validate_output_seasonal_sales_pattern_schema(seasonal_patterns)


def revenue_concentration(enriched_df: pd.DataFrame) -> pd.DataFrame:
    summary = enriched_df.groupby(by=["region"], as_index=False).agg(region_revenue=("total_sales", "sum"))
    summary = summary.sort_values(by="region_revenue", ascending=False).reset_index(drop=True)
    total = summary["region_revenue"].sum()

    if total == 0:
        raise ValueError("Total revenue is 0")

    summary["revenue_share"] = summary["region_revenue"] / total

    summary["cumulative_share"] = summary["revenue_share"].cumsum()

    return validate_output_revenue_concentration_schema(summary)