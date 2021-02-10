resource "azurerm_key_vault" "account-keyvault" {
  #name                = replace("${local.resource_prefix}-vault","_","-")
  name = "${var.project}-${var.environment}-vault"
  resource_group_name = azurerm_resource_group.account_resource_group.name
  location            = azurerm_resource_group.account_resource_group.location
  tenant_id           = data.azurerm_client_config.current.tenant_id
  #soft_delete_enabled         = true
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  sku_name = "standard"

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
    ip_rules       = var.jumpbox_allowed_ips
  }

  tags = merge(local.default_tags,{
    Name = "${var.project}-${var.environment}-vault"
  })
}

resource "azurerm_key_vault_access_policy" "terraform" {
    key_vault_id = azurerm_key_vault.account-keyvault.id
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

resource "azurerm_key_vault_access_policy" "additional" {
  count = length(var.additional_keyvault_tenants)
  key_vault_id = azurerm_key_vault.account-keyvault.id
  tenant_id = var.additional_keyvault_tenants[count.index].tenant_id
  object_id = var.additional_keyvault_tenants[count.index].object_id

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

data "azurerm_client_config" "current" {}