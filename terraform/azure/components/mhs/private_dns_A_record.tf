resource "azurerm_private_dns_a_record" "mhs-inbound" {
  name                = "mhs-inbound"
  zone_name           = data.terraform_remote_state.base.outputs.base_private_dns_zone
  resource_group_name = var.account_resource_group
  ttl                 = 30
  records             = [kubernetes_service.mhs-inbound.status[0].load_balancer[0].ingress[0].ip]
}

resource "azurerm_private_dns_a_record" "mhs-outbound" {
  name                = "mhs-outbound"
  zone_name           = data.terraform_remote_state.base.outputs.base_private_dns_zone
  resource_group_name = var.account_resource_group
  ttl                 = 30
  records             = [kubernetes_service.mhs-outbound.status[0].load_balancer[0].ingress[0].ip]
}

resource "azurerm_private_dns_a_record" "mhs-route" {
  name                = "mhs-route"
  zone_name           = data.terraform_remote_state.base.outputs.base_private_dns_zone
  resource_group_name = var.account_resource_group
  ttl                 = 30
  records             = [kubernetes_service.mhs-route.status[0].load_balancer[0].ingress[0].ip]
}