import os
import logging

from dotenv import load_dotenv

# Показва логовете /в червено са/

logging.basicConfig(
    level=logging.INFO,
    format=("%(asctime)s" " - " "%(name)s" " - " "%(levelname)s: %(message)s")
)

load_dotenv()

# AWS Cred
AWS_KEY = os.getenv("AWS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_FOLDER_PREFIX = os.getenv("AWS_FOLDER_PREFIX")

AWS_FILE_PATH_CSV = os.getenv("AWS_FILE_PATH_CSV")
AWS_FILE_PATH_PARQUET = os.getenv("AWS_FILE_PATH_PARQUET")
AWS_FILE_PATH_JSON = os.getenv("AWS_FILE_PATH_JSON")

# PostgreSQL Cred
POSTGRESQL_USER = os.getenv("POSTGRESQL_USER")
POSTGRESQL_PASSWORD = os.getenv("POSTGRESQL_PASSWORD")
POSTGRESQL_HOST = os.getenv("POSTGRESQL_HOST")
POSTGRESQL_PORT = os.getenv("POSTGRESQL_PORT")
POSTGRESQL_DATABASE = os.getenv("POSTGRESQL_DATABASE")