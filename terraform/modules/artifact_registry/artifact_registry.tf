resource "google_artifact_registry_repository" "artifact_registry" {
    for_each = toset(var.artifact_registries)
    location      = var.region
    repository_id = each.key
    format        = "DOCKER"
}