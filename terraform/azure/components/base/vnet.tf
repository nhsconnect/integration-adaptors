resource "azurerm_virtual_network" "base_vnet" {
  name                = "${local.resource_prefix}-vnet"
  resource_group_name = var.account_resource_group
  location            = var.location
  address_space       = var.ptl_connected ?  [ var.base_cidr, var.ptl_cidr ] : [var.base_cidr] # add option to add more cidrs

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-vnet"
  })
}

# Move to MHS

# data "azurerm_resource_group" "mhs_rg" {
#   name = "mhs-rg"
# }

# resource "azurerm_virtual_network_peering" "peering-base-to-mhs" {
#   name                      = "peering_base_to_mhs"
#   resource_group_name       = var.account_resource_group
#   virtual_network_name      = azurerm_virtual_network.nia_vnet.name
#   remote_virtual_network_id = data.azurerm_virtual_network.mhs_vnet.id
# }

# resource "azurerm_virtual_network_peering" "peering-mhs-to-base" {
#   name                      = "peering_mhs_to_base"
#   resource_group_name       = data.azurerm_resource_group.mhs_rg.name
#   virtual_network_name      = data.azurerm_virtual_network.mhs_vnet.name
#   remote_virtual_network_id = azurerm_virtual_network.nia_vnet.id
# }