import pandera.pandas as pa
from pandera.pandas import Column, Check

sales_output_schema = pa.DataFrameSchema({
    "sales_id": Column(int,nullable=False),
    "product_id": Column(int, nullable=False),
    "region": Column(str, nullable=True),
    "quantity": Column(int, Check.greater_than(0)),
    "price": Column(float, Check.greater_than(0)),
    "timestamp": Column(pa.DateTime, nullable=False),
    "discount": Column(float, Check.greater_than_or_equal_to(0)),
    "order_status": Column(str),
    "total_sales": Column(float, Check.greater_than(0))
})

product_output_schema = pa.DataFrameSchema({
    "product_id": Column(int,nullable=False),
    "category": Column(str, Check(lambda s: s.str.islower())),
    "brand": Column(str, Check(lambda s: s.str.isupper())),
    "rating": Column(float),
    "in_stock": Column(bool,nullable=False),
    "launch_date": Column(pa.DateTime, nullable=False)
})

enrich_output_schema = pa.DataFrameSchema({
    "sales_id": Column(int,nullable=False),
    "product_id": Column(int, nullable=False),
    "region": Column(str, nullable=True),
    "quantity": Column(int, Check.greater_than(0)),
    "price": Column(float, Check.greater_than(0)),
    "timestamp": Column(pa.DateTime, nullable=False),
    "discount": Column(float, Check.greater_than_or_equal_to(0)),
    "order_status": Column(str),
    "total_sales": Column(float, Check.greater_than(0)),
    "category": Column(str, Check(lambda s: s.str.islower())),
    "brand": Column(str, Check(lambda s: s.str.isupper())),
    "rating": Column(float),
    "in_stock": Column(bool,nullable=False),
    "launch_date": Column(pa.DateTime, nullable=False),
    "month": Column(str),
    "quarter": Column(str),
    "sales_bucket": Column(str),
})