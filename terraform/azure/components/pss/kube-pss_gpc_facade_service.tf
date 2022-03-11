resource "kubernetes_service" "pss_gpc_facade" {
  metadata {
    name = "pss-gpc-facade"
    namespace = kubernetes_namespace.pss.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "pss-gpc-facade"
    }

    annotations = {
      "service.beta.kubernetes.io/azure-load-balancer-internal" = true
    }
  }

  spec {
    port {
      name = var.pss_application_port
      port = var.pss_application_port
      target_port = var.pss_gpc_api_facade_container_port
    }

    type = "LoadBalancer"

    selector = {
      name = "pss-gpc-facade"
    }
  }
}
