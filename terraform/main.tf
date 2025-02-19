provider "google" {
  project = var.project
  region  = var.region
}
data "google_project" "project" {}

terraform {
  backend "gcs" {
    bucket = "bucket-looker-summariser"
  }
}

## Secrets
module "secrets" {
  source = "./modules/secrets"
  secrets = {
    action_hub_secret = {
      secret_id = "ACTION_HUB_SECRET"
    },
    cipher_master = {
      secret_id = "CIPHER_MASTER"
    },
    looker_client = {
      secret_id = "LOOKERSDK_CLIENT_ID"
    },
    looker_secret = {
      secret_id = "LOOKERSDK_CLIENT_SECRET"
    }
  }
}

# IAM
module "iam" {
  source  = "./modules/iam"
  project = var.project
  region  = var.region
  services_accounts = {
    "sa-summariser-builder" : {
      "account_id" : "sa-summariser-builder",
      "display_name" : "sa-summariser-builder",
      "roles" : [
        "roles/storage.objectViewer",
        "roles/logging.logWriter",
        "roles/artifactregistry.writer"
      ]
    },
    "sa-summariser" : {
      "account_id" : "sa-summariser",
      "display_name" : "sa-summariser",
      "roles" : [
        "roles/secretmanager.secretAccessor",
        "roles/aiplatform.user",
        "roles/storage.objectUser",
        "roles/logging.logWriter"
      ]
    },
    "sa-actionhub" : {
      "account_id" : "sa-actionhub",
      "display_name" : "sa-actionhub",
      "roles" : [
        "roles/secretmanager.secretAccessor",
      ]
    }
  }
}

# Artifact Registry
module "artifact_registry" {
  source              = "./modules/artifact_registry"
  project             = var.project
  region              = var.region
  artifact_registries = ["summariser-repo"]
}

# Cloud storage to store PDFs
resource "google_storage_bucket" "cf_pdf_bucket" {
  name     = "gcs-${var.project}-pdf-bucket"
  location = var.region
}

resource "google_storage_bucket_iam_member" "pdf_bucket_access" {
  bucket = google_storage_bucket.cf_pdf_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${module.iam.service_account["sa-summariser"].email}"
}

# Cloud storage bucket to store prompts
resource "google_storage_bucket" "cf_prompt_bucket" {
  name     = "gcs-${var.project}-prompt-bucket"
  location = var.region
}

resource "google_storage_bucket_iam_member" "prompt_bucket_access" {
  bucket = google_storage_bucket.cf_prompt_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${module.iam.service_account["sa-summariser"].email}"
}

## Cloud Run for Summariser
resource "google_cloud_run_v2_service" "summariser" {
  name     = "cloud-run-summariser"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"


  template {
    service_account = module.iam.service_account["sa-summariser"].email
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project}/${module.artifact_registry.artifact_registry["summariser-repo"].repository_id}/summariser:${var.run_hash}"
      env {
        name  = "LOOKERSDK_BASE_URL"
        value = var.looker_url
      }
      env {
        name  = "PROJECT_ID"
        value = var.project
      }
      env {
        name  = "PDF_BUCKET"
        value = google_storage_bucket.cf_pdf_bucket.name
      }
      env {
        name  = "PROMPT_BUCKET"
        value = google_storage_bucket.cf_prompt_bucket.name
      }
      env {
        name = "LOOKERSDK_CLIENT_ID"
        value_source {
          secret_key_ref {
            secret  = module.secrets.secrets["looker_client"].secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "LOOKERSDK_CLIENT_SECRET"
        value_source {
          secret_key_ref {
            secret  = module.secrets.secrets["looker_secret"].secret_id
            version = "latest"
          }
        }
      }
      resources {
        limits = {
          memory = "2Gi"
        }
      }
    }
  }
}

resource "google_cloud_run_service_iam_member" "cf-invoker" {
  service  = google_cloud_run_v2_service.summariser.name
  location = google_cloud_run_v2_service.summariser.location
  project  = google_cloud_run_v2_service.summariser.project
  role     = "roles/run.invoker"
  member   = "serviceAccount:${module.iam.service_account["sa-actionhub"].email}"
}

## Cloud Run for Actionhub
resource "google_cloud_run_v2_service" "default" {
  name     = "cloud-run-actionhub"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = module.iam.service_account["sa-actionhub"].email
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project}/${module.artifact_registry.artifact_registry["summariser-repo"].repository_id}/actionhub:${var.run_hash}"
      env {
        name  = "CLOUD_RUN_URL"
        value = google_cloud_run_v2_service.summariser.uri
      }
      # This URI can not be generated from the start, so use the deterministic approach to get the URI
      env {
        name  = "ACTION_HUB_BASE_URL"
        value = "https://cloud-run-actionhub-${data.google_project.project.number}.${var.region}.run.app"
      }
      env {
        name  = "ACTION_HUB_LABEL"
        value = var.action_hub_label
      }
      env {
        name  = "NODE_OPTIONS"
        value = "--max-old-space-size=8192"
      }
      env {
        name = "ACTION_HUB_SECRET"
        value_source {
          secret_key_ref {
            secret  = module.secrets.secrets["action_hub_secret"].name
            version = "latest"
          }
        }
      }
      env {
        name = "CIPHER_MASTER"
        value_source {
          secret_key_ref {
            secret  = module.secrets.secrets["cipher_master"].name
            version = "latest"
          }
        }
      }
      resources {
        limits = {
          memory = "2Gi"
        }
      }
    }
  }
}

resource "google_cloud_run_service_iam_member" "noauth" {
  location = google_cloud_run_v2_service.default.location
  service  = google_cloud_run_v2_service.default.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
