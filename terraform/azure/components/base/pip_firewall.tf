resource "azurerm_public_ip" "base_firewall_pip" {
  name = "${local.resource_prefix}-firewall_ip"
  resource_group_name = var.account_resource_group
  location            = var.location
  allocation_method = "Static"
  sku = "Standard"
}
