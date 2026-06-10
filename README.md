# CareSignal AI 🏥

A real-time patient medication adherence monitoring system built on Google Cloud Platform. The system identifies high-risk Medicare patients before they end up in the emergency room.

## The Problem
A patient's data lives in 3 different systems that never talk to each other — pharmacy claims, medical claims, and beneficiary records. Nobody catches warning signs until it's too late.

## The Solution
CareSignal AI connects these three data sources, calculates medication adherence scores in real time, and uses AI to generate plain-English explanations for case managers — enabling intervention before a crisis occurs.

## Live Dashboard
[View Patient Adherence Dashboard](https://datastudio.google.com/reporting/9414d1ec-2624-4328-b080-2d8213110e7c)

## Architecture
```
Raw Claims → BigQuery → dbt Models → Kafka Alerts → RAG Explanations → Looker Studio
```

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Data Storage | Google BigQuery |
| Data Transformation | dbt (staging + mart models) |
| Real-time Streaming | Apache Kafka |
| AI Explanation | Groq + Llama 3 (RAG) |
| Dashboard | Looker Studio |
| Infrastructure | Terraform |
| Orchestration | Docker |

## Key Metrics
- **1,000** synthetic Medicare patients
- **24,000** pharmacy claims
- **2,761** medical/ER claims
- **537** high-risk patients identified (PDC < 0.80)
- **Real-time alerts** fired via Kafka when PDC drops below threshold

## What is PDC?
PDC (Proportion of Days Covered) is the standard CMS metric for medication adherence. A score below 0.80 indicates a patient is not taking their medication consistently and is at risk of hospitalization.

## Project Structure
```
caresignal-ai/
├── ingestion/          # Data generation and BigQuery loading
│   ├── generate_data.py
│   └── load_to_bigquery.py
├── dbt_project/        # dbt transformation models
│   └── models/
│       ├── staging/    # stg_beneficiaries, stg_pharmacy_claims, stg_medical_claims
│       └── marts/      # mart_patient_timeline
├── kafka/              # Real-time alerting
│   ├── producer.py     # Reads high-risk patients from BigQuery
│   ├── consumer.py     # Processes alerts for case managers
│   └── docker-compose.yml
├── rag/                # AI explanation layer
│   └── rag_explainer.py  # Groq Llama 3 RAG pipeline
├── terraform/          # Infrastructure as code
│   ├── main.tf
│   └── variables.tf
└── dashboard/          # Looker Studio screenshots
```

## How to Run

### Prerequisites
- Python 3.11+
- Docker Desktop
- Google Cloud SDK
- Terraform

### Setup
```bash
# Clone the repo
git clone https://github.com/riyapatel-04/caresignal-ai.git
cd caresignal-ai

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file and add your GROQ_API_KEY
```

### Run the Pipeline
```bash
# Generate and load data
python ingestion/generate_data.py
python ingestion/load_to_bigquery.py

# Run dbt models
cd dbt_project
dbt run

# Start Kafka
cd ../kafka
docker-compose up -d

# Run producer and consumer (in separate terminals)
python kafka/producer.py
python kafka/consumer.py

# Run RAG explainer
python rag/rag_explainer.py
```

## Sample AI Output
```
Elizabeth House is a 75-year-old female patient with hypertension,
who is at high risk due to a low adherence score (PDC: 0.79) and
5 missed medication refills. Recent pharmacy history shows multiple
missed Lisinopril refills. Recommend immediate outreach call to
assess barriers to medication access.
```

## Why This Matters
This project mirrors the infrastructure problem Mayo Clinic and Microsoft
announced solving at scale in 2026 — synthesizing diverse clinical data
for earlier diagnosis and more personalized treatment decisions.
