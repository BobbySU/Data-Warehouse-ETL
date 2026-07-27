import logging
import pandas as pd

from include.s3_utils import get_storage_options

logger = logging.getLogger(__name__)

def load_df_to_s3_csv(df: pd.DataFrame, s3_path: str, aws_conn_id: str):
    s3_hook, storage_options = get_storage_options(aws_conn_id)

    try:
        df.to_csv(s3_path, index=False, storage_options=storage_options)
    except Exception as e:
        logger.exception(f"Error uploading CSV file to s3: {e}")
        raise

    logger.info(f"Finished writing CSV to s3 {s3_path}")

def load_df_to_s3_json(df: pd.DataFrame, s3_path: str, aws_conn_id: str):
    s3_hook, storage_options = get_storage_options(aws_conn_id)

    try:
        df.to_json(
            s3_path,
            orient="records",
            lines=True,
            storage_options=storage_options
        )
    except Exception as e:
        logger.exception(f"Error uploading JSON file to S3: {e}")
        raise

    logger.info(f"Finished writing JSON to S3: {s3_path}")