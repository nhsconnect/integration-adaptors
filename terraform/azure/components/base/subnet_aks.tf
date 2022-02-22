resource "azurerm_subnet" "base_aks_subnet" {
  name = "${local.resource_prefix}-aks_subnet"
  resource_group_name  = var.account_resource_group
  virtual_network_name = azurerm_virtual_network.base_vnet.name
  enforce_private_link_endpoint_network_policies = true
  address_prefixes    = [ var.base_aks_cidr ]

  service_endpoints = [
    "Microsoft.AzureCosmosDB",
    "Microsoft.ContainerRegistry",
    "Microsoft.ServiceBus",
    "Microsoft.Storage",
    "Microsoft.Sql"
  ]
}

resource "azurerm_subnet_route_table_association" "base_aks_subnet_association" {
  subnet_id      = azurerm_subnet.base_aks_subnet.id
  route_table_id = azurerm_route_table.base_route_table.id
  depends_on = [
    azurerm_subnet.base_aks_subnet,
    azurerm_route_table.base_route_table,
  ]
}
