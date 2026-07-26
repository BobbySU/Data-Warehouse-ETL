import pandas as pd
import pandera.pandas as pa

from pandera.pandas import Column, Check
from pandera.errors import SchemaError


product_sales_ranking_schema = pa.DataFrameSchema({
    "product_id": Column(int),
    "revenue": Column(float, Check.ge(0)),
    "sales_count": Column(int, Check.ge(0)),
    "value_bucket": Column(
        str,
        Check.isin(["Low Performance", "Average", "BestSeller"])
    ),
})


def validate_output_product_sales_ranking_schema(
    df: pd.DataFrame,
) -> pd.DataFrame:
    try:
        return product_sales_ranking_schema.validate(df)
    except SchemaError as e:
        print(f"Post-product_sales_ranking schema error: {e}")
        raise