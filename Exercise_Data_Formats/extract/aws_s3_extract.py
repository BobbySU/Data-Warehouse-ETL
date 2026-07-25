import logging
import pandas as pd
import pyarrow

from config.s3_utils import get_s3_client_and_storage_options


def extract_csv_from_s3(bucket_name: str, file_key: str) -> pd.DataFrame:
    """
    Read csv file from s3 bucket.
    """

    _, storage_options = get_s3_client_and_storage_options()

    s3_path = f"s3://{bucket_name}/{file_key}"
    logging.info(f"S3 path: {s3_path}")

    try:
        df = pd.read_csv(s3_path, storage_options=storage_options)
    except Exception:
        logging.error(f"Failed to extract CSV from S3: {s3_path}")
        raise

    logging.info(f"Successfully extracted CSV from S3: {s3_path}")

    return df

def extract_json_from_s3(bucket_name: str, file_key: str) -> pd.DataFrame:
    """
    Read JSON file from s3 bucket.
    """

    _, storage_options = get_s3_client_and_storage_options()

    s3_path = f"s3://{bucket_name}/{file_key}"
    logging.info(f"S3 path: {s3_path}")

    try:
        df = pd.read_json(s3_path, storage_options=storage_options)
    except Exception:
        logging.error(f"Failed to extract JSON from S3: {s3_path}")
        raise

    logging.info(f"Successfully extracted JSON from S3: {s3_path}")

    return df

def extract_parquet_from_s3(bucket_name: str, file_key: str) -> pd.DataFrame:
    """
    Read Parquet file from s3 bucket.
    """

    _, storage_options = get_s3_client_and_storage_options()

    s3_path = f"s3://{bucket_name}/{file_key}"
    logging.info(f"S3 path: {s3_path}")

    try:
        df = pd.read_parquet(s3_path, storage_options=storage_options)
    except Exception:
        logging.error(f"Failed to extract Parquet from S3: {s3_path}")
        raise

    logging.info(f"Successfully extracted Parquet from S3: {s3_path}")

    return df


def extract_from_s3(bucket_name: str, file_key: str, file_type: str, **kwargs,) -> pd.DataFrame:
    """
    Read a file from an S3 bucket into a pandas DataFrame.

    Supported file types:
        - csv
        - json
        - parquet
    """

    readers = {
        "csv": pd.read_csv,
        "json": pd.read_json,
        "parquet": pd.read_parquet,
    }

    if file_type not in readers:
        raise ValueError(
            f"Unsupported file type '{file_type}'. "
            f"Supported types: {', '.join(readers.keys())}"
        )

    _, storage_options = get_s3_client_and_storage_options()

    s3_path = f"s3://{bucket_name}/{file_key}"
    logging.info(f"S3 path: {s3_path}")

    try:
        df = readers[file_type](
            s3_path,
            storage_options=storage_options,
            **kwargs,
        )
    except Exception:
        logging.exception(
            f"Failed to extract {file_type.upper()} from S3: {s3_path}"
        )
        raise

    logging.info(
        f"Successfully extracted {file_type.upper()} from S3: {s3_path}"
    )

    return df