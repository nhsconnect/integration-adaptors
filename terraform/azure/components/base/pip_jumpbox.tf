resource "azurerm_public_ip" "base_jumpbox_pip" {
  name                 = "${local.resource_prefix}-jumpbox_ip"
  resource_group_name  = var.account_resource_group
  location             = var.location
  allocation_method    = "Dynamic"
}
