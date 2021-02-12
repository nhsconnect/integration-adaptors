resource "kubernetes_deployment" "fake_mesh" {
  count = var.fake_mesh_in_use ? 1 : 0
  metadata {
    name = "${local.resource_prefix}-fake-mesh"
    namespace = kubernetes_namespace.nhais.metadata.0.name

    labels = {
      Project = var.project
      Environment = var.environment
      Component = var.component
      Name = "${local.resource_prefix}-fake-mesh"
    }
  }

  spec {
    replicas = var.nhais_replicas

    selector {
      match_labels = {
        Component = "nhais"
        Environment = var.environment
      }
    } // selector

    template {
      metadata {
        labels = {
          Project = var.project
          Environment = var.environment
          Component = var.component
          Name = "${local.resource_prefix}-fake-mesh"
        }
      } //metadata

      spec {
        container {
          image = var.fake_mesh_image
          name = "${local.resource_prefix}-fake-mesh"

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
