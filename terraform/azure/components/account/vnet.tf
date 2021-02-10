resource "azurerm_virtual_network" "account_vnet" {
  name                = "${local.resource_prefix}-vnet"
  resource_group_name = azurerm_resource_group.account_resource_group.name
  location            = azurerm_resource_group.account_resource_group.location
  address_space       = [ var.account_cidr ]

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-vnet"
  })
}
