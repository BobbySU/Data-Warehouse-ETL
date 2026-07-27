import pandas as pd
import pandera.pandas as pa

from pandera.pandas import Column, Check
from pandera.errors import SchemaError

seasonal_sales_pattern_schema = pa.DataFrameSchema({
    "quarter": Column(str),
    "category": Column(str),
    "total_sales": Column(float),
})

def validate_output_seasonal_sales_pattern_schema(df: pd.DataFrame) -> pd.DataFrame:
    try:
        return seasonal_sales_pattern_schema.validate(df)
    except SchemaError as e:
        print(f"Post-seasonal_sales_pattern schema error: {e}")
        raise