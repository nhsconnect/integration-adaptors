resource "azurerm_key_vault" "base-key-vault" {
  name                = "${local.resource_prefix}-keyvault"
  resource_group_name = var.account_resource_group
  location            = var.location
  tenant_id           = data.azurerm_client_config.current.tenant_id
  soft_delete_enabled         = false
  #soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  sku_name = "standard"

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
    ip_rules       = var.jumpbox_allowed_ips
  }
}

resource "azurerm_key_vault_access_policy" "terraform" {
    key_vault_id = azurerm_key_vault.base-key-vault.id
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "get",
      "create",
      "list",
      "update",
      "delete",
    ]

    secret_permissions = [
      "get",
      "set",
      "list",
      "delete",
    ]

    storage_permissions = [
      "get",
      "set",
      "list",
      "update",
      "delete",
    ]
}

# resource "azurerm_key_vault_access_policy" "console" {

# }

data "azurerm_client_config" "current" {}