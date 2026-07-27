import pandas as pd
import pandera.pandas as pa

from pandera.pandas import Column, Check
from pandera.errors import SchemaError

enrich_output_schema = pa.DataFrameSchema({
    "sales_id": Column(int),
    "product_id": Column(int),
    "region": Column(str),
    "quantity": Column(int),
    "price": Column(float),
    "timestamp": Column(pa.DateTime),
    "total_sales": Column(float),
    "category": Column(str),
    "brand": Column(str),
    "rating": Column(float),
    "month": Column(str),
    "hour": Column(int),
    "sales_bucket": Column(str),
})

def validate_output_enrich_schema(merged_df: pd.DataFrame) -> pd.DataFrame:
    try:
        return enrich_output_schema.validate(merged_df)
    except SchemaError as e:
        print(f"Post-enriched schema error: {e}")
        raise