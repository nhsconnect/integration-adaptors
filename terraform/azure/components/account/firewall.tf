resource "azurerm_firewall" "account_firewall" {
  name = "${local.resource_prefix}-firewall"
  resource_group_name = azurerm_resource_group.account_resource_group.name
  location            = azurerm_resource_group.account_resource_group.location

  ip_configuration {
    name = "account_fw_ip_config"
    subnet_id = azurerm_subnet.account_firewall_subnet.id
    public_ip_address_id = azurerm_public_ip.account_firewall_pip.id
  }

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-firewall"
  })
}
