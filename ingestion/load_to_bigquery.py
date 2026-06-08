from google.cloud import bigquery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\RIYA\credentials.json"

client = bigquery.Client(project="caresignal-ai")
dataset_id = "caresignal_dev"

# create dataset if it doesn't exist
dataset_ref = bigquery.Dataset(f"caresignal-ai.{dataset_id}")
dataset_ref.location = "US"
try:
    client.create_dataset(dataset_ref)
    print(f"Dataset {dataset_id} created")
except Exception:
    print(f"Dataset {dataset_id} already exists")

# files to load
tables = [
    {"file": "ingestion/beneficiaries.csv", "table": "raw_beneficiaries"},
    {"file": "ingestion/pharmacy_claims.csv", "table": "raw_pharmacy_claims"},
    {"file": "ingestion/medical_claims.csv", "table": "raw_medical_claims"},
]

job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    autodetect=True,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)

for t in tables:
    with open(t["file"], "rb") as f:
        job = client.load_table_from_file(
            f,
            f"caresignal-ai.{dataset_id}.{t['table']}",
            job_config=job_config,
        )
        job.result()
        table = client.get_table(f"caresignal-ai.{dataset_id}.{t['table']}")
        print(f"{t['table']} loaded — {table.num_rows} rows")

print("\nAll tables loaded into BigQuery successfully!")