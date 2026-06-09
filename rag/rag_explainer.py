import os
from dotenv import load_dotenv
from google.cloud import bigquery
from groq import Groq

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\RIYA\credentials.json"

client_ai = Groq(api_key=os.getenv("GROQ_API_KEY"))
client_bq = bigquery.Client(project="caresignal-ai")

def get_patient_data(beneficiary_id):
    query = f"""
        SELECT *
        FROM `caresignal-ai.caresignal_dev_marts.mart_patient_timeline`
        WHERE beneficiary_id = '{beneficiary_id}'
        LIMIT 1
    """
    rows = list(client_bq.query(query).result())
    return rows[0] if rows else None

def get_pharmacy_history(beneficiary_id):
    query = f"""
        SELECT drug_name, fill_date, missed_refill, days_supply
        FROM `caresignal-ai.caresignal_dev.raw_pharmacy_claims`
        WHERE beneficiary_id = '{beneficiary_id}'
        ORDER BY fill_date DESC
        LIMIT 10
    """
    return list(client_bq.query(query).result())

def generate_explanation(patient, pharmacy_history):
    history_text = "\n".join([
        f"- {row.drug_name}: filled {row.fill_date}, missed={row.missed_refill}"
        for row in pharmacy_history
    ])

    prompt = f"""
You are a clinical data analyst. Based on the following patient data, write a clear,
concise 3-4 sentence explanation for a case manager explaining why this patient is
high risk and what action should be taken. Use only the data provided.

PATIENT DATA:
- Name: {patient.first_name} {patient.last_name}
- Age: {patient.age}
- Gender: {patient.gender}
- Primary Condition: {patient.primary_condition}
- PDC Score: {patient.pdc_score} (threshold: 0.80)
- Total Missed Refills: {patient.total_missed_refills}
- Total ER Visits: {patient.total_er_visits}
- Drugs Prescribed: {patient.drugs_prescribed}
- Total Medical Cost: ${patient.total_charge_amount}

RECENT PHARMACY HISTORY (last 10 fills):
{history_text}

Write the explanation now:
"""

    response = client_ai.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3
    )

    return response.choices[0].message.content

def run_rag_for_high_risk_patients():
    query = """
        SELECT beneficiary_id, first_name, last_name
        FROM `caresignal-ai.caresignal_dev_marts.mart_patient_timeline`
        WHERE adherence_risk_level = 'HIGH'
        LIMIT 5
    """
    patients = list(client_bq.query(query).result())

    for p in patients:
        print(f"\n{'='*60}")
        print(f"Patient: {p.first_name} {p.last_name} ({p.beneficiary_id})")
        print('='*60)

        patient = get_patient_data(p.beneficiary_id)
        pharmacy_history = get_pharmacy_history(p.beneficiary_id)
        explanation = generate_explanation(patient, pharmacy_history)

        print(f"\nAI EXPLANATION:")
        print(explanation)
        print()

if __name__ == "__main__":
    run_rag_for_high_risk_patients()