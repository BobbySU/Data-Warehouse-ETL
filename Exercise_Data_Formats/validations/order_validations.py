import logging
from pathlib import Path

from pandera.pandas import DataFrameSchema, Column, Check
from pandera.errors import SchemaError, SchemaErrors
import pandas as pd

DIR = Path(__file__).resolve()

orders_schema = DataFrameSchema(
    {
        "order_id": Column(int,checks=Check(lambda s: s > 0,
                                               error="Order ID must be > 0",),),
        "customer_id": Column(int,checks=Check(lambda s: s > 0,
                                                  error="Customer ID must be > 0",),),
        "product": Column(str,checks=Check.str_length(min_value=1,max_value=100,
                                                         error="Product must be between 1 and 100 characters",),),
        "quantity": Column(int,checks=Check(lambda s: s > 0,
                                               error="Quantity must be > 0",),),
        "price": Column(float,checks=Check(lambda s: s >= 0,
                                              error="Price must be >= 0",),),
    }, strict=True)


def validate_orders(df: pd.DataFrame, lazy: bool = True) -> pd.DataFrame:
    logging.info(f"Validating orders {DIR}")

    try:
        validated_df = orders_schema.validate(df, lazy=lazy)
    except (SchemaError, SchemaErrors):
        logging.error(f"Orders schema validation failed {DIR}")
        raise

    return validated_df