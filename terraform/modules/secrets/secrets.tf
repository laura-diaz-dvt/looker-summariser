## Secrets
resource "google_secret_manager_secret" "secret" {
  for_each  = var.secrets
  secret_id = each.value.secret_id
  replication {
    user_managed {
      replicas {
        location = "europe-west1"
      }
    }
  }
}
