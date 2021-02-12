resource "kubernetes_service" "nhais" {
  metadata {
    name = local.resource_prefix
    namespace = kubernetes_namespace.nhais.metadata.0.name

    labels = {
      Project = var.project
      Environment = var.environment
      Component = var.component
      Name = local.resource_prefix
    }

    annotations = {
      "service.beta.kubernetes.io/azure-load-balancer-internal" = true
      "service.beta.kubernetes.io/azure-load-balancer-resource-group" = data.terraform_remote_state.account.outputs.resource_group_name
      "service.beta.kubernetes.io/azure-dns-label-name" = local.resource_prefix
    }
  }

  spec {
    port {
      name = var.nhais_application_port
      port = var.nhais_application_port
      target_port = var.nhais_container_port
    }

    type = "LoadBalancer"
    load_balancer_ip = var.nhais_lb_ip == "" ? null : var.nhais_lb_ip

    selector = {
      Component = "nhais"
      Environment = var.environment
    }
  }
}
