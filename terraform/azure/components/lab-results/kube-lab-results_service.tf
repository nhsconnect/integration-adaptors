resource "kubernetes_service" "lab-results" {
  metadata {
    name = "lab-results"
    namespace = kubernetes_namespace.lab-results.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "lab-results"
    }

    annotations = {
      "service.beta.kubernetes.io/azure-load-balancer-internal" = true
    }
  }

  spec {
    port {
      name = var.lab-results_application_port
      port = var.lab-results_application_port
      target_port = var.lab-results_container_port
    }

    type = "LoadBalancer"
    load_balancer_ip = var.lab-results_lb_ip == "" ? null : var.lab-results_lb_ip

    selector = {
      name = "lab-results"
    }
  }
}
