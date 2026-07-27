import pandas as pd
import logging

from include.validations.validate_inputs import validate_input_sales_schema, validate_input_products_schema
from include.validations.validate_outputs import validate_output_sales_schema, validate_output_products_schema, \
    validate_output_enrich_schema

logger = logging.getLogger(__name__)

def transform_sales_data(sales_df: pd.DataFrame) -> pd.DataFrame:
    # Normalize column names
    sales_df.columns = (sales_df.columns.str.strip().str.lower().str.replace(" ", "_"))
    sales_df = sales_df.rename(columns={"qty": "quantity", "time_stamp": "timestamp"})

    # Validate input data
    sales_df = validate_input_sales_schema(sales_df)

    # Clean and transform data
    sales_df["region"] = (sales_df["region"].str.strip().str.lower())
    sales_df["timestamp"] = pd.to_datetime(sales_df["timestamp"],format="mixed",errors="coerce")
    sales_df = sales_df.dropna(subset=["sales_id", "product_id", "timestamp"])
    sales_df = sales_df[(sales_df["price"] > 0) &(sales_df["quantity"] > 0)].copy()
    sales_df["total_sales"] = (sales_df["price"] * sales_df["quantity"])

    # Validate final output before loading
    return validate_output_sales_schema(sales_df)

def transform_products_data(products_df: pd.DataFrame) -> pd.DataFrame:
    # Normalize column names
    products_df.columns = (products_df.columns.str.strip().str.lower().str.replace(" ", "_"))

    # Validate input data
    products_df = validate_input_products_schema(products_df)

    # Clean and transform data
    products_df["brand"] = products_df["brand"].str.strip().str.upper()
    products_df["category"] = products_df["category"].str.strip().str.lower()
    products_df["launch_date"] = pd.to_datetime(products_df["launch_date"],format="mixed",errors="coerce")
    products_df = products_df.dropna(subset=["product_id", "rating", "launch_date"])
    products_df = products_df.drop_duplicates()

    return validate_output_products_schema(products_df)


def merge_sales_and_products(sales_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:

    merge_df = sales_df.merge(products_df, how="inner", on="product_id")
    return merge_df


def enrich_merged_data(merged_df: pd.DataFrame,) -> pd.DataFrame:

    merged_df["launch_date"] = pd.to_datetime(merged_df["launch_date"])
    merged_df["timestamp"] = pd.to_datetime(merged_df["timestamp"], format="mixed", errors="coerce")
    merged_df["month"] = merged_df["timestamp"].dt.to_period("M").astype(str)
    merged_df["quarter"] = merged_df["timestamp"].dt.to_period("Q").astype(str)
    merged_df["week"] = merged_df["timestamp"].dt.isocalendar().week
    merged_df["weekday"] = merged_df["timestamp"].dt.day_name()
    merged_df["sales_bucket"] = pd.cut(
        merged_df["total_sales"],
        bins=[0, 500, 1500, float("inf")],
        labels=["Low", "Medium", "High"],
    )

    return validate_output_enrich_schema(merged_df)