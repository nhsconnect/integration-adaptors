resource "aws_cloudwatch_log_group" "ecs_service_cw_log_group" {
  name = "/ecs/${local.resource_prefix}"

  retention_in_days = var.logs_retention
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-cw_log_group"
  })
}