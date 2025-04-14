import os
import zipfile
import pandas as pd
import subprocess

# Set the Kaggle config directory 
kaggle_dir = os.path.join(os.environ['USERPROFILE'], '.kaggle')
os.environ['KAGGLE_CONFIG_DIR'] = kaggle_dir

# Download dataset using Kaggle API
subprocess.run(["kaggle", "datasets", "download", "-d", "aungpyaeap/supermarket-sales"], check=True)

#Unzip the dataset
with zipfile.ZipFile("supermarket-sales.zip", 'r') as zip_ref:
    zip_ref.extractall("supermarket_data")

# Read the CSV file
csv_path = os.path.join("supermarket_data", "supermarket_sales - Sheet1.csv")
df = pd.read_csv(csv_path)

print(df.head())

