# GloboRetail Analytics ETL + ELT Pipeline

## Project Overview

This project implements a modern hybrid **ETL + ELT pipeline** for the GloboRetail analytics platform.

The pipeline extracts raw retail data from Amazon S3, validates and transforms the data using Python and Pandera, stores the processed data back into S3, and then loads it into Snowflake where the final ELT transformations are performed.

The final Snowflake environment contains:

* CLEANSED layer tables
* BUSINESS layer Star Schema
* PRESENTATION layer Materialized Views for analytics

---

# Architecture Flow

```
Amazon S3 (RAW Zone)
        |
        |
        v
Airflow ETL Pipeline
        |
        |
        +--> Extract data using pandas
        |
        +--> Validate input data (Pandera)
        |
        +--> Transform sales and products
        |
        +--> Validate output schema
        |
        v
Amazon S3 (Processed Zone)
        |
        |
        v
Snowflake ELT Layer
        |
        |
        +--> CLEANSED_LAYER.SALES_CLEAN
        |
        +--> BUSINESS_LAYER
        |       |
        |       +--> DIM_DATE
        |       +--> DIM_PRODUCT
        |       +--> FACT_SALES
        |
        v
Presentation Layer
        |
        +--> Materialized Views
```

---

# Project Structure

```
.
├── dags
│   └── retail_etl_dag.py
│
├── include
│   ├── config.yaml
│   ├── etl
│   │   ├── extract_s3.py
│   │   ├── transform.py
│   │   ├── load_s3_json_or_csv.py
│   │   └── load_snowflake.py
│   │
│   ├── pipelines
│   │   └── retail_pipeline.py
│   │
│   ├── validations
│   │   ├── input_schemas.py
│   │   ├── output_schemas.py
│   │   ├── validate_inputs.py
│   │   └── validate_outputs.py
│   │
│   └── s3_utils.py
│
├── sql
│   └── setup_snowflake.sql
│
├── requirements.txt
├── Dockerfile
├── README.md
└── screenshots
```

---

# Pipeline Execution

## Step 1 - Snowflake Setup

Before running the pipeline, execute:

```
sql/setup_snowflake.sql
```

This creates automatically:

* ROLE
* WAREHOUSE
* DATABASE
* SCHEMAS
* FILE FORMAT
* S3 STAGE
* CLEANSED tables
* BUSINESS Star Schema tables
* PRESENTATION Materialized Views

---

## Step 2 - Start Airflow Pipeline

After the Snowflake structure is created, the project can be started from Airflow.

The DAG:

```
dags/retail_etl_dag.py
```

automatically executes the ETL process:

1. Extract raw sales and product data from S3
2. Validate input datasets
3. Transform sales and product data
4. Merge and enrich datasets
5. Validate final output schema
6. Upload processed files back to S3

Example processed output:

```
s3://data-warehouse-bobby/RegularExamETL/output_folder/
```

---

## Step 3 - Load Data Into Snowflake

After the Airflow ETL pipeline finishes successfully, the processed data is available in S3.

The Snowflake loading step imports the processed file:

```
COPY INTO CLEANSED_LAYER.SALES_CLEAN
FROM @STAGING_LAYER.RETAIL_STAGE
FILE_FORMAT = STAGING_LAYER.CSV_FORMAT;
```

Example:

```
COPY INTO CLEANSED_LAYER.SALES_CLEAN
FILES=('enrich.csv');
```

After loading:

```
CLEANSED_LAYER.SALES_CLEAN
```

contains the validated enriched retail dataset.

---

## Step 4 - Build Analytics Layer

After the data is loaded into Snowflake, execute the remaining SQL transformations.

The ELT process creates:

### Star Schema

```
BUSINESS_LAYER.DIM_DATE

BUSINESS_LAYER.DIM_PRODUCT

BUSINESS_LAYER.FACT_SALES
```

### Analytical Views

```
PRESENTATION_LAYER.MV_SALES_BY_REGION_MONTH

PRESENTATION_LAYER.MV_TOP_PRODUCTS_BY_REVENUE

PRESENTATION_LAYER.MV_REVENUE_TREND

PRESENTATION_LAYER.MV_CATEGORY_PERFORMANCE
```

These objects are used for reporting and analytics.

---

# Airflow DAG Tasks

The DAG contains the following workflow:

```
extract_group
        |
        |
transform_group
        |
        |
save_processed_data
        |
        |
Snowflake ELT
```

Successful execution can be verified from the Airflow Graph view.

---

# Validation

## Input Validation

Implemented with Pandera.

Checks:

* Required columns
* Null IDs
* Negative prices
* Invalid timestamps
* Incorrect datatypes

## Output Validation

Checks:

* Correct datatypes
* Complete records
* Positive sales values
* Required fields are not null

---

# Technologies Used

* Python
* Apache Airflow
* Pandas
* Pandera
* Amazon S3
* Snowflake
* SQL
* Docker

---

# Screenshots Included

The `screenshots` folder contains evidence of:

1. Airflow DAG Graph execution
2. Successful ETL pipeline run
3. Snowflake CLEANSED_LAYER tables
4. Star Schema tables
5. Materialized Views populated

---

# Final Workflow Summary

1. Create Snowflake infrastructure using `setup_snowflake.sql`
2. Start Airflow project
3. Run `retail_etl_dag`
4. Data is extracted, validated, transformed and uploaded to S3
5. Snowflake loads the processed file into CLEANSED_LAYER
6. Run Star Schema and Materialized View SQL queries
7. Analytics layer becomes ready for reporting
