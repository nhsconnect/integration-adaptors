resource "aws_ecs_cluster" "ecs_cluster" { 
  name = local.resource_prefix
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}"
  })

  setting {
    name = "containerInsights"
    value = var.container_insights
  }
}