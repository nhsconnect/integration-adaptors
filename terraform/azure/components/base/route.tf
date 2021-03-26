resource "azurerm_route" "base_default_route" {
  name = "${local.resource_prefix}-default_route"
  resource_group_name = var.account_resource_group
  route_table_name    = azurerm_route_table.base_route_table.name
  address_prefix       = "0.0.0.0/0"
  next_hop_type       = "VirtualAppliance"
  next_hop_in_ip_address = data.terraform_remote_state.account.outputs.fw_private_ip_address
}

resource "azurerm_route" "ptl_hscn_route" {
  name = "${local.resource_prefix}-ptl_hscn_route_${count.index}"
  count = var.ptl_connected ? length(var.base_ptl_prefixes) : 0
  resource_group_name    = var.account_resource_group
  route_table_name       = azurerm_route_table.base_route_table.name
  address_prefix         = var.base_ptl_prefixes[count.index]
  next_hop_type          = "VirtualAppliance"
  next_hop_in_ip_address = var.base_ptl_next_hop
}
