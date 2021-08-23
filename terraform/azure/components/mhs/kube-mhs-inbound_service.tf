resource "kubernetes_service" "mhs-inbound" {
  metadata {
    name = "mhs-inbound"
    namespace = kubernetes_namespace.mhs.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "mhs-inbound"
    }

    annotations = {
      "service.beta.kubernetes.io/azure-load-balancer-internal" = true
    }
  }

  spec {
    port {
      name = var.mhs_inbound_service_container_port
      port = var.mhs_inbound_service_container_port
      target_port = var.mhs_inbound_service_container_port
    }

    type = "LoadBalancer"

    selector = {
      name = "mhs-inbound"
    }
  }
}
