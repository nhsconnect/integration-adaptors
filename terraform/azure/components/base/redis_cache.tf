# NOTE: the Name used for Redis needs to be globally unique
resource "azurerm_redis_cache" "redis-cache" {
  name                = "${local.resource_prefix}-redis"
  location            = var.location
  resource_group_name = var.account_resource_group
  capacity            = 2
  family              = "P"
  sku_name            = "Premium" # required from allocating a subnet for redis
  enable_non_ssl_port = true
  minimum_tls_version = "1.2"
  subnet_id = azurerm_subnet.base_redis_subnet.id

  redis_configuration {
    enable_authentication = false
  }

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-redis"
  })
}

