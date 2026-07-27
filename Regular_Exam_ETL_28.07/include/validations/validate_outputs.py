import logging
import pandas as pd
from pandera.errors import SchemaError

from include.validations.output_schemas import product_output_schema, sales_output_schema, enrich_output_schema

logger = logging.getLogger(__name__)


def validate_output_sales_schema(df: pd.DataFrame) -> pd.DataFrame:
    try:
        return sales_output_schema.validate(df)
    except SchemaError as e:
        logger.exception(f"Output sales schema error: {e}")
        raise

def validate_output_products_schema(products_df: pd.DataFrame) -> pd.DataFrame:
    try:
        return product_output_schema.validate(products_df)
    except SchemaError as e:
        logger.exception(f"Output product schema error: {e}")
        raise

def validate_output_enrich_schema(merged_df: pd.DataFrame) -> pd.DataFrame:
    try:
        return enrich_output_schema.validate(merged_df)
    except SchemaError as e:
        logger.exception(f"Output enrich schema error: {e}")
        raise