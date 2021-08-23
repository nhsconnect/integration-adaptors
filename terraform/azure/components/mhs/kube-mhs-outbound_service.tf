resource "kubernetes_service" "mhs-outbound" {
  metadata {
    name = "mhs-outbound"
    namespace = kubernetes_namespace.mhs.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "mhs-outbound"
    }

    annotations = {
      "service.beta.kubernetes.io/azure-load-balancer-internal" = true
    }
  }

  spec {

    port {
      name = var.mhs_service_application_port
      port = var.mhs_service_application_port
      target_port = var.mhs_outbound_service_container_port
    }

    type = "LoadBalancer"

    selector = {
      name = "mhs-outbound"
    }
  }
}
