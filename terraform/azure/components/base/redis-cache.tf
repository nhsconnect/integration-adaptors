# NOTE: the Name used for Redis needs to be globally unique
resource "azurerm_redis_cache" "redis-cache" {
  name                = "${var.cluster_name}-cache"
  location            = azurerm_resource_group.mhs_adaptor.location
  resource_group_name = azurerm_resource_group.mhs_adaptor.name
  capacity            = 2
  family              = "P"
  sku_name            = "Premium" # required from allocating a subnet for redis
  enable_non_ssl_port = true
  minimum_tls_version = "1.2"
  subnet_id = azurerm_subnet.mhs_redis_subnet.id

  redis_configuration {
    enable_authentication = false
  }
}

output "redis_hostname" {
  value = azurerm_redis_cache.redis-cache.hostname
}

output "redis_ssl_port" {
  value = azurerm_redis_cache.redis-cache.ssl_port
}

output "redis_non_ssl_port" {
  value = azurerm_redis_cache.redis-cache.port
}

output "redis_key" {
  value = azurerm_redis_cache.redis-cache.primary_access_key
}

output "redis_connection_string" {
  value = azurerm_redis_cache.redis-cache.primary_connection_string
}