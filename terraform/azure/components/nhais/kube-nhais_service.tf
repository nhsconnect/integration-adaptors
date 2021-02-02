
# apiVersion: v1
# kind: Service
# metadata:
#   name: nhais
#   labels:
#     app: nhais
# spec:
#   ports:
#   - port: 80
#     protocol: TCP
#     targetPort: 8080
#   selector:
#     app: nhais



resource "kubernetes_service" "nhais" {
  metadata {
    name = "${local.resource_prefix}-service"
    namespace = kubernetes_namespace.nhais.metadata.0.name

    labels = {
      Project = var.project
      Environment = var.environment
      Component = var.component
      Name = "${local.resource_prefix}-service"
    }
  }

  spec {
    port {
      port = var.nhais_application_port
      target_port = var.nhais_container_port
    }

    selector = {
      Component = "nhais"
      Environment = var.environment
    }

  }
}