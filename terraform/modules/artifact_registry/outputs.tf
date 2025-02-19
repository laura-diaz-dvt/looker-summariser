output "artifact_registry" {
    value = {for k, v in google_artifact_registry_repository.artifact_registry: k => v}
}