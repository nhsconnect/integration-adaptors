resource "azurerm_network_security_group" "account_jumpbox_sg" {
  name                = "${local.resource_prefix}-jumpbox_sg"
  resource_group_name = azurerm_resource_group.account_resource_group.name
  location            = azurerm_resource_group.account_resource_group.location
}

resource "azurerm_network_interface_security_group_association" "account_jumpbox_sg_association" {
  network_interface_id      = azurerm_network_interface.account_jumpbox_nic.id
  network_security_group_id = azurerm_network_security_group.account_jumpbox_sg.id
  depends_on = [
    azurerm_network_security_group.account_jumpbox_sg
  ]
}
