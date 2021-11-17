resource "azurerm_private_dns_zone" "private-dns" {
  name                = var.base_private_dns
  resource_group_name = var.account_resource_group
}

resource "azurerm_private_dns_zone_virtual_network_link" "virtual_network_link" {
  name                  = "${local.resource_prefix}-virtual_network_link"
  resource_group_name   = var.account_resource_group
  private_dns_zone_name = azurerm_private_dns_zone.private-dns.name
  virtual_network_id    = azurerm_virtual_network.base_vnet.id

  depends_on = [azurerm_private_dns_zone.private-dns]
}