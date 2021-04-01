resource "kubernetes_service" "fake_mesh" {
  count = var.fake_mesh_in_use ? 1 : 0
  metadata {
    name = "nhais-fake-mesh"
    namespace = kubernetes_namespace.nhais.metadata.0.name

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = "nhais-fake-mesh"
    }
  }

  spec {
    port {
      name = var.fake_mesh_application_port
      port = var.fake_mesh_application_port
      target_port = var.fake_mesh_container_port
    }

    selector = {
      name = "nhais-fake-mesh"
    }
  }
}
