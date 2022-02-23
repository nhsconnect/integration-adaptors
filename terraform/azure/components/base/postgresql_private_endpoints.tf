resource "azurerm_private_endpoint" "testbox-to-postgres-ep" {
  name                = "${local.resource_prefix}-testbox-postgres-endpoint"
  location            = var.location
  resource_group_name = var.account_resource_group
  subnet_id           = azurerm_subnet.base_testbox_subnet.id

  private_service_connection {
    name                           = "testbox-to-postgres"
    private_connection_resource_id = azurerm_postgresql_server.postgres_server.id
    subresource_names              = ["postgresqlServer"]
    is_manual_connection           = false
  }
}

resource "azurerm_private_endpoint" "aks-to-postgres-ep" {
  name                = "${local.resource_prefix}-aks-postgres-endpoint"
  location            = var.location
  resource_group_name = var.account_resource_group
  subnet_id           = azurerm_subnet.base_aks_subnet.id

  private_service_connection {
    name                           = "aks-to-postgres"
    private_connection_resource_id = azurerm_postgresql_server.postgres_server.id
    subresource_names              = ["postgresqlServer"]
    is_manual_connection           = false
  }
}

resource "azurerm_private_endpoint" "jumpbox-to-postgres-ep" {
  name                = "${local.resource_prefix}-jumpbox-postgres-endpoint"
  location            = var.location
  resource_group_name = var.account_resource_group
  subnet_id           = data.terraform_remote_state.account.outputs.jumpbox_subnet_id

  private_service_connection {
    name                           = "jumpbox-to-postgres"
    private_connection_resource_id = azurerm_postgresql_server.postgres_server.id
    subresource_names              = ["postgresqlServer"]
    is_manual_connection           = false
  }
}