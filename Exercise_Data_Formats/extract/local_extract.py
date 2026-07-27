import json
import logging
import pandas as pd
from pathlib import Path


def extract_customers_from_json(file_path: str | Path) -> pd.DataFrame:
    """
    Read customers from a JSON file and return them as a pandas dataframe.
    """
    logging.info(f"Reading customers from json {file_path}")

    try:
        df = pd.read_json(file_path)
    except Exception:
        logging.error(f"Unexpected error with json file {file_path}")
        raise

    logging.info(f"Loaded {len(df)} customers")
    return df

def extract_and_flatten_records(file_path: str | Path) -> pd.DataFrame:
    """
    Load orders from JSON file and return them as a pandas dataframe
    """
    logging.info(f"Reading records from {file_path}")

    try:
        with open(file_path, "r") as file:
            records = json.load(file)
    except Exception as exc:
        logging.error(f"Unexpected error with file {file_path}")
        raise

    try:
        df = pd.json_normalize(records, meta=["order_id", "customer_id"], record_path=["order_details"]
        )
    except Exception as exc:
        logging.error(f"Error flattening order JSON file {file_path}")
        raise
    logging.info(f"Loaded {len(df)} records")
    return df