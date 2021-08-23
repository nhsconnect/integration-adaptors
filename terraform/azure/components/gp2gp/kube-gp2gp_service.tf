resource "kubernetes_service" "gp2gp" {
  metadata {
    name = "gp2gp"
    namespace = kubernetes_namespace.gp2gp.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "gp2gp"
    }

    annotations = {
      "service.beta.kubernetes.io/azure-load-balancer-internal" = true
    }
  }

  spec {
    port {
      name = var.gp2gp_application_port
      port = var.gp2gp_application_port
      target_port = var.gp2gp_container_port
    }

    type = "LoadBalancer"

    selector = {
      name = "gp2gp"
    }
  }
}
