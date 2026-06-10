variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "caresignal-ai"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "location" {
  description = "BigQuery dataset location"
  type        = string
  default     = "US"
}