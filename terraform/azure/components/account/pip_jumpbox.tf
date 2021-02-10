resource "azurerm_public_ip" "account_jumpbox_pip" {
  name                 = "${local.resource_prefix}-jumpbox_ip"
  resource_group_name = azurerm_resource_group.account_resource_group.name
  location            = azurerm_resource_group.account_resource_group.location
  allocation_method    = "Dynamic"
}
