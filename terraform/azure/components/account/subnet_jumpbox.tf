resource "azurerm_subnet" "account_jumpbox_subnet" {
  name = "${local.resource_prefix}-jumpbox_subnet"
  resource_group_name = azurerm_resource_group.account_resource_group.name
  virtual_network_name = azurerm_virtual_network.account_vnet.name
  address_prefixes    = [ var.account_jumpbox_cidr ]

  service_endpoints = [
    "Microsoft.AzureCosmosDB",
    "Microsoft.ContainerRegistry",
    "Microsoft.ServiceBus",
    "Microsoft.Storage"
  ]
}

# resource "azurerm_subnet_route_table_association" "base_jumpbox_subnet_association" {
#   subnet_id      = azurerm_subnet.base_jumpbox_subnet.id
#   route_table_id = azurerm_route_table.base_route_table.id
# }
