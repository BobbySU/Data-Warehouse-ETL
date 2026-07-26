import pandas as pd

from include.s3_utils import get_storage_options


def load_df_to_s3_csv(df: pd.DataFrame, s3_path: str, aws_conn_id: str):
    s3_hook, storage_options = get_storage_options(aws_conn_id)

    try:
        df.to_csv(s3_path, index=False, storage_options=storage_options)
    except Exception as e:
        print(f"Error uploading file to s3: {e}")
        raise

    print(f"Finished writing CSV to s3 {s3_path}")