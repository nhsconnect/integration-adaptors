######################
# AWS ECS MHS cluster and MHS services/tasks to run in it
######################







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



# Create an ECS task definition for the MHS route service container image.
resource "aws_ecs_task_definition" "mhs_route_task" {
  family = "${var.environment_id}-mhs-route"
  container_definitions = jsonencode(
  [
    {
      name = "mhs-route"
      image = "${var.ecr_address}/mhs/route:route-${var.build_id}"
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
