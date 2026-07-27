import pandas as pd
from airflow.sdk import task, task_group
from airflow.exceptions import AirflowException
from airflow.utils import yaml

from include.etl.extract_s3 import extract_data_from_s3
from include.etl.load_s3_json_or_csv import (
    load_df_to_s3_csv,
    load_df_to_s3_json,
)
from include.etl.load_snowflake import load_enrich_to_snowflake
from include.etl.transform import (
    transform_sales_data,
    transform_products_data,
    merge_sales_and_products,
    enrich_merged_data,
)
from include.s3_utils import get_storage_options

with open("include/config.yaml") as file:
    config = yaml.safe_load(file)

s3_hook, storage_options = get_storage_options(config["aws_conn_id"])


# ==========================
# EXTRACT
# ==========================

@task_group(group_id="extract_group")
def extract_group():

    @task
    def extract_csv_files(bucket, folder, aws_conn_id):
        return extract_data_from_s3(
            bucket,
            folder,
            aws_conn_id,
            file_type="csv",
        )

    @task
    def extract_json_files(bucket, folder, aws_conn_id):
        return extract_data_from_s3(
            bucket,
            folder,
            aws_conn_id,
            file_type="json",
        )

    @task
    def get_sales_path(paths):
        for path in paths:
            if "sales_data" in path.lower():
                return path
        raise AirflowException("Sales path not found")

    @task
    def get_products_path(paths):
        for path in paths:
            if "product" in path.lower():
                return path
        raise AirflowException("Products path not found")

    csv_paths = extract_csv_files(
        config["s3"]["bucket"],
        config["s3"]["folder"],
        config["aws_conn_id"],
    )

    json_paths = extract_json_files(
        config["s3"]["bucket"],
        config["s3"]["folder"],
        config["aws_conn_id"],
    )

    sales_path = get_sales_path(csv_paths)
    products_path = get_products_path(json_paths)

    return {
        "sales_path": sales_path,
        "products_path": products_path,
    }


# ==========================
# TRANSFORM
# ==========================

@task_group(group_id="transform_group")
def transform_group(sales_path, products_path):

    @task
    def transform_sales(sales_path):
        df = pd.read_csv(
            sales_path,
            storage_options=storage_options,
        )

        df = transform_sales_data(df)

        return df.to_json(orient="records")

    @task
    def transform_products(products_path):
        df = pd.read_json(
            products_path,
            storage_options=storage_options,
        )

        df = transform_products_data(df)

        return df.to_json(orient="records")

    @task
    def merge_data(sales_json, products_json):
        sales_df = pd.read_json(sales_json)
        products_df = pd.read_json(products_json)

        merged_df = merge_sales_and_products(
            sales_df,
            products_df,
        )

        return merged_df.to_json(orient="records")

    @task
    def enrich_data(merged_json):
        merged_df = pd.read_json(merged_json)

        enriched_df = enrich_merged_data(merged_df)

        return enriched_df.to_json(orient="records")

    sales = transform_sales(sales_path)
    products = transform_products(products_path)
    merged = merge_data(sales, products)
    enriched = enrich_data(merged)

    return {
        "sales": sales,
        "products": products,
        "merged": merged,
        "enriched": enriched,
    }


# ==========================
# LOAD TO S3
# ==========================

@task_group(group_id="s3_load_group")
def load_group(sales_json, products_json, merged_json, enriched_json):

    @task
    def load_sales(sales_json):
        df = pd.read_json(sales_json)

        output = (
            f"s3://{config['s3']['bucket']}/"
            f"{config['s3']['output_folder']}/cleaned_sales.json"
        )

        load_df_to_s3_json(
            df,
            output,
            config["aws_conn_id"],
        )

        return output

    @task
    def load_products(products_json):
        df = pd.read_json(products_json)

        output = (
            f"s3://{config['s3']['bucket']}/"
            f"{config['s3']['output_folder']}/cleaned_products.csv"
        )

        load_df_to_s3_csv(
            df,
            output,
            config["aws_conn_id"],
        )

        return output

    @task
    def load_merged(merged_json):
        df = pd.read_json(merged_json)

        output = (
            f"s3://{config['s3']['bucket']}/"
            f"{config['s3']['output_folder']}/merge.csv"
        )

        load_df_to_s3_csv(
            df,
            output,
            config["aws_conn_id"],
        )

        return output

    @task
    def load_enriched(enriched_json):
        df = pd.read_json(enriched_json)

        output = (
            f"s3://{config['s3']['bucket']}/"
            f"{config['s3']['output_folder']}/enrich.csv"
        )

        load_df_to_s3_csv(
            df,
            output,
            config["aws_conn_id"],
        )

        return output

    sales = load_sales(sales_json)
    products = load_products(products_json)
    merged = load_merged(merged_json)
    enriched = load_enriched(enriched_json)

    return {
        "sales": sales,
        "products": products,
        "merged": merged,
        "enriched": enriched,
    }

# ==========================
# LOAD TO SNOWFLAKE
    # First create table SALES_CLEAN in snowflake!!!
# ==========================

@task_group(group_id="snowflake_load_group")
def snowflake_load_group():

    @task
    def load():
        load_enrich_to_snowflake(
            config["snowflake"]["conn_id"]
        )

    return load()

# ==========================
# PIPELINE
# ==========================

def build_retail_pipeline():

    extract_output = extract_group()

    transform_output = transform_group(
        extract_output["sales_path"],
        extract_output["products_path"],
    )

    load_output = load_group(
        transform_output["sales"],
        transform_output["products"],
        transform_output["merged"],
        transform_output["enriched"],
    )

    snowflake_task = snowflake_load_group()

    load_output["enriched"] >> snowflake_task

    return load_output