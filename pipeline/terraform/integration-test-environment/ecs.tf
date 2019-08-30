resource "aws_ecs_cluster" "mhs_cluster" {
  name = "${var.build_id}-mhs-cluster"

  tags = {
    Name    = "${var.build_id}-mhs-cluster"
    BuildId = var.build_id
  }
}

resource "aws_cloudwatch_log_group" "mhs_outbound_log_group" {
  name = "/ecs/${var.build_id}-mhs-outbound"
  tags = {
    Name    = "${var.build_id}-mhs-outbound-log-group"
    BuildId = var.build_id
  }
}

resource "aws_cloudwatch_log_group" "mhs_inbound_log_group" {
  name = "/ecs/${var.build_id}-mhs-inbound"
  tags = {
    Name    = "${var.build_id}-mhs-inbound-log-group"
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
        secrets = [
          {
            name      = "MHS_PARTY_KEY"
            valueFrom = var.party_key_arn
          },
          {
            name      = "MHS_CLIENT_CERT"
            valueFrom = var.client_cert_arn
          },
          {
            name      = "MHS_CLIENT_KEY"
            valueFrom = var.client_key_arn
          },
          {
            name      = "MHS_CA_CERTS"
            valueFrom = var.ca_certs_arn
          }
        ]
        essential = true
        logConfiguration = {
          logDriver = "awslogs"
          options = {
            awslogs-group         = aws_cloudwatch_log_group.mhs_outbound_log_group.name
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
  task_role_arn      = var.task_role_arn
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
          },
          {
            name      = "MHS_PARTY_KEY"
            valueFrom = var.party_key_arn
          },
          {
            name      = "MHS_CLIENT_KEY"
            valueFrom = var.client_key_arn
          },
          {
            name      = "MHS_CA_CERTS"
            valueFrom = var.ca_certs_arn
          }
        ]
        essential = true
        logConfiguration = {
          logDriver = "awslogs"
          options = {
            awslogs-group         = aws_cloudwatch_log_group.mhs_inbound_log_group.name
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
  task_role_arn      = var.task_role_arn
  execution_role_arn = var.execution_role_arn
}

resource "aws_ecs_service" "mhs_outbound_service" {
  name                               = "${var.build_id}-mhs-outbound"
  cluster                            = aws_ecs_cluster.mhs_cluster.id
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  desired_count                      = var.mhs_outbound_service_instance_count
  launch_type                        = "FARGATE"
  scheduling_strategy                = "REPLICA"
  task_definition                    = aws_ecs_task_definition.mhs_outbound_task.arn

  network_configuration {
    assign_public_ip = false
    security_groups = [
      aws_security_group.mhs_outbound_security_group.id
    ]
    subnets = aws_subnet.mhs_subnet.*.id
  }

  load_balancer {
    container_name   = jsondecode(aws_ecs_task_definition.mhs_outbound_task.container_definitions)[0].name
    container_port   = jsondecode(aws_ecs_task_definition.mhs_outbound_task.container_definitions)[0].portMappings[0].hostPort
    target_group_arn = aws_lb_target_group.outbound_alb_target_group.arn
  }
}

resource "aws_ecs_service" "mhs_inbound_service" {
  name                               = "${var.build_id}-mhs-inbound"
  cluster                            = aws_ecs_cluster.mhs_cluster.id
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  desired_count                      = var.mhs_inbound_service_instance_count
  launch_type                        = "FARGATE"
  scheduling_strategy                = "REPLICA"
  task_definition                    = aws_ecs_task_definition.mhs_inbound_task.arn

  network_configuration {
    assign_public_ip = false
    security_groups = [
      aws_security_group.mhs_inbound_security_group.id
    ]
    subnets = aws_subnet.mhs_subnet.*.id
  }
}
