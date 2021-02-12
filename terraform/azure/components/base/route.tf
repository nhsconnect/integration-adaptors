resource "azurerm_route" "base_default_route" {
  name = "${local.resource_prefix}-default_route"
  resource_group_name = var.account_resource_group
  route_table_name    = azurerm_route_table.base_route_table.name
  address_prefix       = "0.0.0.0/0"
  next_hop_type       = "VirtualAppliance"
  next_hop_in_ip_address = data.terraform_remote_state.account.outputs.fw_private_ip_address
}
