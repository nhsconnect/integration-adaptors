resource "kubernetes_service" "fake_mesh" {
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

    annotations = {
      "service.beta.kubernetes.io/azure-load-balancer-internal" = true
      "service.beta.kubernetes.io/azure-load-balancer-resource-group" =  data.terraform_remote_state.account.outputs.resource_group_name
      "service.beta.kubernetes.io/azure-dns-label-name" = "${local.resource_prefix}-fake-mesh"
    }
  }

  spec {
    port {
      name = var.fake_mesh_application_port
      port = var.fake_mesh_application_port
      target_port = var.fake_mesh_container_port
    }

    type = "LoadBalancer"

    selector = {
      Component = "nhais"
      Environment = var.environment
    }
  }
}
