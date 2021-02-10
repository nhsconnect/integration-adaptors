resource "azurerm_public_ip" "account_firewall_pip" {
  name = "${local.resource_prefix}-firewall_ip"
  resource_group_name = azurerm_resource_group.account_resource_group.name
  location            = azurerm_resource_group.account_resource_group.location
  allocation_method = "Static"
  sku = "Standard"
}
