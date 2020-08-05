# Container configuration for nginx container

locals {
  nginx_image_name = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/111-nginx:${var.OneOneOne_build_id}"
  nginx_container_name = "${local.resource_prefix}-nginx_container"

  application_mapping = [
    {
      containerPort = "443"
      hostPort = "443"
      protocol = "TCP"
    }
  ]

  # healthcheck_mapping = local.healthcheck_port == var.container_healthcheck_port ? [] : [
  #   {
  #     containerPort = var.container_healthcheck_port
  #     hostPort = var.container_healthcheck_port
  #     protocol = var.container_protocol
  #   }
  # ]

  # port_mappings = concat(local.application_mapping,local.healthcheck_mapping)

  nginx_container_config = [
    {
      name      = local.nginx_container_name
      image     = local.nginx_image_name

      essential = false
      # portMappings = local.application_mapping
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group           = aws_cloudwatch_log_group.ecs_service_cw_log_group.name
          awslogs-create-group    = "true"
          awslogs-region          = var.region
          awslogs-stream-prefix   = var.OneOneOne_build_id
          awslogs-datetime-format = "%Y-%m-%d %H:%M:%S%L"
        }
      }
        # environment = var.environment_variables
        # secrets = var.secret_variables
    }
  ]
}

# CW log  group

resource "aws_cloudwatch_log_group" "ecs_service_cw_log_group" {
  name = "/ecs/${local.resource_prefix}"

  retention_in_days = "14"
  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-cw_log_group"
  })
}