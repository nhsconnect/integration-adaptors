# NOTE: the Name used for Redis needs to be globally unique
resource "azurerm_redis_cache" "redis-cache" {
  name                = "${var.cluster_name}-cache"
  location            = azurerm_resource_group.mhs_adaptor.location
  resource_group_name = azurerm_resource_group.mhs_adaptor.name
  capacity            = 2
  family              = "C"
  sku_name            = "Standard"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"

  redis_configuration {}
}