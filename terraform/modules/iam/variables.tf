variable "project" {
  description = "The project ID to deploy to"
  type        = string
}

variable "region" {
  description = "The region to deploy to"
  type        = string
}

variable "services_accounts" {
  description = "Object containing service accounts to create"
  type = map(object({
    account_id   = string
    display_name = string
    roles        = list(string)
  }))
}