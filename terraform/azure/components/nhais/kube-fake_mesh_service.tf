resource "kubernetes_service" "fake_mesh" {
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
    }
  }

  spec {
    port {
      port = var.fake_mesh_application_port
      target_port = var.fake_mesh_container_port
    }

    type = "LoadBalancer"
    load_balancer_ip = var.fake_mesh_lb_ip

    selector = {
      Component = "nhais"
      Environment = var.environment
    }
  }
}

output fake_mesh_ingress {
  value = kubernetes_service.fake_mesh.status[0].load_balancer[0].ingress
}
