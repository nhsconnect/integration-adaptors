resource "azurerm_subnet" "base_redis_subnet" {
  name = "${local.resource_prefix}-redis_subnet"
  resource_group_name = var.account_resource_group
  virtual_network_name = azurerm_virtual_network.base_vnet.name
  address_prefixes = [ var.base_redis_cidr ]
}
