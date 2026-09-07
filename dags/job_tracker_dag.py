from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

from data_pipeline import extract_data, transform_data, load_data

default_args = {
    "owner": "data-engineer",
    "depends_on_past": False,
    "start_date": datetime(2026, 9, 7),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def extract_job_data(**context):
    raw_data = extract_data(search_term="software developer", results_per_page=10)
    context["ti"].xcom_push(key="raw_data", value=raw_data)

def transform_job_data(**context):
    ti = context["ti"]
    raw_data = ti.xcom_pull(task_ids="extract_job_data", key="raw_data")

    if raw_data:
        cleaned_data = transform_data(raw_data)
        ti.xcom_push(key="clean_data", value=cleaned_data)
    else:
        raise ValueError("No raw data available to transform.")

def load_job_data(**context):
    ti = context["ti"]
    cleaned_data = ti.xcom_pull(task_ids="transform_job_data", key="clean_data")

    if cleaned_data:
        load_data(cleaned_data)
    else:
        raise ValueError("No transformed data available to load.")

with DAG(
    dag_id="job_tracker_etl",
    default_args=default_args,
    description="Daily job-tracker ETL pipeline",
    schedule_interval="@daily",
    catchup=False,
    tags=["jobs", "etl"],
) as dag:

    task_extract = PythonOperator(
        task_id="extract_job_data",
        python_callable=extract_job_data,
    )

    task_transform = PythonOperator(
        task_id="transform_job_data",
        python_callable=transform_job_data,
    )

    task_load = PythonOperator(
        task_id="load_job_data",
        python_callable=load_job_data,
    )

    task_extract >> task_transform >> task_load