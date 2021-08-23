resource "kubernetes_service" "gpc-consumer" {
  metadata {
    name = "gp2gp-gpc-consumer"
    namespace = kubernetes_namespace.gp2gp.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "gp2gp-gpc-consumer"
    }

    annotations = {
      "service.beta.kubernetes.io/azure-load-balancer-internal" = true
    }
  }

  spec {
    port {
      name = var.gpc-consumer_application_port
      port = var.gpc-consumer_application_port
      target_port = var.gpc-consumer_container_port
    }

    type = "LoadBalancer"
    
    selector = {
      name = "gp2gp-gpc-consumer"
    }
  }
}
