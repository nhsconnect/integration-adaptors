resource "azurerm_subnet" "base_firewall_subnet" {
  #name = "${local.resource_prefix}-firewall_subnet"
  name = "AzureFirewallSubnet"
  resource_group_name  = var.account_resource_group
  virtual_network_name = azurerm_virtual_network.base_vnet.name
  address_prefixes    = [var.base_firewall_cidr]
}