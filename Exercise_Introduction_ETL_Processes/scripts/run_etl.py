from config.config import AWS_BUCKET_NAME, AWS_FOLDER_PREFIX
from extract.extract_s3 import extract_s3
from transform.transform import clean_data, remove_duplicates, merge_data, compute_derived_columns, segment_deliveries, \
    categorize_products
from load.load_to_postgres import create_database_if_not_exists, load_to_postgresql, load_transformed_to_postgres


def run_etl_pipeline():
    sales_df, customer_df, product_df, shipping_df = extract_s3(bucket_name=AWS_BUCKET_NAME, folder_name=AWS_FOLDER_PREFIX)

    #print(sales_df)
    #print(customer_df)
    #print(product_df)
    #print(shipping_df)

    #print(sales_df.columns)
    #print(customer_df.columns)
    #print(product_df.columns)
    #print(shipping_df.columns)

    cleaned_dfs = clean_data([sales_df,customer_df, product_df, shipping_df],
                             old_column_name="diskount", new_column_name="discount")

    deduped_dfs = remove_duplicates(cleaned_dfs)

    merge_columns = [
        ("customer_id", "customer_id"),
        ("product_id", "product_id"),
        ("order_id", "order_id"),
    ]

    merged_df = merge_data(dfs=deduped_dfs,merge_columns=merge_columns)

    merged_df = compute_derived_columns(merged_df=merged_df)
    merged_df = segment_deliveries(merged_df=merged_df)
    merged_df = categorize_products(merged_df=merged_df)

    print(merged_df)

    create_database_if_not_exists()
    load_to_postgresql(df=merged_df, table_name="sales_data")
    load_transformed_to_postgres(df=merged_df, table_name="sales_transformed")

if __name__ == "__main__":
    run_etl_pipeline()