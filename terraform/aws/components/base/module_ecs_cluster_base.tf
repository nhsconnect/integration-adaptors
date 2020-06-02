module "base_ecs_cluster" {
  source = "../../modules/module_ecs_cluster"
  default_tags    = local.default_tags
  resource_prefix = local.resource_prefix
  module_instance = "ecs_cluster"
  container_insights = var.cluster_container_insights
}
