terraform {
  # Store the Terraform state in an S3 bucket
  backend "s3" {
    # Intentionally blank - all parameters provided in command line
  }
}

# Setup AWS provider
provider "aws" {
  version = "~> 2.27"
  profile = "default"
  region = var.region
}

# SCR ECS task definition
resource "aws_ecs_task_definition" "test-environment-scr-service-task" {
  family = "scr-service-task-${var.build_id}"

  container_definitions = jsonencode(
  [
    {
      name = "scr-service"
      image = "${var.ecr_address}/scr-web-service:${var.build_id}"
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group = "/ecs/scr-service-environment"
          awslogs-region = var.region
          awslogs-stream-prefix = var.build_id
          awslogs-datetime-format = "\\[%Y-%m-%dT%H:%M:%S\\.%fZ\\]"
        }
      }

      environment = [
        {
          name = "SCR_LOG_LEVEL"
          value = var.scr_log_level
        },
        {
          name = "SCR_MHS_ADDRESS"
          value = var.scr_mhs_address
        }
      ]

      secrets = var.scr_mhs_ca_certs_arn == "" ? [] : [
        {
          name = "SCR_SECRET_MHS_CA_CERTS",
          valueFrom = var.scr_mhs_ca_certs_arn
        }
      ]

      portMappings = [
        {
          containerPort = 80
          hostPort = var.scr_service_port
          protocol = "tcp"
        }
      ]
    }
  ]
  )
  cpu = "128"
  memory = "128"
  requires_compatibilities = [
    "EC2"
  ]
  execution_role_arn = var.task_execution_role
  tags = {
    Name = "${var.environment_id}-scr-task"
    EnvironmentId = var.environment_id
  }
}

# SCR ECS service
resource "aws_ecs_service" "test-scr-service-environment" {
  name = "${var.build_id}-scr-service"
  cluster = var.cluster_id
  task_definition = aws_ecs_task_definition.test-environment-scr-service-task.arn
  desired_count = 1
  launch_type = "EC2"
}

