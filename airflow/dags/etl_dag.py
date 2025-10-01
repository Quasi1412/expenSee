import os
from datetime import datetime
from airflow import DAG

from airflow.operators.python import PythonOperator
from extract.fetch_data import fetch_transactions
from transform.normalise_data import normalise_df
from load.add_to_postgresdb import push_data_to_db

local_workflow = DAG(
    "LocalIngestionDAG",
    schedule = "0 12 30 * *",
    start_date = None    
)

AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME","/opt/airflow/")

PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_DATABASE = os.getenv('PG_DATABASE')
PG_CONN_URL = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}'

STATEMENTS_DIR = os.getenv('STATEMENTS_DIR','/opt/airflow/statements')
FINAL_DF_DIR = '/opt/airflow/final_df.csv'

with local_workflow:
    fetch_data_task = PythonOperator(
        task_id = 'extract_data_from_statements',
        python_callable = fetch_transactions,
        op_kwargs = dict(parent_directory = STATEMENTS_DIR,output_dir = 'extracted'),

    )
    
    transform_data_task = PythonOperator(
        task_id = 'transform_by_normalising_data',
        python_callable = normalise_df,
        op_kwargs = dict(input_files = "{{ti.xcom_pull(task_ids = 'extract_data_from_statements')}}",output_file = FINAL_DF_DIR),
    )
    
    load_data_task = PythonOperator(
        task_id = 'load_data_to_postgres',
        python_callable = push_data_to_db,
        op_kwargs = dict(csv_file = "{{ti.xcom_pull(task_ids = 'transform_by_normalising_data')}}",PG_URL = PG_CONN_URL)
    )
    
fetch_data_task >> transform_data_task >> load_data_task