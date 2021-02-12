resource "azurerm_servicebus_namespace" "base_servicebus_namespace" {
  name                = "${local.resource_prefix}-service-bus"
  location            = var.location
  resource_group_name = var.account_resource_group
  capacity            = var.servicebus_capacity
  sku                 = var.servicebus_sku

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-service-bus"
  })
}
