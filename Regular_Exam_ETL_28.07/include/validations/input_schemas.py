import pandera.pandas as pa
from pandera.pandas import Column

sales_input_schema = pa.DataFrameSchema({
    "sales_id": Column(int),
    "product_id": Column(int),
    "region": Column(str),
    "quantity": Column(int),
    "price": Column(float),
    "timestamp": Column(object),
    "discount": Column(float),
    "order_status": Column(str),
})

product_input_schema = pa.DataFrameSchema({
    "product_id": Column(int),
    "category": Column(str),
    "brand": Column(str),
    "rating": Column(float),
    "in_stock": Column(bool),
    "launch_date": Column(object)
})