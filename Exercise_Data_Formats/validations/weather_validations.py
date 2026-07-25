import logging
from pathlib import Path

from pandera.pandas import DataFrameSchema, Column, Check
from pandera.errors import SchemaError
import pandas as pd

DIR = Path(__file__).resolve()

weather_schema = DataFrameSchema({
    "city": Column(str, checks=Check.str_length(1, 100)),
    "temperature": Column(str,Check.str_length(1, 100, error="Invalid Temperature format")),
    "feel": Column(str)
})

def validate_weather(df: pd.DataFrame, lazy: bool = True) -> pd.DataFrame:
    logging.info(f"Validating weather data {DIR}")

    try:
        validated_df = weather_schema.validate(df, lazy=lazy)
    except SchemaError:
        logging.info(f"Weather data not valid {DIR}")
        raise

    return validated_df