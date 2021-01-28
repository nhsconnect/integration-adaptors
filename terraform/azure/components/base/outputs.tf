## General outputs


## Mongo outputs
output "mongodb_endpoint" {
  value = azurerm_cosmosdb_account.mongodb.endpoint
}

output "mongodb_write_endpoints" {
  value = azurerm_cosmosdb_account.mongodb.write_endpoints
}

output "mongodb_read_endpoints" {
  value = azurerm_cosmosdb_account.mongodb.read_endpoints
}

output "mongodb_connection_string" {
  value = azurerm_cosmosdb_account.mongodb.connection_strings
}

# redis outputs

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

# jumpbox outputs

output "base_jumpbox_ip" {
  description = "Jumpbox VM IP"
  value       = azurerm_linux_virtual_machine.base_jumpbox.public_ip_address
}

output "base_jumpbox_username" {
  description = "Jumpbox VM username"
  value       = var.jumpbox_user
}

output "base_jumpbox_connect" {
  description = "Command for connecting to jumpbox"
  value = "ssh ${var.jumpbox_user}@${azurerm_linux_virtual_machine.base_jumpbox.public_ip_address} -i ~/.ssh/azure_mhs_jumpbox"
}
