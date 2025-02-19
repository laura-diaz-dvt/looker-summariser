locals {
    sa_flattened = flatten([
        for sa in var.services_accounts : [
            for role in sa["roles"] : {
                account_id   = sa["account_id"]
                display_name = sa["display_name"]
                role         = role
            }
        ]
    ])
}

resource "google_service_account" "sa_names" {
  project      = var.project
  for_each     = var.services_accounts
  account_id   = each.value["account_id"]
  display_name = each.value["display_name"]
}

resource "google_project_iam_member" "sa_roles" {
  depends_on = [google_service_account.sa_names]
  for_each   = {for idx, sa in local.sa_flattened: "${sa["account_id"]}_${sa["role"]}" => sa}
  project    = var.project
  role       = each.value["role"]
  member     = "serviceAccount:${each.value["account_id"]}@${var.project}.iam.gserviceaccount.com"
}