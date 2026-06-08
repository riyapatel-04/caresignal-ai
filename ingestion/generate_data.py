import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)
Faker.seed(42)

# real drugs from CMS Part D data
DRUGS = [
    {"name": "Lisinopril", "condition": "hypertension", "days_supply": 30},
    {"name": "Metformin", "condition": "diabetes", "days_supply": 30},
    {"name": "Atorvastatin", "condition": "heart_disease", "days_supply": 30},
    {"name": "Amlodipine", "condition": "hypertension", "days_supply": 30},
    {"name": "Metoprolol", "condition": "heart_disease", "days_supply": 30},
    {"name": "Omeprazole", "condition": "diabetes", "days_supply": 30},
    {"name": "Levothyroxine", "condition": "hypertension", "days_supply": 90},
    {"name": "Gabapentin", "condition": "heart_disease", "days_supply": 30},
]

CONDITIONS = ["diabetes", "hypertension", "heart_disease"]

# ── 1. BENEFICIARIES ──────────────────────────────────────────────
beneficiaries = []
for i in range(1000):
    bene_id = f"BENE_{i+1:04d}"
    condition = random.choice(CONDITIONS)
    beneficiaries.append({
        "beneficiary_id": bene_id,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "date_of_birth": fake.date_of_birth(minimum_age=65, maximum_age=90).strftime("%Y-%m-%d"),
        "gender": random.choice(["M", "F"]),
        "state": fake.state_abbr(),
        "zip_code": fake.zipcode(),
        "primary_condition": condition,
        "has_diabetes": condition == "diabetes",
        "has_hypertension": condition == "hypertension",
        "has_heart_disease": condition == "heart_disease",
    })

df_bene = pd.DataFrame(beneficiaries)
df_bene.to_csv("ingestion/beneficiaries.csv", index=False)
print(f"beneficiaries.csv — {len(df_bene)} rows")

# ── 2. PHARMACY CLAIMS ────────────────────────────────────────────
pharmacy_claims = []
claim_id = 1

for bene in beneficiaries:
    # each patient gets 1-2 drugs matching their condition
    matching_drugs = [d for d in DRUGS if d["condition"] == bene["primary_condition"]]
    assigned_drugs = random.sample(matching_drugs, k=min(2, len(matching_drugs)))

    for drug in assigned_drugs:
        # simulate 12 months of refills
        fill_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 30))

        for refill in range(12):
            # 20% chance of missing a refill (late by 5-15 days)
            missed = random.random() < 0.20
            if missed:
                fill_date += timedelta(days=drug["days_supply"] + random.randint(5, 15))
            else:
                fill_date += timedelta(days=drug["days_supply"])

            pharmacy_claims.append({
                "claim_id": f"RX_{claim_id:06d}",
                "beneficiary_id": bene["beneficiary_id"],
                "drug_name": drug["name"],
                "fill_date": fill_date.strftime("%Y-%m-%d"),
                "days_supply": drug["days_supply"],
                "quantity": drug["days_supply"],
                "refill_number": refill + 1,
                "missed_refill": missed,
                "prescriber_state": bene["state"],
                "total_drug_cost": round(random.uniform(10, 300), 2),
            })
            claim_id += 1

df_rx = pd.DataFrame(pharmacy_claims)
df_rx.to_csv("ingestion/pharmacy_claims.csv", index=False)
print(f"pharmacy_claims.csv — {len(df_rx)} rows")

# ── 3. MEDICAL CLAIMS ─────────────────────────────────────────────
DIAGNOSIS_CODES = {
    "diabetes": ["E11.9", "E11.65", "E11.40"],
    "hypertension": ["I10", "I11.9", "I12.9"],
    "heart_disease": ["I25.10", "I50.9", "I21.9"],
}

medical_claims = []
med_claim_id = 1

for bene in beneficiaries:
    # patients who missed refills are more likely to have ER visits
    missed_refills = sum(1 for rx in pharmacy_claims
                        if rx["beneficiary_id"] == bene["beneficiary_id"]
                        and rx["missed_refill"])

    # base 1-2 visits, +1 for every 3 missed refills
    num_visits = random.randint(1, 2) + (missed_refills // 3)

    for _ in range(num_visits):
        visit_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))
        claim_type = random.choice(["ER", "Inpatient", "Outpatient"])

        medical_claims.append({
            "claim_id": f"MED_{med_claim_id:06d}",
            "beneficiary_id": bene["beneficiary_id"],
            "claim_type": claim_type,
            "visit_date": visit_date.strftime("%Y-%m-%d"),
            "diagnosis_code": random.choice(DIAGNOSIS_CODES[bene["primary_condition"]]),
            "diagnosis_description": bene["primary_condition"].replace("_", " ").title(),
            "total_charge_amount": round(random.uniform(500, 50000), 2),
            "medicare_payment_amount": round(random.uniform(200, 30000), 2),
            "provider_state": bene["state"],
        })
        med_claim_id += 1

df_med = pd.DataFrame(medical_claims)
df_med.to_csv("ingestion/medical_claims.csv", index=False)
print(f"medical_claims.csv — {len(df_med)} rows")

print("\nAll 3 datasets generated successfully!")