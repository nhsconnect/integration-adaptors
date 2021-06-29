resource "kubernetes_namespace" "lab-results" {
  metadata {
#    name = var.environment
    name = "${var.environment}-lab-results"

    labels = {
      project = var.project
      environment = var.environment
      component = var.component
      name = local.resource_prefix
    }
  }
}
# Note: Terraform creates Kube Namespace without problems, it has problems destroying it, you may need to remove namespace with kubectl if needed
# And remove it from tfstate afterwards
