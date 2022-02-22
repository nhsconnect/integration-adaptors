resource "azurerm_subnet" "base_testbox_subnet" {
  name = "${local.resource_prefix}-jumpbox_subnet"
  resource_group_name  = data.terraform_remote_state.account.outputs.resource_group_name
  virtual_network_name = azurerm_virtual_network.base_vnet.name
  address_prefixes     = [ var.base_testbox_cidr ]
  enforce_private_link_endpoint_network_policies = true

  service_endpoints = [
    "Microsoft.AzureCosmosDB",
    "Microsoft.ContainerRegistry",
    "Microsoft.ServiceBus",
    "Microsoft.Storage",
    "Microsoft.Sql"
  ]
}

resource "azurerm_subnet_route_table_association" "base_testbox_subnet_association" {
  subnet_id      = azurerm_subnet.base_testbox_subnet.id
  route_table_id = azurerm_route_table.base_route_table.id
}
