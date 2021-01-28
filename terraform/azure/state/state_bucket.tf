terraform {
  required_version = ">= 0.14"
}

provider "azurerm" {
  #version = "~>2.44.0"
  features {}
}

resource "azurerm_resource_group" "state_bucket_rg" {
  name     = var.state_bucket_resource_group
  location = var.location
}

resource "azurerm_storage_account" "state_bucket_sa" {
  resource_group_name      = var.state_bucket_resource_group
  name                     = var.state_bucket_storage_account
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  network_rules {
    bypass = ["AzureServices"]
    default_action="Allow"
  }

  depends_on = [ azurerm_resource_group.state_bucket_rg ]
}

resource "azurerm_storage_container" "state_bucket_container" {
  name = var.state_bucket_name
  storage_account_name = azurerm_storage_account.state_bucket_sa.name
}

output "storage_account_name" {
  value = azurerm_storage_account.state_bucket_sa.name
}

output "container_name" {
  value = azurerm_storage_container.state_bucket_container.name
}

output "state_account_key" {
  value = azurerm_storage_account.state_bucket_sa.primary_access_key
}

output "state_connection_string" {
  value = azurerm_storage_account.state_bucket_sa.primary_connection_string
}
