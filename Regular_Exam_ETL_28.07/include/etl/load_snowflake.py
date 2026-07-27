from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

def load_enrich_to_snowflake(snowflake_conn_id: str):
    hook = SnowflakeHook(
        snowflake_conn_id=snowflake_conn_id
    )

    sql = """
    COPY INTO CLEANSED_LAYER.SALES_CLEAN
    FROM @STAGING_LAYER.RETAIL_STAGE
    FILE_FORMAT = (FORMAT_NAME = STAGING_LAYER.CSV_FORMAT)
    FILES = ('enrich.csv');
    """

    hook.run(sql)