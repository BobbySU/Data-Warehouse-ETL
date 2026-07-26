from airflow.sdk import dag
from pendulum import datetime

from include.pipelines.retail_pipeline import build_retail_pipeline


@dag(
    schedule=None,
    start_date=datetime(year=2021, month=1, day=1),
    catchup=False,
    tags=["retail"]
)
def retail_etl_dag():
    build_retail_pipeline()


retail_etl_dag()