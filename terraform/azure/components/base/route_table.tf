resource "azurerm_route_table" "base_route_table" {
  name = "${local.resource_prefix}-route_table"
  resource_group_name = var.account_resource_group
  location            = var.location

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-route_table"
  })
}
