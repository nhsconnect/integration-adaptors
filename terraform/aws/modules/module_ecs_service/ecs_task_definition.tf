resource "aws_ecs_task_definition" "ecs_task_definition" { 
  family = "${local.resource_prefix}-task_definition"
  
  task_role_arn = var.task_role_arn
  execution_role_arn = var.task_execution_role_arn
  container_definitions = jsonencode(
    [
      {
        name      = local.container_name
        image     = var.image_name

        essential = true
        portMappings = local.port_mappings
        logConfiguration = {
          logDriver = "awslogs"
          options = {
            awslogs-group           = aws_cloudwatch_log_group.ecs_service_cw_log_group.name
            awslogs-create-group    = "true"
            awslogs-region          = var.region
            awslogs-stream-prefix   = var.log_stream_prefix
            awslogs-datetime-format = var.logs_datetime_format
          }
        }
        environment = var.environment_variables
        secrets = var.secret_variables
      }
    ]
  )

  cpu = var.cpu_units
  memory = var.memory_units
  network_mode = var.network_mode
  requires_compatibilities = [var.launch_type]

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-task_definition"
  })
}