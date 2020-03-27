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
