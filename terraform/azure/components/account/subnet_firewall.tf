resource "azurerm_subnet" "account_firewall_subnet" {
  name = "AzureFirewallSubnet"
  resource_group_name = azurerm_resource_group.account_resource_group.name
  virtual_network_name = azurerm_virtual_network.account_vnet.name
  address_prefixes    = [var.account_firewall_cidr]
}
