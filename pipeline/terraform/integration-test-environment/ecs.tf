resource "aws_ecs_cluster" "mhs_cluster" {
  name = "${var.build_id}-mhs-cluster"

  tags = {
    Name    = "${var.build_id}-mhs-cluster"
    BuildId = var.build_id
  }
}

resource "aws_ecs_task_definition" "mhs_outbound_task" {
  family = "${var.build_id}-mhs-outbound"
  container_definitions = jsonencode(
    [
      {
        name  = "mhs-outbound"
        image = "${var.ecr_address}/mhs/outbound:${var.build_id}"
        environment = [
          {
            name  = "MHS_LOG_LEVEL"
            value = var.mhs_log_level
          },
          {
            name  = "MHS_STATE_TABLE_NAME"
            value = var.mhs_state_table_name
          }
        ]
        essential = true
        logConfiguration = {
          logDriver = "awslogs"
          options = {
            awslogs-group         = "/ecs/${var.build_id}-mhs-outbound"
            awslogs-region        = var.region
            awslogs-stream-prefix = var.build_id
          }
        }
        portMappings = [
          {
            containerPort = 80
            hostPort      = 80
            protocol      = "tcp"
          }
        ]
      }
    ]
  )
  cpu          = "512"
  memory       = "1024"
  network_mode = "awsvpc"
  requires_compatibilities = [
    "FARGATE"
  ]
  tags = {
    Name    = "${var.build_id}-mhs-outbound-task"
    BuildId = var.build_id
  }
  task_role_arn = var.task_role_arn
  execution_role_arn = var.execution_role_arn
}

resource "aws_ecs_task_definition" "mhs_inbound_task" {
  family = "${var.build_id}-mhs-inbound"
  container_definitions = jsonencode(
    [
      {
        name  = "mhs-inbound"
        image = "${var.ecr_address}/mhs/inbound:${var.build_id}"
        environment = [
          {
            name  = "MHS_LOG_LEVEL"
            value = var.mhs_log_level
          },
          {
            name  = "MHS_STATE_TABLE_NAME"
            value = var.mhs_state_table_name
          },
          {
            name  = "MHS_SYNC_ASYNC_STATE_TABLE_NAME"
            value = var.mhs_sync_async_table_name
          },
          {
            name  = "MHS_INBOUND_QUEUE_HOST"
            value = var.inbound_queue_host
          }
        ]
        secrets = [
          {
            name      = "MHS_INBOUND_QUEUE_USERNAME"
            valueFrom = var.inbound_queue_username_arn
          },
          {
            name      = "MHS_INBOUND_QUEUE_PASSWORD"
            valueFrom = var.inbound_queue_password_arn
          }
        ]
        essential = true
        logConfiguration = {
          logDriver = "awslogs"
          options = {
            awslogs-group         = "/ecs/${var.build_id}-mhs-inbound"
            awslogs-region        = var.region
            awslogs-stream-prefix = var.build_id
          }
        }
        portMappings = [
          {
            containerPort = 443
            hostPort      = 443
            protocol      = "tcp"
          }
        ]
      }
    ]
  )
  cpu          = "512"
  memory       = "1024"
  network_mode = "awsvpc"
  requires_compatibilities = [
    "FARGATE"
  ]
  tags = {
    Name    = "${var.build_id}-mhs-inbound-task"
    BuildId = var.build_id
  }
  task_role_arn = var.task_role_arn
  execution_role_arn = var.execution_role_arn
}
