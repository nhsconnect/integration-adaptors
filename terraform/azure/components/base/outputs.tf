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
  sensitive = true
}

# Mongo credentials calculated from connection string, some adaptors require this

output mongodb_username {
  value = split(":",split("@",replace(azurerm_cosmosdb_account.mongodb.connection_strings[0],"mongodb://",""))[0])[0]
}

output mongodb_password {
  value = split(":",split("@",replace(azurerm_cosmosdb_account.mongodb.connection_strings[0],"mongodb://",""))[0])[1]
  sensitive = true
}

output mongodb_port {
  value = split(":",split("/",split("@",azurerm_cosmosdb_account.mongodb.connection_strings[0])[1])[0])[1]
}

output "mongodb_hostname" {
  value = split(":",split("/",split("@",azurerm_cosmosdb_account.mongodb.connection_strings[0])[1])[0])[0]
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

# testbox outputs

output "base_testbox_ip" {
  description = "testbox VM IP"
  value       = azurerm_linux_virtual_machine.base_testbox.private_ip_address
}

output "base_testbox_username" {
  description = "Jumpbox VM username"
  value       = var.jumpbox_user
}

output "base_testbox_connect" {
  description = "Command for connecting to jumpbox"
  value = "ssh -i ${var.jumpbox_private_key_location} -o \"ProxyCommand ssh -i ${var.jumpbox_private_key_location} -W %h:%p ${var.jumpbox_user}@${data.terraform_remote_state.account.outputs.jumpbox_ip}\" ${var.jumpbox_user}@${azurerm_linux_virtual_machine.base_testbox.private_ip_address}"
}

# VNET

output "vnet_id" {
  value = azurerm_virtual_network.base_vnet.id
}

output "vnet_name" {
  value = azurerm_virtual_network.base_vnet.name
}

# Servicebus

output "base_servicebus_namespace" {
  value = azurerm_servicebus_namespace.base_servicebus_namespace.name
}

# AKS

output "base_aks_id" {
    value = azurerm_kubernetes_cluster.base_aks.id
}

output "base_aks_client_key" {
  value = azurerm_kubernetes_cluster.base_aks.kube_config.0.client_key
}

output "base_aks_client_certificate" {
  value = azurerm_kubernetes_cluster.base_aks.kube_config.0.client_certificate
}

output "base_aks_cluster_ca_certificate" {
  value = azurerm_kubernetes_cluster.base_aks.kube_config.0.cluster_ca_certificate
}

output "base_aks_kube_config" {
  value = azurerm_kubernetes_cluster.base_aks.kube_config_raw
}

output "base_aks_host" {
  value = azurerm_kubernetes_cluster.base_aks.kube_config.0.host
}

output "base_aks_configure" {
  value = <<CONFIGURE

Run the following commands to configure kubernetes client:

$ terraform output kube_config > ~/.kube/aksconfig
$ export KUBECONFIG=~/.kube/aksconfig

Test configuration using kubectl

$ kubectl get nodes
CONFIGURE
}
