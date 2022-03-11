resource "kubernetes_service" "pss_gp2gp_translator" {
  metadata {
    name = "pss-gp2gp-translator"
    namespace = kubernetes_namespace.pss.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "pss-gp2gp-translator"
    }

    annotations = {
      "service.beta.kubernetes.io/azure-load-balancer-internal" = true
    }
  }

  spec {
    port {
      name = var.pss_application_port
      port = var.pss_application_port
      target_port = var.pss_gp2gp_translator_container_port
    }

    type = "LoadBalancer"

    selector = {
      name = "pss-gp2gp-translator"
    }
  }
}
