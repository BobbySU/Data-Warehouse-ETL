import pandas as pd
import pandera.pandas as pa

from pandera.pandas import Column, Check
from pandera.errors import SchemaError

revenue_concentration_schema = pa.DataFrameSchema({
    "region": Column(str, Check(lambda s: s.str.len() > 0)),
    "region_revenue": Column(float, Check.ge(0)),
    "revenue_share": Column(float, Check.in_range(min_value=0, max_value=1)),
    "cumulative_share": Column(float)
})

def validate_output_revenue_concentration_schema(df: pd.DataFrame) -> pd.DataFrame:
    try:
        return revenue_concentration_schema.validate(df)
    except SchemaError as e:
        print(f"Post-revenue_concentration schema error: {e}")
        raise