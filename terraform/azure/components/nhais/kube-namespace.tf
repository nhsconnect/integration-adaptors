resource "kubernetes_namespace" "nhais" {
  metadata {
    name = "${local.resource_prefix}-namespace"

    labels = {
      Project = var.project
      Environment = var.environment
      Component = var.component
      Name = "${local.resource_prefix}-namespace"
    }
  }
}