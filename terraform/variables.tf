variable "project" {
  description = "The project ID to deploy to"
  type        = string
}

variable "region" {
  description = "The region to deploy to"
  type        = string
}

variable "run_hash" {
  description = "The hash of the commit"
  type        = string
}

variable "looker_url" {
  description = "The looker base url to which the actionhub communicates"
  type        = string
}

variable "action_hub_label" {
  description = "The label of the action hub"
  type        = string
}