from config.config import AWS_BUCKET_NAME, AWS_FOLDER_PREFIX
from extract.extract_s3 import extract_s3

def run_etl_pipeline():
    sales_df, customer_df, product_df, shipping_df = extract_s3(bucket_name=AWS_BUCKET_NAME, folder_name=AWS_FOLDER_PREFIX)

    print(sales_df)
    print(customer_df)
    print(product_df)
    print(shipping_df)

if __name__ == "__main__":
    run_etl_pipeline()