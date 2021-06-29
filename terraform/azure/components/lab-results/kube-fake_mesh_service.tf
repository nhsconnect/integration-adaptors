resource "kubernetes_service" "fake_mesh" {
  count = var.lab-results_fake_mesh_in_use ? 1 : 0
  metadata {
    name = "lab-results-fake-mesh"
    namespace = kubernetes_namespace.lab-results.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "lab-results-fake-mesh"
    }
  }

  spec {
    port {
      name = var.lab-results_fake_mesh_application_port
      port = var.lab-results_fake_mesh_application_port
      target_port = var.lab-results_fake_mesh_container_port
    }

    selector = {
      name = "lab-results-fake-mesh"
    }
  }
}
