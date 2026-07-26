import pandas as pd
import pandera.pandas as pa

from pandera.pandas import Column, Check
from pandera.errors import SchemaError

hourly_sales_trend_schema = pa.DataFrameSchema({
    "region": Column(str, Check(lambda s: s.str.len() > 0)),
    "hour": Column(int, Check.in_range(min_value=0, max_value=23)),
    "hourly_sales_trend": Column(float, Check.ge(0)),
})

def validate_output_hourly_sales_trend_schema(
    df: pd.DataFrame,
) -> pd.DataFrame:
    try:
        return hourly_sales_trend_schema.validate(df)
    except SchemaError as e:
        print(f"Post-hourly_sales_trend schema error: {e}")
        raise