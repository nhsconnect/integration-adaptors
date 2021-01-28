resource "azurerm_route" "base_default_route" {
  name = "${local.resource_prefix}-default_route"
  resource_group_name = var.account_resource_group
  route_table_name    = azurerm_route_table.base_route_table.name
  address_prefix       = "0.0.0.0/0"
  next_hop_type       = "VirtualAppliance"
  next_hop_in_ip_address = azurerm_firewall.base_firewall.ip_configuration[0].private_ip_address
}

# resource "azurerm_route" "mhs_aks_route_to_N3" {
#   count = length(var.N3_prefixes)
#   name = "mhs_aks_route_to_N3_${count.index}"
#   resource_group_name    = var.account_resource_group
#   route_table_name       = azurerm_route_table.base_route_table.name
#   address_prefix         = var.N3_prefixes[count.index]
#   next_hop_type          = "VirtualAppliance"
#   next_hop_in_ip_address = var.N3_next_hop
# }