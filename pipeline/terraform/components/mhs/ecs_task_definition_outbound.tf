# MHS outbound ECS task definition
resource "aws_ecs_task_definition" "mhs_outbound_task" {
  family = "${var.environment_id}-mhs-outbound"
  container_definitions = jsonencode(
  [
    {
      name = "mhs-outbound"
      image = "${var.ecr_address}/mhs/outbound:outbound-${var.build_id}"
      environment = var.mhs_outbound_http_proxy == "" ? local.mhs_outbound_base_environment_vars : concat(local.mhs_outbound_base_environment_vars, [
        {
          name = "MHS_OUTBOUND_HTTP_PROXY"
          value = var.mhs_outbound_http_proxy
        },
        {
          name = "MHS_RESYNC_INITIAL_DELAY"
          value = var.mhs_resync_initial_delay
        }
      ])
      secrets = var.route_ca_certs_arn == "" ? local.mhs_outbound_base_secrets : concat(local.mhs_outbound_base_secrets, [
        {
          name = "MHS_SECRET_SPINE_ROUTE_LOOKUP_CA_CERTS",
          valueFrom = var.route_ca_certs_arn
        }
      ])
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group = aws_cloudwatch_log_group.mhs_outbound_log_group.name
          awslogs-region = var.region
          awslogs-stream-prefix = var.build_id
          awslogs-datetime-format = "\\[%Y-%m-%dT%H:%M:%S\\.%fZ\\]"
        }
      }
      portMappings = [
        {
          containerPort = 80
          hostPort = 80
          protocol = "tcp"
        }
      ]
    }
  ]
  )
  cpu = "512"
  memory = "1024"
  network_mode = "awsvpc"
  requires_compatibilities = [
    "FARGATE"
  ]
  tags = {
    Name = "${var.environment_id}-mhs-outbound-task"
    EnvironmentId = var.environment_id
  }
  task_role_arn = var.task_role_arn
  execution_role_arn = var.execution_role_arn
}