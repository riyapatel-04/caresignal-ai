import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'patient-alerts',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Listening for patient alerts...\n")

for message in consumer:
    alert = message.value
    print("=" * 60)
    print(f"ALERT: High Risk Patient Detected")
    print(f"Patient:    {alert['first_name']} {alert['last_name']} ({alert['beneficiary_id']})")
    print(f"Condition:  {alert['primary_condition'].title()}")
    print(f"PDC Score:  {alert['pdc_score']} (below 0.80 threshold)")
    print(f"Missed Refills: {alert['total_missed_refills']}")
    print(f"ER Visits:  {alert['total_er_visits']}")
    print(f"Drugs:      {alert['drugs_prescribed']}")
    print(f"ACTION:     Assign case manager for outreach call")
    print("=" * 60)
    print()