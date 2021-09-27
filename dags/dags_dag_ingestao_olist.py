from datetime import timedelta, date 
import configparser
import os
import sys
from airflow import models
from airflow.models import Variable
from airflow.providers.google.cloud.operators.dataflow import DataflowTemplatedJobStartOperator
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
from airflow.operators import BashOperator 
from airflow.utils.dates import days_ago

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURR_DIR)


config = configparser.ConfigParser()
config.read(CURR_DIR + '/config.cfg')
config_options = dict(config[Variable.get('ENVIRONMENT')])

current_date = str(date.today())

default_args = {
    "owner":"airflow",
    "depends_on_past":False,
    "start_date": days_ago(1),
    "email_on_failure":False,
    "email_on_retry":False,
    "retries":0
}

dataflow_default_options = {
    "project": config_options['project'],
    "staging_location": config_options['staging_location'],
    "temp_location": config_options['temp_location'],
    "service_account_email": config_options['service_account_email'],
}


with models.DAG(
    "olist_etl",
        default_args=default_args,
    schedule_interval=timedelta(days=1),  # Override to match your needs
) as dag:

    start_template_job = DataflowTemplatedJobStartOperator(
        task_id="dataflow_olist_data_process",       
        gcp_conn_id=config_options['gcp_conn_id'],
        template=config_options['template'],
        dataflow_default_options=dataflow_default_options, 
        parameters={     
            "input_itens": config_options['input_itens'],
            "input_seller": config_options['input_seller'],
            "input_products": config_options['input_products'],
            "input_order": config_options['input_order'],
            "input_reviews": config_options['input_reviews'],
            "input_payments": config_options['input_payments'],
            "input_customer": config_options['input_customer'],
            "output": config_options['output'],
            "partition_date":current_date
        }
    )

    bq_load_olist_cleared_data = GoogleCloudStorageToBigQueryOperator(

        task_id = "bq_load_olist_cleared_data",
        bucket='olist_etl',
        source_objects=["output/output-00000-of-00001.csv"],
        destination_project_dataset_table=config_options['bq_table_id'],
        bigquery_conn_id=config_options['bigquery_default'],        
       # WRITE_DISPOSITION_UNSPECIFIED, WRITE_EMPTY, WRITE_TRUNCATE, WRITE_APPEND
        create_disposition="CREATE_IF_NEEDED",
        skip_leading_rows=1,
        write_disposition="WRITE_APPEND",
        max_bad_records=0,
        source_format='CSV',
        #GZIP or NONE
        compression='NONE',

        field_delimiter=',',
        quote_character=None,
        ignore_unknown_values=False,
        allow_quoted_newlines=False,
        allow_jagged_rows=False,
        encoding='UTF-8',
        max_id_key=None,
        autodetect=False,
        schema_fields=[
        {
            "mode": "REQUIRED",
            "name": "partition_date",
            "type": "DATE"
        },
        {
            "mode": "REQUIRED",
            "name": "order_id",
            "type": "STRING"
        },
            {
            "mode": "REQUIRED",
            "name": "order_status",
            "type": "STRING"
        },
        {
            "mode": "NULLABLE",
            "name": "order_purchase_timestamp",
            "type": "DATE"
        },
        {
            "mode": "NULLABLE",
            "name": "order_approved_at",
            "type": "DATE"
        },
        {
            "mode": "NULLABLE",
            "name": "order_delivered_carrier_date",
            "type": "DATE"
        },
        {
            "mode": "NULLABLE",
            "name": "order_delivered_customer_date",
            "type": "DATE"
        },
        {
            "mode": "NULLABLE",
            "name": "order_estimated_delivery_date",
            "type": "DATE"
        },  
        {
            "mode": "REQUIRED",
            "name": "payment_sequential",
            "type": "INTEGER"
        },
        {
            "mode": "REQUIRED",
            "name": "payment_type",
            "type": "STRING"
        },
        {
            "mode": "REQUIRED",
            "name": "payment_installments",
            "type": "INTEGER"
        },
        {
            "mode": "REQUIRED",
            "name": "payment_value",
            "type": "FLOAT"
        },
        {
            "mode": "REQUIRED",
            "name": "review_score",
            "type": "STRING"
        },
        {
            "mode": "REQUIRED",
            "name": "customer_id",
            "type": "STRING"
        },
        {
            "mode": "REQUIRED",
            "name": "customer_city",
            "type": "STRING"
        },
        {
            "mode": "REQUIRED",
            "name": "customer_state",
            "type": "STRING"
        },
            {
            "mode": "NULLABLE",
            "name": "shipping_limit_date",
            "type": "DATE"
        },
        {
            "mode": "REQUIRED",
            "name": "product_id",
            "type": "STRING"
        },
        {
            "mode": "NULLABLE",
            "name": "product_category_name",
            "type": "STRING"
        },
        {
            "mode": "REQUIRED",
            "name": "itens_count",
            "type": "INTEGER"
        },
        {
            "mode": "REQUIRED",
            "name": "price",
            "type": "FLOAT"
        },
        {
            "mode": "REQUIRED",
            "name": "freight_value",
            "type": "FLOAT"
        },
        {
            "mode": "REQUIRED",
            "name": "seller_id",
            "type": "STRING"
        },
        {
            "mode": "REQUIRED",
            "name": "seller_city",
            "type": "STRING"
        },
        {
            "mode": "REQUIRED",
            "name": "seller_state",
            "type": "STRING"
        }
        ]
    )    
  
    delete_tranformed_files = BashOperator(
        task_id = "delete_tranformed_files",
        bash_command = "gsutil -m rm -r gs://olist_etl/output/*"
    )

    start_template_job >> bq_load_olist_cleared_data >> delete_tranformed_files

