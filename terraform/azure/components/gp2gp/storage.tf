
resource "azurerm_storage_container" "gp2gp_bucket_container" {
  name = "${local.resource_prefix}-container"
  storage_account_name = data.terraform_remote_state.account.outputs.storage_account_name
}
