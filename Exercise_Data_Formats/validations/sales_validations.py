import logging
from pathlib import Path

import pandera
from pandera.pandas import DataFrameSchema, Column, Check
from pandera.errors import SchemaError
import pandas as pd

DIR = Path(__file__).resolve()

sales_schema = DataFrameSchema({
    "order_id": Column(int, checks=Check(lambda s: s > 0, error="Sales Order ID must be greater than 0")),
    "customer_id": Column(int, checks=Check(lambda s: s > 0, error="Customer ID must be greater than 0")),
    "amount": Column(float, checks=Check(lambda s: s >= 0.0, error="Amount must be greater than 0")),
    "quantity": Column(int, checks=Check(lambda s: s > 0, error="Quantity must be greater than 0")),
    "order_date": Column(pandera.DateTime, coerce=True)
})


def validate_sales(df: pd.DataFrame, lazy: bool = True) -> pd.DataFrame:
    logging.info(f"Validating sales data {DIR}")

    try:
        validated_df = sales_schema.validate(df, lazy=lazy)
    except SchemaError:
        logging.error(f"Sales Data Schema Error {DIR}")
        raise

    return validated_df