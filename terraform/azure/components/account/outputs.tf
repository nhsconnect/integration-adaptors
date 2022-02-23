output "resource_group_name" {
  value = azurerm_resource_group.account_resource_group.name
}

output "resource_group_location" {
  value = azurerm_resource_group.account_resource_group.location
}

output "storage_account_name" {
  value = azurerm_storage_account.account_bucket_sa.name
}

output "storage_account_key" {
  value = azurerm_storage_account.account_bucket_sa.primary_access_key
}

output "storage_account_connection_string" {
  value = azurerm_storage_account.account_bucket_sa.primary_connection_string
}

output "jumpbox_ip" {
  description = "Jumpbox VM IP"
  value       = azurerm_linux_virtual_machine.account_jumpbox.public_ip_address
}

output "jumpbox_username" {
  description = "Jumpbox VM username"
  value       = var.jumpbox_user
}

output "jumpbox_connect" {
  description = "Command for connecting to jumpbox"
  value = "ssh -i ${var.jumpbox_private_key_location} ${var.jumpbox_user}@${azurerm_linux_virtual_machine.account_jumpbox.public_ip_address}"
}

output "vnet_id" {
  value = azurerm_virtual_network.account_vnet.id
}

output "vnet_name" {
  value = azurerm_virtual_network.account_vnet.name
}

output "fw_private_ip_address" {
  value = azurerm_firewall.account_firewall.ip_configuration[0].private_ip_address
}

output "jumpbox_subnet_id" {
  value = azurerm_subnet.account_jumpbox_subnet.id
}
