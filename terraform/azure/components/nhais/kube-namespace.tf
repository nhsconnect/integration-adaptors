resource "kubernetes_namespace" "nhais" {
  metadata {
    name = local.resource_prefix

    labels = {
      Project = var.project
      Environment = var.environment
      Component = var.component
      Name = local.resource_prefix
    }
  }
}
# Note: Terraform creates Kube Namespace without problems, it has problems destroying it, you may need to remove namespace with kubectl if needed
# And remove it from tfstate afterwards
