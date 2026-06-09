import json
import os
import time
from kafka import KafkaProducer
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\RIYA\credentials.json"

# connect to BigQuery first
print("Connecting to BigQuery...")
client = bigquery.Client(project="caresignal-ai")

query = """
    SELECT
        beneficiary_id,
        first_name,
        last_name,
        primary_condition,
        pdc_score,
        total_missed_refills,
        total_er_visits,
        adherence_risk_level,
        drugs_prescribed
    FROM `caresignal-ai.caresignal_dev_marts.mart_patient_timeline`
    WHERE adherence_risk_level = 'HIGH'
    LIMIT 50
"""

print("Fetching HIGH risk patients from BigQuery...")
rows = list(client.query(query).result())
print(f"Fetched {len(rows)} patients. Connecting to Kafka...")

# connect to Kafka after data is ready
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    request_timeout_ms=30000
)

print("Connected to Kafka. Sending alerts...")
time.sleep(2)

count = 0
for row in rows:
    alert = {
        "beneficiary_id": row.beneficiary_id,
        "first_name": row.first_name,
        "last_name": row.last_name,
        "primary_condition": row.primary_condition,
        "pdc_score": float(row.pdc_score),
        "total_missed_refills": row.total_missed_refills,
        "total_er_visits": row.total_er_visits,
        "adherence_risk_level": row.adherence_risk_level,
        "drugs_prescribed": row.drugs_prescribed,
    }
    producer.send('patient-alerts', value=alert)
    count += 1
    print(f"Alert sent: {row.beneficiary_id} — PDC: {row.pdc_score}")

producer.flush()
print(f"\n{count} alerts sent to Kafka topic 'patient-alerts'")