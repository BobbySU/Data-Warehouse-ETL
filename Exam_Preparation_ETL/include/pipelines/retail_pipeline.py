import pandas as pd
from airflow.sdk import task, task_group
from airflow.exceptions import AirflowException
from airflow.utils import yaml

from include.etl.extract_data import extract_data_from_s3

from include.etl.load_df_to_s3 import load_df_to_s3_csv
from include.etl.transform import transform_sales_data, transform_products_data, hourly_sales_trend, \
    product_sales_ranking_with_brand, revenue_concentration, seasonal_sales_pattern, merge_sales_and_products, \
    enrich_merged_data
from include.s3_utils import get_storage_options

with open("include/config.yaml") as file:
    config = yaml.safe_load(file)

s3_hook, storage_options = get_storage_options(config["aws_conn_id"])

@task_group(group_id="extract_group")
def extract_group():

    @task()
    def extract_csv_files(bucket: str, folder: str, aws_conn_id: str) -> list:
        return extract_data_from_s3(
            bucket,
            folder,
            aws_conn_id,
            file_type="csv"
        )

    @task()
    def extract_json_files(bucket: str, folder: str, aws_conn_id: str) -> list:
        return extract_data_from_s3(
            bucket,
            folder,
            aws_conn_id,
            file_type="json"
        )

    @task()
    def get_sales_path(paths: list) -> list:
        for path in paths:
            if "sales_north" in path.lower():
                return path
        raise AirflowException("Sales path not found")

    @task()
    def get_products_path(paths: list) -> list:
        for path in paths:
            if "product" in path.lower():
                return path
        raise AirflowException("Products path not found")

    csv_paths = extract_csv_files(
        config["s3"]["bucket"],
        config["s3"]["folder"],
        config["aws_conn_id"]
    )

    json_paths = extract_json_files(
        config["s3"]["bucket"],
        config["s3"]["folder"],
        config["aws_conn_id"]
    )

    sales_path = get_sales_path(csv_paths)
    products_path = get_products_path(json_paths)

    return {
        "sales_path": sales_path,
        "products_path": products_path
    }

@task_group(group_id="transform_group")
def transform_group(sales_path: str, products_path: str):

    @task()
    def transform_sales(sales_path: str):
        df = pd.read_csv(sales_path, storage_options=storage_options)
        df = transform_sales_data(df)

        output_path = (
            f"s3://{config['s3']['bucket']}/"
            f"{config['s3']['output_folder']}/cleaned_sales.csv"
        )
        load_df_to_s3_csv(df, output_path, config["aws_conn_id"])
        return output_path

    @task()
    def transform_products(products_path: str):
        df = pd.read_json(products_path, storage_options=storage_options)
        df = transform_products_data(df)

        output_path = (
            f"s3://{config['s3']['bucket']}/"
            f"{config['s3']['output_folder']}/cleaned_products.csv"
        )
        load_df_to_s3_csv(df, output_path, config["aws_conn_id"])
        return output_path

    @task()
    def merge_data(clean_sales_path: str, clean_products_path: str):
        sales_df = pd.read_csv(clean_sales_path, storage_options=storage_options)
        products_df = pd.read_csv(clean_products_path, storage_options=storage_options)

        merge_df = merge_sales_and_products(sales_df, products_df)
        output_path = (
            f"s3://{config['s3']['bucket']}/"
            f"{config['s3']['output_folder']}/merge.csv"
        )
        load_df_to_s3_csv(merge_df, output_path, config["aws_conn_id"])
        return output_path

    @task()
    def enrich_data(merged_path: str):
        df = pd.read_csv(merged_path, storage_options=storage_options)
        enrich_df = enrich_merged_data(df)

        output_path = (
            f"s3://{config['s3']['bucket']}/"
            f"{config['s3']['output_folder']}/enrich.csv"
        )
        load_df_to_s3_csv(enrich_df, output_path, config["aws_conn_id"])
        return output_path

    cleaned_sales = transform_sales(sales_path)
    cleaned_products = transform_products(products_path)
    merged = merge_data(cleaned_sales, cleaned_products)
    enriched = enrich_data(merged)

    return {
        "cleaned_sales": cleaned_sales,
        "cleaned_products": cleaned_products,
        "merged": merged,
        "enriched": enriched
    }

@task_group(group_id="analytics")
def analytics_group(enriched_path: str):

    @task()
    def run_hourly_sales_trend(enriched_path: str):
        df = pd.read_csv(enriched_path, storage_options=storage_options)
        result = hourly_sales_trend(df)

        output_path = f"s3://{config['s3']['bucket']}/{config['s3']['analytics']}/hourly_sales_trend.csv"
        load_df_to_s3_csv(result, output_path, config["aws_conn_id"])
        return output_path

    @task()
    def run_product_sales_ranking_with_brand(enriched_df: str):
        df = pd.read_csv(enriched_df, storage_options=storage_options)
        result = product_sales_ranking_with_brand(df)

        output_path = f"s3://{config['s3']['bucket']}/{config['s3']['analytics']}/product_sales_ranking.csv"
        load_df_to_s3_csv(result, output_path, config["aws_conn_id"])
        return output_path

    @task()
    def run_seasonal_sales_pattern(enriched_df: str):
        df = pd.read_csv(enriched_df, storage_options=storage_options)
        result = seasonal_sales_pattern(df)

        output_path = f"s3://{config['s3']['bucket']}/{config['s3']['analytics']}/seasonal_sales_pattern.csv"
        load_df_to_s3_csv(result, output_path, config["aws_conn_id"])
        return output_path

    @task()
    def run_revenue_concentration(enriched_df: str):
        df = pd.read_csv(enriched_df, storage_options=storage_options)
        result = revenue_concentration(df)

        output_path = f"s3://{config['s3']['bucket']}/{config['s3']['analytics']}/revenue_concentration.csv"
        load_df_to_s3_csv(result, output_path, config["aws_conn_id"])
        return output_path

    hourly_trend = run_hourly_sales_trend(enriched_path)
    product_ranking = run_product_sales_ranking_with_brand(enriched_path)
    seasonal_patterns = run_seasonal_sales_pattern(enriched_path)
    revenue_conc = run_revenue_concentration(enriched_path)

    return {
        "hourly_trend": hourly_trend,
        "product_ranking": product_ranking,
        "seasonal_patterns": seasonal_patterns,
        "revenue_conc": revenue_conc,
    }


@task_group(group_id="load_group")
def load_group(hourly_trend, product_ranking, seasonal_patterns, revenue_conc):

    @task()
    def copy_csv(input_path: str, output_file: str):
        df = pd.read_csv(input_path, storage_options=storage_options)

        bucket = config["s3"]["bucket"]
        folder = config["s3"]["output_df"]

        output_path = f"s3://{bucket}/{folder}/{output_file}"
        load_df_to_s3_csv(df, output_path, config["aws_conn_id"])
        return output_path

    copy_csv.override(task_id="load_hourly_trend")(
        hourly_trend,
        output_file="hourly_sales_trend.csv"
    )
    copy_csv.override(task_id="load_product_sales_ranking")(
        product_ranking,
        output_file="product_sales_ranking.csv"
    )
    copy_csv.override(task_id="load_seasonal_patterns")(
        seasonal_patterns,
        output_file="seasonal_patterns.csv"
    )
    copy_csv.override(task_id="load_revenue_conc")(
        revenue_conc,
        output_file="revenue_conc.csv"
    )



def build_retail_pipeline():
    extract_output = extract_group()

    sales_path = extract_output["sales_path"]
    products_path = extract_output["products_path"]

    transform_output = transform_group(sales_path, products_path)

    enriched_path = transform_output["enriched"]

    analytics_output = analytics_group(enriched_path)

    load_group(
        hourly_trend=analytics_output["hourly_trend"],
        product_ranking=analytics_output["product_ranking"],
        seasonal_patterns=analytics_output["seasonal_patterns"],
        revenue_conc=analytics_output["revenue_conc"]
    )