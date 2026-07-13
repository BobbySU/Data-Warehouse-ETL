from dataclasses import replace

import pandas as pd
import s3fs
from pandas import merge
from sqlalchemy.testing.plugin.plugin_base import engines

from config import *

dara = { "name": ["dasd", "dadd"],
       "af": ["12", "21"]}

df = pd.DataFrame(dara)
print(df)


df2 = pd.read_csv("C:\\Users\\radio\\OneDrive\\Desktop\\sales.csv")
print(df2)

df3 = pd.read_csv(
    "s3://data-warehouse-bobby/IntroductionDataToolsAndStorage/sales.csv",
    storage_options={
        "key": AWS_KEY,
        "secret": AWS_SECRET_KEY,
        "client_kwargs": {"region_name": AWS_DEFAULT_REGION}
    }
)
print(df3)

print("----")
print(df3.head())
print("----")
print(df3.info())
print("----")
print(df3.shape)

print("----")
print(df3["sale_id"])

print("----")
print(df3.describe())

print("----")
filter = df3[df3["amount"] > 1800]
print(filter)

print("----")
print(df3.sort_values(by="amount", ascending=False))

print("----")
print(df3.groupby("product_category")["amount"].sum())
print(df3.groupby("product_category")["amount"].mean())
print(df3.groupby("product_category")["amount"].max())

print("----")
df4 = pd.read_csv(
    "s3://data-warehouse-bobby/IntroductionDataToolsAndStorage/customers.csv",
    storage_options={
        "key": AWS_KEY,
        "secret": AWS_SECRET_KEY,
        "client_kwargs": {"region_name": AWS_DEFAULT_REGION}
    }
)
print(df4.columns)

merged_df = pd.merge(df3, df4, on="customer_id")
print(merged_df)

print("----")


DATABASE = "sales_data"

import sqlalchemy
import psycopg2
from sqlalchemy import create_engine

connection_string = f"postgresql+psycopg2://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@{POSTGRESQL_HOST}/{POSTGRESQL_DATABASE}"
engine = create_engine(connection_string)
merged_df.to_sql("sales_merged", engine, if_exists="replace", index=False)