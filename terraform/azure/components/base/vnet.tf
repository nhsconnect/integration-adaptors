resource "azurerm_virtual_network" "base_vnet" {
  name                = "${local.resource_prefix}-vnet"
  resource_group_name = var.account_resource_group
  location            = var.location
  address_space       = var.ptl_connected ?  [ var.base_cidr, var.ptl_cidr ] : [ var.base_cidr ] # add option to add more cidrs

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-vnet"
  })
}
