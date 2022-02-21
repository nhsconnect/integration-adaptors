resource "azurerm_postgresql_virtual_network_rule" "testbox_network_rule" {
  name                                 = "${local.resource_prefix}-postgresql-vnet-rule"
  resource_group_name                  = var.account_resource_group
  server_name                          = azurerm_postgresql_server.postgres_server.name
  subnet_id                            = azurerm_subnet.base_testbox_subnet.id
  ignore_missing_vnet_service_endpoint = true
}

resource "azurerm_postgresql_virtual_network_rule" "aks_network_rule" {
  name                                 = "${local.resource_prefix}-postgresql-vnet-rule"
  resource_group_name                  = var.account_resource_group
  server_name                          = azurerm_postgresql_server.postgres_server.name
  subnet_id                            = azurerm_subnet.base_aks_subnet.id
  ignore_missing_vnet_service_endpoint = true
}