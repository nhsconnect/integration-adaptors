resource "azurerm_network_security_group" "base_jumpbox_sg" {
  name                = "${local.resource_prefix}-jumpbox_sg"
  resource_group_name = var.account_resource_group
  location            = var.location
}

resource "azurerm_network_interface_security_group_association" "base_jumpbox_sg_association" {
  network_interface_id      = azurerm_network_interface.base_jumpbox_nic.id
  network_security_group_id = azurerm_network_security_group.base_jumpbox_sg.id
  depends_on = [
    azurerm_network_security_group.base_jumpbox_sg
  ]
}
