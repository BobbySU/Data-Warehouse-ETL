import logging

import pandas as pd
import psycopg2

from sqlalchemy import create_engine

def extract_sales_from_database(sql_query: str, db_params: dict) -> pd.DataFrame:
    connection_string = (
        f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}"
        f"@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    )

    logging.info(f"Connecting to PostgreSQL database: {db_params['database']}")

    try:
        engine = create_engine(connection_string)
    except Exception as e:
        logging.error(f"Error connecting to PostgreSQL database: {e}")
        raise

    logging.info(f"Connecting to PostgreSQL database: {db_params['database']}")

    try:
        df = pd.read_sql_query(sql_query, engine)
    except Exception as e:
        logging.error(f"Failed to execute query {sql_query}")
        raise

    logging.info(f"Successfully extracted sales from {db_params['database']}")

    return df