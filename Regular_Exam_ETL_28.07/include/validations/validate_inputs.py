import logging
import pandas as pd
from pandera.errors import SchemaError

from include.validations.input_schemas import product_input_schema, sales_input_schema

logger = logging.getLogger(__name__)

def validate_input_sales_schema(sales_df: pd.DataFrame) -> pd.DataFrame:
    try:
        return sales_input_schema.validate(sales_df)
    except SchemaError as e:
        logger.exception(f"Input schema validation failed: {e}")
        return sales_df


def validate_input_products_schema(products_df: pd.DataFrame) -> pd.DataFrame:
    try:
        return product_input_schema.validate(products_df)
    except SchemaError as e:
        logger.exception(f"Input product schema validation failed: {e}")
        return products_df