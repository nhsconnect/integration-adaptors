resource "azurerm_private_dns_a_record" "pss_gp2gp_translator" {
  name                = "pss_gp2gp_translator"
  zone_name           = data.terraform_remote_state.base.outputs.base_private_dns_zone
  resource_group_name = var.account_resource_group
  ttl                 = 30
  records             = [kubernetes_service.pss_gp2gp_translator.status[0].load_balancer[0].ingress[0].ip]
}

resource "azurerm_private_dns_a_record" "pss_gpc_facade" {
  name                = "pss_gpc_facade"
  zone_name           = data.terraform_remote_state.base.outputs.base_private_dns_zone
  resource_group_name = var.account_resource_group
  ttl                 = 30
  records             = [kubernetes_service.pss_gpc_facade.status[0].load_balancer[0].ingress[0].ip]
}

resource "azurerm_private_dns_a_record" "pss_mhs_mock" {
  name                = "pss_mhs_mock"
  zone_name           = data.terraform_remote_state.base.outputs.base_private_dns_zone
  resource_group_name = var.account_resource_group
  ttl                 = 30
  records             = [kubernetes_service.pss_mock_mhs.status[0].load_balancer[0].ingress[0].ip]
}