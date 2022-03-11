resource "kubernetes_service" "pss_mock_mhs" {
  metadata {
    name = "pss-mock-mhs"
    namespace = kubernetes_namespace.pss.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "pss-mock-mhs"
    }

    annotations = {
      "service.beta.kubernetes.io/azure-load-balancer-internal" = true
    }
  }

  spec {
    port {
      name = var.pss_application_port
      port = var.pss_application_port
      target_port = var.pss_mock_mhs_port
    }

    type = "LoadBalancer"

    selector = {
      name = "pss-mock-mhs"
    }
  }
}
