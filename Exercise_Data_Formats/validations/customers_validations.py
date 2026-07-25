import logging
from pathlib import Path

from pandera.pandas import DataFrameSchema, Column, Check
from pandera.errors import SchemaError
import pandas as pd


DIR = Path(__file__).resolve()

customers_schema = DataFrameSchema({
    "name": Column(str, checks=Check.str_length(1, 100, error="Name must be between 1 and 100 characters")),
    "email": Column(str),
    "customer_id": Column(int, checks=Check(lambda s: s > 0, error="Customer ID must be greater than 0"))
})


def validate_customers(df: pd.DataFrame, lazy: bool = True) -> pd.DataFrame:
    logging.info(f"Validating customers {DIR}")

    try:
        validated_df = customers_schema.validate(df, lazy=lazy)
    except SchemaError:
        logging.error(f"Customer Schema Error {DIR}")
        raise

    return validated_df

