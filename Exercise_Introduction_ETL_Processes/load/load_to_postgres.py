import pandas as pd
import  psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import create_engine

from config.config import POSTGRESQL_HOST, POSTGRESQL_PORT, POSTGRESQL_DATABASE, POSTGRESQL_USER, POSTGRESQL_PASSWORD


def create_database_if_not_exists():
    db_params = {
        "host": POSTGRESQL_HOST,
        "port": POSTGRESQL_PORT,
        "database": "postgres",
        "user": POSTGRESQL_USER,
        "password": POSTGRESQL_PASSWORD,
    }

    conn = psycopg2.connect(**db_params)
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (POSTGRESQL_DATABASE,))

            if cur.fetchone() is None:
                cur.execute(f'CREATE DATABASE "{POSTGRESQL_DATABASE}"')
                print(f"Database {POSTGRESQL_DATABASE} created successfully")
            else:
                print(f"Database {POSTGRESQL_DATABASE} already exists")
    finally:
        conn.close()

# Малки и до средни данни за качване
def load_to_postgresql(df: pd.DataFrame, table_name: str, if_exists: str = "append"):
    try:
        connection_string = f"postgresql+psycopg2://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@{POSTGRESQL_HOST}/{POSTGRESQL_DATABASE}"
        engine = create_engine(connection_string)
        df.to_sql(table_name, engine, if_exists=if_exists, index=False, method="multi", chunksize=1000)
        print(f"Successfully loaded data to table {table_name}")
    except Exception as e:
        print(f"Error loading data to PostgreSQL: {e}")
        raise

def load_transformed_to_postgres(df: pd.DataFrame, table_name: str):
    create_table_sql = (f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        order_id INT PRIMARY KEY,
        customer_id INT,
        total_revenue NUMERIC(10, 2),
        profit_margin NUMERIC(10, 2),
        shipping_days INT
    );
    """)

    insert_sql = f"""
    INSERT INTO {table_name}(
    order_id,
    customer_id,
    total_revenue,
    profit_margin,
    shipping_days
    )
    VALUES %s
    ON CONFLICT (order_id) DO UPDATE
    SET total_revenue = EXCLUDED.total_revenue,
        profit_margin = EXCLUDED.profit_margin,
        shipping_days = EXCLUDED.shipping_days;
    """

    db_param = {
        "host": POSTGRESQL_HOST,
        "port": POSTGRESQL_PORT,
        "database": POSTGRESQL_DATABASE,
        "user": POSTGRESQL_USER,
        "password": POSTGRESQL_PASSWORD
    }

    try:
        columns_to_load = [
            "order_id", "customer_id", "total_revenue", "profit_margin", "shipping_days"
        ]
        missing_columns = [column for column in columns_to_load if column not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns: {missing_columns}")

        values = list(df[columns_to_load].itertuples(index=False, name=None))
        if not values:
            print(f"No rows to load into table {table_name}")
            return

        with psycopg2.connect(**db_param) as conn:
            with conn.cursor() as cur:
                cur.execute(create_table_sql)
                execute_values(cur, insert_sql, values)
                conn.commit()
                print(f"Successfully loaded data to table {table_name}")

    except Exception as e:
        print(f"Error loading data to PostgreSQL: {e}")
        raise
