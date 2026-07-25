from config.config import AWS_BUCKET_NAME, AWS_FILE_PATH_CSV, AWS_FILE_PATH_PARQUET, AWS_FILE_PATH_JSON, \
    POSTGRESQL_DATABASE, POSTGRESQL_USER, POSTGRESQL_PASSWORD, POSTGRESQL_HOST, POSTGRESQL_PORT
from extract.aws_s3_extract import extract_csv_from_s3, extract_from_s3, extract_parquet_from_s3, extract_json_from_s3
from extract.extract_sinoptik import extract_weather_from_sinoptik
from extract.local_extract import extract_customers_from_json, extract_and_flatten_records
from extract.postgres_extract import extract_sales_from_database
from load.load_data_to_s3 import load_df_to_s3_csv, load_df_to_s3_json
from load.load_local_data import load_to_json, load_to_csv
from validations.customers_validations import validate_customers
from validations.order_validations import validate_orders
from validations.sales_validations import validate_sales
from validations.weather_validations import validate_weather

if __name__ == "__main__":
    customers_df = extract_customers_from_json("../data/customers.json")
    orders_df = extract_and_flatten_records("../data/orders.json")

    #print(customers_df.head())
    #print(orders_df.head())
    """
    Само за определен формат CSV
    """
    #sales_df_csv = extract_csv_from_s3(bucket_name=AWS_BUCKET_NAME, file_key=AWS_FILE_PATH_CSV)
    #sales_df_parquet = extract_parquet_from_s3(bucket_name=AWS_BUCKET_NAME, file_key=AWS_FILE_PATH_PARQUET)
    #sales_df_json = extract_json_from_s3(bucket_name=AWS_BUCKET_NAME, file_key=AWS_FILE_PATH_JSON)
    """
    За няколко формата CSV/JSON/PARQUET
    """
    sales_df_csv = extract_from_s3(bucket_name=AWS_BUCKET_NAME, file_key=AWS_FILE_PATH_CSV, file_type="csv")
    sales_df_parquet = extract_from_s3(bucket_name=AWS_BUCKET_NAME, file_key=AWS_FILE_PATH_PARQUET, file_type="parquet")
    sales_df_json = extract_from_s3(bucket_name=AWS_BUCKET_NAME, file_key=AWS_FILE_PATH_JSON, file_type="json")

    #print(sales_df_csv.head())
    #print(sales_df_parquet.head())
    #print(sales_df_json.head())

    orders_df["order_id"] = orders_df["order_id"].astype(int)
    orders_df["customer_id"] = orders_df["customer_id"].astype(int)

    merged_df = customers_df.merge(orders_df, on="customer_id", how="left")

    #print(merged_df.head())

    sql_query = "SELECT * FROM sales_data"

    db_params = {
        "database": POSTGRESQL_DATABASE,
        "user": POSTGRESQL_USER,
        "password": POSTGRESQL_PASSWORD,
        "host": POSTGRESQL_HOST,
        "port": POSTGRESQL_PORT,
    }

    sales_df_db = extract_sales_from_database(sql_query=sql_query, db_params=db_params)

    #print(sales_df_db.head())

    weather_df = extract_weather_from_sinoptik()

    #print(weather_df)

    validated_customers_df = validate_customers(customers_df)
    validated_orders_df = validate_orders(orders_df)
    validated_sales_df = validate_sales(sales_df_csv)
    validated_weather_df = validate_weather(weather_df)


    load_to_json(sales_df_db, filename="sales_data_db.json")
    load_to_json(validated_customers_df, filename="customers_data.json")
    load_to_json(validated_orders_df, filename="orders_data.json")

    load_to_csv(validated_sales_df, filename="sales_data.csv")
    load_to_csv(validated_weather_df, filename="weather_data.csv")

    load_df_to_s3_csv(validated_sales_df,s3_path=f"s3://{AWS_BUCKET_NAME}/ExerciseDataFormats/test_load_data/sales_data.csv",)
    load_df_to_s3_json(validated_orders_df,s3_path=f"s3://{AWS_BUCKET_NAME}/ExerciseDataFormats/test_load_data/orders_data.json",)