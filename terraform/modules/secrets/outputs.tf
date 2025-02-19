output "secrets" {
  value       = { for k, v in google_secret_manager_secret.secret : k => v }
  description = "The ids of the created secrets."
}
