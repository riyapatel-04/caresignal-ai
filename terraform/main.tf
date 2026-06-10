terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project     = "caresignal-ai"
  region      = "us-central1"
  credentials = file("C:/Users/RIYA/credentials.json")
}

# BigQuery dataset - raw data
resource "google_bigquery_dataset" "caresignal_dev" {
  dataset_id    = "caresignal_dev"
  friendly_name = "CareSignal Raw Data"
  description   = "Raw ingested data for CareSignal AI"
  location      = "US"
}

# BigQuery dataset - marts
resource "google_bigquery_dataset" "caresignal_dev_marts" {
  dataset_id    = "caresignal_dev_marts"
  friendly_name = "CareSignal Mart Layer"
  description   = "dbt mart models for CareSignal AI"
  location      = "US"
}

# BigQuery dataset - staging
resource "google_bigquery_dataset" "caresignal_dev_staging" {
  dataset_id    = "caresignal_dev_staging"
  friendly_name = "CareSignal Staging Layer"
  description   = "dbt staging models for CareSignal AI"
  location      = "US"
}

# GCS bucket for raw data files
resource "google_storage_bucket" "caresignal_raw" {
  name          = "caresignal-ai-raw-data"
  location      = "US"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}