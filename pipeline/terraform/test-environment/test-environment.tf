provider "aws" {
  profile = "default"
  region = var.region
}

resource "aws_ecs_task_definition" "test-environment-mhs-inbound-task" {
  family = "mhs-inbound-task-${var.build_id}"

  volume {
    name = "certs-volume"
    host_path = "/home/ec2-user/certs"
  }

  container_definitions = jsonencode(
  [
    {
      name = "mhs"
      image = "${var.ecr_address}:inbound-${var.build_id}"
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group = "/ecs/inbound-test-environment"
          awslogs-region = var.region
          awslogs-stream-prefix = var.build_id
        }
      }

      mountPoints = [{
        sourceVolume = "certs-volume"
        containerPath = "/usr/src/app/mhs/common/data/certs/"
      }]

      environment = [
        {
          name = "MHS_LOG_LEVEL"
          value = var.mhs_log_level
        },
        {
          name = "MHS_STATE_TABLE_NAME",
          value = var.mhs_state_table_name
        },
        {
          name = "MHS_INBOUND_QUEUE_HOST",
          value = var.mhs_inbound_queue_host
        },
        {
          name = "MHS_INBOUND_QUEUE_USERNAME",
          value = var.mhs_inbound_queue_username
        },
        {
          name = "MHS_INBOUND_QUEUE_PASSWORD",
          value = var.mhs_inbound_queue_password
        },
        {
          name = "MHS_SYNC_ASYNC_STATE_TABLE_NAME",
          value = var.mhs_sync_async_state_table_name
        }

      ]

      portMappings = [
        {
          containerPort = 443
          hostPort = 443
          protocol = "tcp"
        }
      ]
    }
  ]
  )
  cpu = "128"
  memory = "256"
  requires_compatibilities = [
    "EC2"
  ]
  execution_role_arn = var.task_execution_role
}

resource "aws_ecs_task_definition" "test-environment-mhs-outbound-task" {
  family = "mhs-outbound-task-${var.build_id}"

  volume {
    name = "certs-volume"
    host_path = "/home/ec2-user/certs"
  }

  container_definitions = jsonencode(
  [
    {
      name = "mhs"
      image = "${var.ecr_address}:outbound-${var.build_id}"
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group = "/ecs/outbound-test-environment"
          awslogs-region = var.region
          awslogs-stream-prefix = var.build_id
        }
      }

      mountPoints = [{
        sourceVolume = "certs-volume"
        containerPath = "/usr/src/app/mhs/common/data/certs/"
      }]

      environment = [
        {
          name = "MHS_LOG_LEVEL"
          value = var.mhs_log_level
        },
        {
          name = "MHS_STATE_TABLE_NAME",
          value = var.mhs_state_table_name
        }
      ]

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
  cpu = "128"
  memory = "256"
  requires_compatibilities = [
    "EC2"
  ]
  execution_role_arn = var.task_execution_role
}

resource "aws_ecs_task_definition" "test-environment-scr-service-task" {
  family = "scr-service-task-${var.build_id}"

  container_definitions = jsonencode(
  [
    {
      name = "scr-service"
      image = "${var.scr_ecr_address}:${var.build_id}"
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group = "/ecs/scr-service-environment"
          awslogs-region = var.region
          awslogs-stream-prefix = var.build_id
        }
      }

      environment = [
        {
          name = "SCR_LOG_LEVEL"
          value = var.scr_log_level
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
}

resource "aws_ecs_service" "test-outbound-mhs-environment-service" {
  name = "${var.build_id}-outbound-service"
  cluster = var.cluster_id
  task_definition = aws_ecs_task_definition.test-environment-mhs-outbound-task.arn
  desired_count = 1
  launch_type = "EC2"
}

resource "aws_ecs_service" "test-inbound-mhs-environment-service" {
  name = "${var.build_id}-inbound-service"
  cluster = var.cluster_id
  task_definition = aws_ecs_task_definition.test-environment-mhs-inbound-task.arn
  desired_count = 1
  launch_type = "EC2"
}

resource "aws_ecs_service" "test-scr-service-environment" {
  name = "${var.build_id}-scr-service"
  cluster = var.cluster_id
  task_definition = aws_ecs_task_definition.test-environment-scr-service-task.arn
  desired_count = 1
  launch_type = "EC2"
}

