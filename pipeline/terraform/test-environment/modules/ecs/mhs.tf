resource "aws_ecs_service" "mhs-service" {
  name = "${var.environment}-mhs-service-${var.build_id}"
  cluster = var.cluster_id
  task_definition = aws_ecs_task_definition.mhs-task.arn
  desired_count = 1
  launch_type = "EC2"
}

resource "aws_ecs_task_definition" "mhs-task" {
  family = "${var.environment}-mhs-task-${var.build_id}"

  volume {
    name = "certs-volume"
    host_path = "/home/ec2-user/certs"
  }

  container_definitions = jsonencode(
  [
    {
      name = "${var.environment}-mhs"
      image = "${var.ecr_address}:${var.build_id}"
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group = "/ecs/test-environment"
          awslogs-region = var.region
          awslogs-stream-prefix = var.build_id
        }
      }

      mountPoints = [
        {
          sourceVolume = "certs-volume"
          containerPath = "/usr/src/app/mhs/data/certs/"
        }]

      environment = [
        {
          name = "MHS_LOG_LEVEL"
          value = var.mhs_log_level
        }
      ]

      portMappings = [
        {
          containerPort = 80
          hostPort = 80
          protocol = "tcp"
        },
        {
          containerPort = 443
          hostPort = 443
          protocol = "tcp"
        }
      ]
    }
  ]
  )
  cpu = "256"
  memory = "512"
  requires_compatibilities = [
    "EC2"
  ]
  execution_role_arn = var.task_execution_role
}