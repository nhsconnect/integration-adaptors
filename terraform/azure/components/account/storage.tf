
resource "azurerm_storage_account" "account_bucket_sa" {
  resource_group_name      = var.account_resource_group
  name                     = var.account_bucket_storage_account
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  network_rules {
    bypass = ["AzureServices"]
    default_action="Allow"
  }

  depends_on = [ azurerm_resource_group.account_resource_group ]
}
