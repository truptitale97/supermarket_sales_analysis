import os
import pandas as pd
from google.cloud import bigquery

# Authenticate to gcp
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\TRUPTI\Downloads\supermarketsales-456610-688bbd04f1ea.json"

# Load the data
df = pd.read_csv(r"C:\Users\TRUPTI\Downloads\supermarket_sales - Sheet1.csv")

# Transform dimension tables

# Create Date Dim Table
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
df['Month'] = df['Date'].dt.month_name()
df['Year'] = df['Date'].dt.year

dim_date = df[['Date', 'Time', 'Month', 'Year']].drop_duplicates().reset_index(drop=True)

# Create CUSTOMER_PRODUCT Dim Table
dim_customer_product = df[['Invoice ID', 'Customer type', 'Gender', 'Product line', 'Branch', 'City','Payment']].drop_duplicates().reset_index(drop=True)

# Create FACT_SALES
fact_sales = df[[
    'Invoice ID', 'Date', 'Quantity', 'Total',  'Rating',
    'Unit price', 'Tax 5%', 'cogs', 'gross margin percentage', 'gross income'
]]

# Create BigQuery Dataset 
project_id = "supermarketsales-456610"
dataset_id = "supermarket_sales"

client = bigquery.Client(project=project_id)

# Create dataset if it doesn't exist
def create_dataset():
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset_ref.location = "US"
    try:
        client.create_dataset(dataset_ref)
        print("Dataset created.")
    except:
        print("Dataset already exists.")

create_dataset()

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
