resource "azurerm_virtual_network_peering" "base_to_account" {
  name                      = "${local.resource_prefix}-peering_to_account"
  resource_group_name       = data.terraform_remote_state.account.outputs.resource_group_name
  virtual_network_name      = azurerm_virtual_network.base_vnet.name
  remote_virtual_network_id = data.terraform_remote_state.account.outputs.vnet_id
}

resource "azurerm_virtual_network_peering" "account_to_base" {
  name                      = "${local.resource_prefix}-peering_from_account"
  resource_group_name       = data.terraform_remote_state.account.outputs.resource_group_name
  virtual_network_name      = data.terraform_remote_state.account.outputs.vnet_name
  remote_virtual_network_id = azurerm_virtual_network.base_vnet.id
}
