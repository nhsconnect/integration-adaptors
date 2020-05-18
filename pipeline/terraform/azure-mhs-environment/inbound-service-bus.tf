resource "azurerm_servicebus_namespace" "mhsinbound" {
  name                = "${var.cluster_name}-service-bus"
  location            = azurerm_resource_group.mhs_adaptor.location
  resource_group_name = azurerm_resource_group.mhs_adaptor.name
  sku                 = "Standard"

  tags = {
    source = "terraform"
  }
}

resource "azurerm_servicebus_queue" "asb_inbound_queue" {
  name                = "${var.cluster_name}-servicebus-queue"
  resource_group_name = azurerm_resource_group.mhs_adaptor.name
  namespace_name      = azurerm_servicebus_namespace.mhsinbound.name

  enable_partitioning = true
}