resource "azurerm_subnet" "account_jumpbox_subnet" {
  name = "${local.resource_prefix}-jumpbox_subnet"
  resource_group_name = azurerm_resource_group.account_resource_group.name
  virtual_network_name = azurerm_virtual_network.account_vnet.name
  address_prefixes    = [ var.account_jumpbox_cidr ]
  enforce_private_link_endpoint_network_policies = true

  service_endpoints = [
    "Microsoft.AzureCosmosDB",
    "Microsoft.ContainerRegistry",
    "Microsoft.ServiceBus",
    "Microsoft.Storage",
    "Microsoft.Sql"
  ]
}
