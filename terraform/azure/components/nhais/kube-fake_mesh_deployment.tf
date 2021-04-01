resource "kubernetes_deployment" "fake_mesh" {
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
    replicas = var.nhais_replicas

    selector {
      match_labels = {
        name = "nhais-fake-mesh"
      }
    } // selector

    template {
      metadata {
        labels = {
          project = var.project
          environment = var.environment
          component = var.component
          name = "nhais-fake-mesh"
        }
      } //metadata

      spec {
        container {
          image = var.fake_mesh_image
          name = "nhais-fake-mesh"

          port {
            name = "container-port"
            container_port = "${var.fake_mesh_container_port}"
            protocol = "TCP"
          } // port
        } // container
      } // spec
    } //template 
  } // spec
} // resource
