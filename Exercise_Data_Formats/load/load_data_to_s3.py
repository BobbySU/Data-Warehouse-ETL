import logging
import pandas as pd

from config.s3_utils import get_s3_client_and_storage_options


def load_df_to_s3_csv(df: pd.DataFrame, s3_path: str) -> None:
    _, storage_options = get_s3_client_and_storage_options()
    try:
        df.to_csv(s3_path, index=False, storage_options=storage_options)
    except Exception:
        logging.exception(f"Error while trying to save dataframe to {s3_path}")
        raise

    logging.info(f"Successfully saved dataframe to {s3_path}")


def load_df_to_s3_json(df: pd.DataFrame, s3_path: str) -> None:
    _, storage_options = get_s3_client_and_storage_options()

    logging.info(f"Saving dataframe to {s3_path}")

    try:
        df.to_json(s3_path, orient="records", storage_options=storage_options)
    except Exception:
        logging.exception(f"Error while trying to save dataframe to {s3_path}")
        raise

    logging.info(f"Successfully saved dataframe to {s3_path}")


