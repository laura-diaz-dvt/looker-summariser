variable "secrets" {
  type = map(object({
    secret_id = string
  }))
  description = "A map of secrets to create."
}
