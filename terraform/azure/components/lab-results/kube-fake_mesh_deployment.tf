resource "kubernetes_deployment" "fake_mesh" {
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
    replicas = var.lab-results_replicas

    selector {
      match_labels = {
        name = "lab-results-fake-mesh"
      }
    } // selector

    template {
      metadata {
        labels = {
          project = var.project
          environment = var.environment
          component = var.component
          name = "lab-results-fake-mesh"
        }
      } //metadata

      spec {
        container {
          image = var.lab-results_fake_mesh_image
          name = "lab-results-fake-mesh"

          port {
            name = "container-port"
            container_port = var.lab-results_fake_mesh_container_port
            protocol = "TCP"
          } // port
        } // container
      } // spec
    } //template 
  } // spec
} // resource
