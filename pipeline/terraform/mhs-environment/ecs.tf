######################
# AWS ECS MHS cluster and MHS services/tasks to run in it
######################

# The ECS cluster within which all MHS tasks will run
resource "aws_ecs_cluster" "mhs_cluster" {
  name = "${var.environment_id}-mhs-cluster"

  tags = {
    Name = "${var.environment_id}-mhs-cluster"
    EnvironmentId = var.environment_id
  }
}

# Cloudwatch log group for MHS outbound to log to
resource "aws_cloudwatch_log_group" "mhs_outbound_log_group" {
  name = "/ecs/${var.environment_id}-mhs-outbound"
  tags = {
    Name = "${var.environment_id}-mhs-outbound-log-group"
    EnvironmentId = var.environment_id
  }
}

# Cloudwatch log group for MHS inbound to log to
resource "aws_cloudwatch_log_group" "mhs_inbound_log_group" {
  name = "/ecs/${var.environment_id}-mhs-inbound"
  tags = {
    Name = "${var.environment_id}-mhs-inbound-log-group"
    EnvironmentId = var.environment_id
  }
}

# Cloudwatch log group for MHS route service to log to
resource "aws_cloudwatch_log_group" "mhs_route_log_group" {
  name = "/ecs/${var.environment_id}-mhs-route"
  tags = {
    Name = "${var.environment_id}-mhs-route-log-group"
    EnvironmentId = var.environment_id
  }
}

# This locals block is used in mhs_outbound_task below to define the
# environment variables
locals {
  mhs_outbound_base_environment_vars = [
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
      name = "MHS_RESYNC_RETRIES"
      value = var.mhs_resynchroniser_max_retries
    },
    {
      name = "MHS_RESYNC_INTERVAL"
      value = var.mhs_resynchroniser_interval
    },
    {
      name = "MHS_SPINE_ROUTE_LOOKUP_URL"
      value = "https://${aws_route53_record.mhs_route_load_balancer_record.name}"
    },
    {
      name = "MHS_SPINE_ORG_CODE"
      value = var.mhs_spine_org_code
    },
    {
      name = "MHS_SPINE_REQUEST_MAX_SIZE"
      value = var.mhs_spine_request_max_size
    },
    {
      name = "MHS_FORWARD_RELIABLE_ENDPOINT_URL"
      value = var.mhs_forward_reliable_endpoint_url
    },
    {
      name = "MHS_OUTBOUND_VALIDATE_CERTIFICATE"
      value = var.mhs_outbound_validate_certificate
    }
  ]
  mhs_outbound_base_secrets = [
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
}

# MHS outbound ECS task definition
resource "aws_ecs_task_definition" "mhs_outbound_task" {
  family = "${var.environment_id}-mhs-outbound"
  container_definitions = jsonencode(
  [
    {
      name = "mhs-outbound"
      image = "${var.ecr_address}/mhs/outbound:${var.build_id}"
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

# MHS inbound ECS task definition
resource "aws_ecs_task_definition" "mhs_inbound_task" {
  family = "${var.environment_id}-mhs-inbound"
  container_definitions = jsonencode(
  [
    {
      name = "mhs-inbound"
      image = "${var.ecr_address}/mhs/inbound:${var.build_id}"
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
          name = "MHS_INBOUND_QUEUE_BROKERS"
          value = var.inbound_queue_brokers
        },
        {
          name = "MHS_INBOUND_QUEUE_NAME"
          value = var.inbound_queue_name
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

# Create an ECS task definition for the MHS route service container image.
resource "aws_ecs_task_definition" "mhs_route_task" {
  family = "${var.environment_id}-mhs-route"
  container_definitions = jsonencode(
  [
    {
      name = "mhs-route"
      image = "${var.ecr_address}/mhs/route:${var.build_id}"
      environment = [
        {
          name = "MHS_LOG_LEVEL"
          value = var.mhs_log_level
        },
        {
          name = "MHS_SDS_URL"
          value = var.spineroutelookup_service_sds_url
        },
        {
          name = "MHS_SDS_SEARCH_BASE"
          value = var.spineroutelookup_service_search_base
        },
        {
          name = "MHS_DISABLE_SDS_TLS"
          value = var.spineroutelookup_service_disable_sds_tls
        },
        {
          name = "MHS_SDS_REDIS_CACHE_HOST"
          value = aws_elasticache_replication_group.elasticache_replication_group.primary_endpoint_address
        },
        {
          name = "MHS_SDS_REDIS_CACHE_PORT"
          value = tostring(aws_elasticache_replication_group.elasticache_replication_group.port)
        }
      ]
      secrets = [
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
          awslogs-group = aws_cloudwatch_log_group.mhs_route_log_group.name
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
    Name = "${var.environment_id}-mhs-route-task"
    EnvironmentId = var.environment_id
  }
  task_role_arn = var.task_role_arn
  execution_role_arn = var.execution_role_arn
}


# MHS outbound service that runs multiple of the MHS outbound task definition
# defined above
resource "aws_ecs_service" "mhs_outbound_service" {
  name = "${var.environment_id}-mhs-outbound"
  cluster = aws_ecs_cluster.mhs_cluster.id
  deployment_maximum_percent = 200
  deployment_minimum_healthy_percent = 100
  desired_count = var.mhs_outbound_service_minimum_instance_count
  launch_type = "FARGATE"
  scheduling_strategy = "REPLICA"
  task_definition = aws_ecs_task_definition.mhs_outbound_task.arn

  network_configuration {
    assign_public_ip = false
    security_groups = [
      aws_security_group.mhs_outbound_security_group.id
    ]
    subnets = aws_subnet.mhs_subnet.*.id
  }

  load_balancer {
    # In the MHS outbound task definition, we define only 1 container, and for that container, we expose only 1 port
    # That is why in these 2 lines below we do "[0]" to reference that one container and port definition.
    container_name = jsondecode(aws_ecs_task_definition.mhs_outbound_task.container_definitions)[0].name
    container_port = jsondecode(aws_ecs_task_definition.mhs_outbound_task.container_definitions)[0].portMappings[0].hostPort
    target_group_arn = aws_lb_target_group.outbound_alb_target_group.arn
  }

  depends_on = [
    aws_lb.outbound_alb
  ]

  # Preserve the autoscaled instance count when this service is updated
  lifecycle {
    ignore_changes = [
      "desired_count"
    ]
  }
}

# The autoscaling target that configures autoscaling for the MHS outbound ECS service.
resource "aws_appautoscaling_target" "mhs_outbound_autoscaling_target" {
  max_capacity = var.mhs_outbound_service_maximum_instance_count
  min_capacity = var.mhs_outbound_service_minimum_instance_count
  resource_id = "service/${aws_ecs_cluster.mhs_cluster.name}/${aws_ecs_service.mhs_outbound_service.name}"
  role_arn = var.task_scaling_role_arn
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace = "ecs"
}

# An autoscaling policy for the MHS outbound ECS service that scales services so that each instance handles the desired
# number of requests per minute.
resource "aws_appautoscaling_policy" "mhs_outbound_autoscaling_policy" {
  name = "${var.environment_id}-mhs-outbound-autoscaling-policy"
  policy_type = "TargetTrackingScaling"
  resource_id = aws_appautoscaling_target.mhs_outbound_autoscaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.mhs_outbound_autoscaling_target.scalable_dimension
  service_namespace = aws_appautoscaling_target.mhs_outbound_autoscaling_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = var.mhs_outbound_service_target_request_count
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label = "${aws_lb.outbound_alb.arn_suffix}/${aws_lb_target_group.outbound_alb_target_group.arn_suffix}"
    }
  }
}

# MHS inbound service that runs multiple of the MHS outbound task definition
# defined above
resource "aws_ecs_service" "mhs_inbound_service" {
  name = "${var.environment_id}-mhs-inbound"
  cluster = aws_ecs_cluster.mhs_cluster.id
  deployment_maximum_percent = 200
  deployment_minimum_healthy_percent = 100
  desired_count = var.mhs_inbound_service_minimum_instance_count
  launch_type = "FARGATE"
  scheduling_strategy = "REPLICA"
  task_definition = aws_ecs_task_definition.mhs_inbound_task.arn

  network_configuration {
    assign_public_ip = false
    security_groups = [
      aws_security_group.mhs_inbound_security_group.id
    ]
    subnets = aws_subnet.mhs_subnet.*.id
  }

  load_balancer {
    # In the MHS inbound task definition, we define only 1 container, and for that container, we expose 2 ports.
    # The first of these ports is 443, the port that we want to expose as it handles inbound requests from Spine.
    # The other port is for doing healthchecks, only the load balancer will be making requests to that port.
    # That is why in these 2 lines below we do "[0]" to reference that one container and the first port definition.
    container_name = jsondecode(aws_ecs_task_definition.mhs_inbound_task.container_definitions)[0].name
    container_port = jsondecode(aws_ecs_task_definition.mhs_inbound_task.container_definitions)[0].portMappings[0].hostPort
    target_group_arn = aws_lb_target_group.inbound_nlb_target_group.arn
  }

  depends_on = [
    aws_lb.inbound_nlb
  ]

  # Preserve the autoscaled instance count when this service is updated
  lifecycle {
    ignore_changes = [
      "desired_count"
    ]
  }
}

# The autoscaling target that configures autoscaling for the MHS inbound ECS service.
resource "aws_appautoscaling_target" "mhs_inbound_autoscaling_target" {
  max_capacity = var.mhs_inbound_service_maximum_instance_count
  min_capacity = var.mhs_inbound_service_minimum_instance_count
  resource_id = "service/${aws_ecs_cluster.mhs_cluster.name}/${aws_ecs_service.mhs_inbound_service.name}"
  role_arn = var.task_scaling_role_arn
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace = "ecs"
}

# An autoscaling policy for the MHS inbound ECS service that scales services so that each instance handles the desired
# number of requests per minute.
resource "aws_appautoscaling_policy" "mhs_inbound_autoscaling_policy" {
  name = "${var.environment_id}-mhs-inbound-autoscaling-policy"
  policy_type = "TargetTrackingScaling"
  resource_id = aws_appautoscaling_target.mhs_inbound_autoscaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.mhs_inbound_autoscaling_target.scalable_dimension
  service_namespace = aws_appautoscaling_target.mhs_inbound_autoscaling_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = var.mhs_inbound_service_target_cpu_utilization
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}

# Create an ECS service that runs a configurable number of instances of the route service container across all of the
# VPC's subnets. Each container is register with the route service's LB's target group.
resource "aws_ecs_service" "mhs_route_service" {
  name = "${var.environment_id}-mhs-route"
  cluster = aws_ecs_cluster.mhs_cluster.id
  deployment_maximum_percent = 200
  deployment_minimum_healthy_percent = 100
  desired_count = var.mhs_route_service_minimum_instance_count
  launch_type = "FARGATE"
  scheduling_strategy = "REPLICA"
  task_definition = aws_ecs_task_definition.mhs_route_task.arn

  network_configuration {
    assign_public_ip = false
    security_groups = [
      aws_security_group.mhs_route_security_group.id
    ]
    subnets = aws_subnet.mhs_subnet.*.id
  }

  load_balancer {
    # In the MHS route task definition, we define only 1 container, and for that container, we expose only 1 port
    # That is why in these 2 lines below we do "[0]" to reference that one container and port definition.
    container_name = jsondecode(aws_ecs_task_definition.mhs_route_task.container_definitions)[0].name
    container_port = jsondecode(aws_ecs_task_definition.mhs_route_task.container_definitions)[0].portMappings[0].hostPort
    target_group_arn = aws_lb_target_group.route_alb_target_group.arn
  }

  depends_on = [
    aws_lb.route_alb
  ]

  # Preserve the autoscaled instance count when this service is updated
  lifecycle {
    ignore_changes = [
      "desired_count"
    ]
  }
}

# The autoscaling target that configures autoscaling for the MHS route ECS service.
resource "aws_appautoscaling_target" "mhs_route_autoscaling_target" {
  max_capacity = var.mhs_route_service_maximum_instance_count
  min_capacity = var.mhs_route_service_minimum_instance_count
  resource_id = "service/${aws_ecs_cluster.mhs_cluster.name}/${aws_ecs_service.mhs_route_service.name}"
  role_arn = var.task_scaling_role_arn
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace = "ecs"
}

# An autoscaling policy for the MHS route ECS service that scales services so that each instance handles the desired
# number of requests per minute.
resource "aws_appautoscaling_policy" "mhs_route_autoscaling_policy" {
  name = "${var.environment_id}-mhs-route-autoscaling-policy"
  policy_type = "TargetTrackingScaling"
  resource_id = aws_appautoscaling_target.mhs_route_autoscaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.mhs_route_autoscaling_target.scalable_dimension
  service_namespace = aws_appautoscaling_target.mhs_route_autoscaling_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = var.mhs_route_service_target_request_count
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label = "${aws_lb.route_alb.arn_suffix}/${aws_lb_target_group.route_alb_target_group.arn_suffix}"
    }
  }
}
