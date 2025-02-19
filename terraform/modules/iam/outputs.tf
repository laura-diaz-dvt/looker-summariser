output "service_account" {
    value = {for k, v in google_service_account.sa_names: k => v}
}