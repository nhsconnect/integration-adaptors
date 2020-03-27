# MHS inbound ECS task definition
resource "aws_ecs_task_definition" "mhs_inbound_task" {
  family = "${var.environment_id}-mhs-inbound"
  container_definitions = jsonencode(
  [
    {
      name = "mhs-inbound"
      image = "${var.ecr_address}/mhs/inbound:inbound-${var.build_id}"
      environment = [
        {
          name = "MHS_LOG_LEVEL"
          value = var.mhs_log_level
        },
        {
          name = "MHS_STATE_TABLE_NAME"
          value = aws_dynamodb_table.mhs_state_table.name
        },
        {
          name = "MHS_SYNC_ASYNC_STATE_TABLE_NAME"
          value = aws_dynamodb_table.mhs_sync_async_table.name
        },
        {
          name = "MHS_INBOUND_QUEUE_URL"
          value = var.inbound_queue_host
        }
      ]
      secrets = [
        {
          name = "MHS_SECRET_INBOUND_QUEUE_USERNAME"
          valueFrom = var.inbound_queue_username_arn
        },
        {
          name = "MHS_SECRET_INBOUND_QUEUE_PASSWORD"
          valueFrom = var.inbound_queue_password_arn
        },
        {
          name = "MHS_SECRET_PARTY_KEY"
          valueFrom = var.party_key_arn
        },
        {
          name = "MHS_SECRET_CLIENT_CERT"
          valueFrom = var.client_cert_arn
        },
        {
          name = "MHS_SECRET_CLIENT_KEY"
          valueFrom = var.client_key_arn
        },
        {
          name = "MHS_SECRET_CA_CERTS"
          valueFrom = var.ca_certs_arn
        }
      ]
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group = aws_cloudwatch_log_group.mhs_inbound_log_group.name
          awslogs-region = var.region
          awslogs-stream-prefix = var.build_id
          awslogs-datetime-format = "\\[%Y-%m-%dT%H:%M:%S\\.%fZ\\]"
        }
      }
      portMappings = [
        # Port 443 is the port for inbound requests from Spine
        {
          containerPort = 443
          hostPort = 443
          protocol = "tcp"
        },
        # Port 80 is the port for healthcheck requests from the MHS inbound load balancer
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
    Name = "${var.environment_id}-mhs-inbound-task"
    EnvironmentId = var.environment_id
  }
  task_role_arn = var.task_role_arn
  execution_role_arn = var.execution_role_arn
}