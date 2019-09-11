resource "aws_ecs_cluster" "mhs_cluster" {
  name = "${var.environment_id}-mhs-cluster"

  tags = {
    Name          = "${var.environment_id}-mhs-cluster"
    EnvironmentId = var.environment_id
  }
}

resource "aws_cloudwatch_log_group" "mhs_outbound_log_group" {
  name = "/ecs/${var.environment_id}-mhs-outbound"
  tags = {
    Name          = "${var.environment_id}-mhs-outbound-log-group"
    EnvironmentId = var.environment_id
  }
}

resource "aws_cloudwatch_log_group" "mhs_inbound_log_group" {
  name = "/ecs/${var.environment_id}-mhs-inbound"
  tags = {
    Name          = "${var.environment_id}-mhs-inbound-log-group"
    EnvironmentId = var.environment_id
  }
}

resource "aws_cloudwatch_log_group" "mhs_route_log_group" {
  name = "/ecs/${var.environment_id}-mhs-route"
  tags = {
    Name          = "${var.environment_id}-mhs-route-log-group"
    EnvironmentId = var.environment_id
  }
}

locals {
  mhs_outbound_base_environment_vars = [
    {
      name  = "MHS_LOG_LEVEL"
      value = var.mhs_log_level
    },
    {
      name  = "MHS_STATE_TABLE_NAME"
      value = aws_dynamodb_table.mhs_state_table.name
    },
    {
      name  = "MHS_SYNC_ASYNC_STATE_TABLE_NAME",
      value = aws_dynamodb_table.mhs_sync_async_table.name
    },
    {
      name  = "MHS_RESYNC_RETRIES",
      value = var.mhs_resynchroniser_max_retries
    },
    {
      name  = "MHS_RESYNC_INTERVAL",
      value = var.mhs_resynchroniser_interval
    },
    {
      name = "MHS_SPINE_ROUTE_LOOKUP_URL",
      value = aws_route53_record.mhs_route_load_balancer_record.name
    },
    {
      name = "MHS_SPINE_ORG_CODE",
      value = var.mhs_spine_org_code
    }
  ]
}

resource "aws_ecs_task_definition" "mhs_outbound_task" {
  family = "${var.environment_id}-mhs-outbound"
  container_definitions = jsonencode(
    [
      {
        name  = "mhs-outbound"
        image = "${var.ecr_address}/mhs/outbound:outbound-${var.build_id}"
        environment = var.mhs_outbound_http_proxy == "" ? local.mhs_outbound_base_environment_vars : concat(local.mhs_outbound_base_environment_vars, [
          {
            name  = "MHS_OUTBOUND_HTTP_PROXY"
            value = var.mhs_outbound_http_proxy
          }
        ])
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
    Name          = "${var.environment_id}-mhs-outbound-task"
    EnvironmentId = var.environment_id
  }
  task_role_arn      = var.task_role_arn
  execution_role_arn = var.execution_role_arn
}

resource "aws_ecs_task_definition" "mhs_inbound_task" {
  family = "${var.environment_id}-mhs-inbound"
  container_definitions = jsonencode(
    [
      {
        name  = "mhs-inbound"
        image = "${var.ecr_address}/mhs/inbound:inbound-${var.build_id}"
        environment = [
          {
            name  = "MHS_LOG_LEVEL"
            value = var.mhs_log_level
          },
          {
            name  = "MHS_STATE_TABLE_NAME"
            value = aws_dynamodb_table.mhs_state_table.name
          },
          {
            name  = "MHS_SYNC_ASYNC_STATE_TABLE_NAME"
            value = aws_dynamodb_table.mhs_sync_async_table.name
          },
          {
            name  = "MHS_INBOUND_QUEUE_URL"
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
    Name          = "${var.environment_id}-mhs-inbound-task"
    EnvironmentId = var.environment_id
  }
  task_role_arn      = var.task_role_arn
  execution_role_arn = var.execution_role_arn
}

# Create an ECS task definition for the route service container image.
resource "aws_ecs_task_definition" "mhs_route_task" {
  family = "${var.environment_id}-mhs-route"
  container_definitions = jsonencode(
    [
      {
        name  = "mhs-route"
        image = "${var.ecr_address}/mhs/route:route-${var.build_id}"
        environment = [
          {
            name  = "MHS_LOG_LEVEL"
            value = var.mhs_log_level
          },
          {
            name = "MHS_SDS_URL"
            value = var.spineroutelookup_service_sds_url
          },
          {
            name = "MHS_DISABLE_SDS_TLS"
            value = var.spineroutelookup_service_disable_sds_tls
          }
        ]
        secrets = [
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
            awslogs-group         = aws_cloudwatch_log_group.mhs_route_log_group.name
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
    Name          = "${var.environment_id}-mhs-route-task"
    EnvironmentId = var.environment_id
  }
  task_role_arn      = var.task_role_arn
  execution_role_arn = var.execution_role_arn
}

resource "aws_ecs_service" "mhs_outbound_service" {
  name                               = "${var.environment_id}-mhs-outbound"
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

  depends_on = [
    aws_lb.outbound_alb
  ]
}

resource "aws_ecs_service" "mhs_inbound_service" {
  name                               = "${var.environment_id}-mhs-inbound"
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

  load_balancer {
    container_name   = jsondecode(aws_ecs_task_definition.mhs_inbound_task.container_definitions)[0].name
    container_port   = jsondecode(aws_ecs_task_definition.mhs_inbound_task.container_definitions)[0].portMappings[0].hostPort
    target_group_arn = aws_lb_target_group.inbound_nlb_target_group.arn
  }

  depends_on = [
    aws_lb.inbound_nlb
  ]
}

# Create an ECS service that runs a configurable number of instances of the route service container across all of the
# VPC's subnets. Each container is register with the route service's LB's target group.
resource "aws_ecs_service" "mhs_route_service" {
  name                               = "${var.environment_id}-mhs-route"
  cluster                            = aws_ecs_cluster.mhs_cluster.id
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100
  desired_count                      = var.mhs_route_service_instance_count
  launch_type                        = "FARGATE"
  scheduling_strategy                = "REPLICA"
  task_definition                    = aws_ecs_task_definition.mhs_route_task.arn

  network_configuration {
    assign_public_ip = false
    security_groups = [
      aws_security_group.mhs_route_security_group.id
    ]
    subnets = aws_subnet.mhs_subnet.*.id
  }

  load_balancer {
    container_name   = jsondecode(aws_ecs_task_definition.mhs_route_task.container_definitions)[0].name
    container_port   = jsondecode(aws_ecs_task_definition.mhs_route_task.container_definitions)[0].portMappings[0].hostPort
    target_group_arn = aws_lb_target_group.route_alb_target_group.arn
  }

  depends_on = [
    aws_lb.route_alb
  ]
}
