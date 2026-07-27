import boto3
from config.config import AWS_KEY, AWS_SECRET_KEY


def get_s3_client_and_storage_options():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
    )

    storage_options = {
        "key": AWS_KEY,
        "secret": AWS_SECRET_KEY,
    }

    return s3, storage_options