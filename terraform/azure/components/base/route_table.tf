resource "azurerm_route_table" "base_route_table" {
  name = "${local.resource_prefix}-route_table"
  resource_group_name = var.account_resource_group
  location            = var.location

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-route_table"
  })
}

resource "azurerm_route_table" "ptl_route_table" {
  name = "${local.resource_prefix}-ptl_route_table"
  count = var.ptl_connected ? 1 : 0
  resource_group_name = var.account_resource_group
  location            = var.location
  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-ptl_route_table"
  })
}



# resource "azurerm_route_table" "mhs_aks_route_table" {
#   name = "mhs_aks_route_table"
#   resource_group_name = azurerm_resource_group.mhs_adaptor.name
#   location            = azurerm_resource_group.mhs_adaptor.location
# }

# resource "azurerm_route" "mhs_aks_route" {
#   name = "mhs_aks_route_default"
#   resource_group_name = azurerm_resource_group.mhs_adaptor.name
#   route_table_name    = azurerm_route_table.mhs_aks_route_table.name
#   address_prefix       = "0.0.0.0/0"
#   next_hop_type       = "VirtualAppliance"
#   next_hop_in_ip_address = azurerm_firewall.mhs_firewall.ip_configuration[0].private_ip_address
# }

# resource "azurerm_route" "mhs_aks_route_to_N3" {
#   count = length(var.N3_prefixes)
#   name = "mhs_aks_route_to_N3_${count.index}"
#   resource_group_name    = azurerm_resource_group.mhs_adaptor.name
#   route_table_name       = azurerm_route_table.mhs_aks_route_table.name
#   address_prefix         = var.N3_prefixes[count.index]
#   next_hop_type          = "VirtualAppliance"
#   next_hop_in_ip_address = var.N3_next_hop
# }

# resource "azurerm_subnet_route_table_association" "mhs_aks_subnet_association" {
#   subnet_id      = azurerm_subnet.mhs_aks_subnet.id
#   route_table_id = azurerm_route_table.mhs_aks_route_table.id
# }

# resource "azurerm_subnet_route_table_association" "mhs_jumpbox_subnet_association" {
#   subnet_id      = azurerm_subnet.mhs_jumpbox_subnet.id
#   route_table_id = azurerm_route_table.mhs_aks_route_table.id
# }