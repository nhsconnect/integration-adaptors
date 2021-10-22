resource "azurerm_private_dns_a_record" "lab-results" {
  name                = "lab-results"
  zone_name           = data.terraform_remote_state.base.outputs.base_private_dns_zone
  resource_group_name = var.account_resource_group
  ttl                 = 30
  records             = [kubernetes_service.lab-results.status[0].load_balancer[0].ingress[0].ip]
}
