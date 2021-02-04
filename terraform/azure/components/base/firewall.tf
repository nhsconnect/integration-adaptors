resource "azurerm_firewall" "base_firewall" {
  name = "${local.resource_prefix}-firewall"
  resource_group_name = var.account_resource_group
  location            = var.location

  ip_configuration {
    name = "base_fw_ip_config"
    subnet_id = azurerm_subnet.base_firewall_subnet.id
    public_ip_address_id = azurerm_public_ip.base_firewall_pip.id
  }

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-firewall"
  })
}
