# Container configuration for nginx container

locals {
  nginx_image_name = "${var.account_id}.dkr.ecr.${var.region}.amazonaws.com/111:${var.OneOneOne_build_id}"
  nginx_container_name = "${local.resource_prefix}-nginx_container"

  application_mapping = [
    {
      containerPort = var.container_port
      hostPort = var.container_port
      protocol = var.container_protocol
    }
  ]

  healthcheck_mapping = local.healthcheck_port == var.container_healthcheck_port ? [] : [
    {
      containerPort = var.container_healthcheck_port
      hostPort = var.container_healthcheck_port
      protocol = var.container_protocol
    }
  ]

  port_mappings = concat(local.application_mapping,local.healthcheck_mapping)


  nginx_container_config = jsonencode(
    [
      {
        name      = local.nginx_container_name
        image     = local.nginx_image_name

        essential = true
        portMappings = local.port_mappings
        # logConfiguration = {
        #   logDriver = "awslogs"
        #   options = {
        #     awslogs-group           = aws_cloudwatch_log_group.ecs_service_cw_log_group.name
        #     awslogs-create-group    = "true"
        #     awslogs-region          = var.region
        #     awslogs-stream-prefix   = var.log_stream_prefix
        #     awslogs-datetime-format = var.logs_datetime_format
        #   }
        # }
        # environment = var.environment_variables
        # secrets = var.secret_variables
      }
    ]
  )

}