resource "azurerm_network_security_rule" "base_jumpbox_ssh_rule" {
    name                        = "SSH"
    priority                    = 1001
    direction                   = "Inbound"
    access                      = "Allow"
    protocol                    = "Tcp"
    source_port_range           = "*"
    destination_port_range      = "22"
    source_address_prefixes     = var.jumpbox_allowed_ips
    destination_address_prefix  = "*"
    resource_group_name         = var.account_resource_group
    network_security_group_name = azurerm_network_security_group.base_jumpbox_sg.name

    depends_on = [
      azurerm_network_security_group.base_jumpbox_sg
    ]
}
