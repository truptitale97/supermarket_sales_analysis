import os
import pandas as pd
from google.cloud import storage, bigquery

# Authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\TRUPTI\Downloads\supermarketsales-456610-688bbd04f1ea.json"

# Configuration
project_id = "supermarketsales-456610"
dataset_id = "supermarket_sales"
bucket_name = "gcs-bucket-name"  
source_file_path = r"C:\Users\TRUPTI\Downloads\supermarket_sales - Sheet1.csv"
gcs_blob_name = "supermarket_sales.csv"

# Upload CSV to GCS
def upload_to_gcs():
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(gcs_blob_name)
    blob.upload_from_filename(source_file_path)
    print(" CSV file uploaded to GCS.")

# Load CSV from GCS to BigQuery raw table
def load_to_bigquery():
    client = bigquery.Client(project=project_id)
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset_ref.location = "US"

    try:
        client.create_dataset(dataset_ref)
        print("Dataset created.")
    except:
        print("Dataset already exists.")

    table_id = f"{project_id}.{dataset_id}.raw_sales"
    gcs_uri = f"gs://{bucket_name}/{gcs_blob_name}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
    )

    load_job = client.load_table_from_uri(
        gcs_uri, table_id, job_config=job_config
    )
    load_job.result()
    print("Raw data loaded into BigQuery.")

# Read raw data from BigQuery and transform
def transform_and_upload():
    client = bigquery.Client(project=project_id)

    # Read raw data from BigQuery
    query = f"SELECT * FROM `{project_id}.{dataset_id}.raw_sales`"
    df = client.query(query).to_dataframe()

    # Transformations

    # Create DATE Dim table
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    df['Month'] = df['Date'].dt.month_name()
    df['Year'] = df['Date'].dt.year
    dim_date = df[['Date', 'Time', 'Month', 'Year']].drop_duplicates().reset_index(drop=True)

    # Create CUSTOMER_PRODUCT Dim Table
    dim_customer_product = df[['Invoice ID', 'Customer type', 'Gender', 'Product line', 'Branch', 'City']].drop_duplicates().reset_index(drop=True)

    # Create FACT_SALES
    fact_sales = df[[
        'Invoice ID', 'Date', 'Quantity', 'Total', 'Payment', 'Rating',
        'Unit price', 'Tax 5%', 'cogs', 'gross margin percentage', 'gross income'
    ]]

    # Upload function
    def upload_table(df, table_name):
        table_id = f"{project_id}.{dataset_id}.{table_name}"
        job = client.load_table_from_dataframe(df, table_id)
        job.result()
        print(f"Uploaded table: {table_name}")

    # Upload all tables
    upload_table(dim_date, "dim_date")
    upload_table(dim_customer_product, "dim_customer_product")
    upload_table(fact_sales, "fact_sales")

# Run all functions
upload_to_gcs()
load_to_bigquery()
transform_and_upload()
