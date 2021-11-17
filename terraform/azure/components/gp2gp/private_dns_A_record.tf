resource "azurerm_private_dns_a_record" "gp2gp" {
  name                = "gp2gp"
  zone_name           = data.terraform_remote_state.base.outputs.base_private_dns_zone
  resource_group_name = var.account_resource_group
  ttl                 = 30
  records             = [kubernetes_service.gp2gp.status[0].load_balancer[0].ingress[0].ip]
}

resource "azurerm_private_dns_a_record" "gpc-consumer" {
  name                = "gpc-consumer"
  zone_name           = data.terraform_remote_state.base.outputs.base_private_dns_zone
  resource_group_name = var.account_resource_group
  ttl                 = 30
  records             = [kubernetes_service.gpc-consumer.status[0].load_balancer[0].ingress[0].ip]
}