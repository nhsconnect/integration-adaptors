resource "azurerm_private_dns_a_record" "postgres" {
  name                = "postgres"
  zone_name           = azurerm_private_dns_zone.private-dns.name
  resource_group_name = var.account_resource_group
  ttl                 = 30
  records             = [azurerm_private_endpoint.testbox-to-postgres-ep.private_service_connection[0].private_ip_address,azurerm_private_endpoint.aks-to-postgres-ep.private_service_connection[0].private_ip_address,azurerm_private_endpoint.jumpbox-to-postgres-ep.private_service_connection[0].private_ip_address]
}