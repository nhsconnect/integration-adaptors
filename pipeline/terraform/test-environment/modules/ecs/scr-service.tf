resource "aws_ecs_service" "scr-service" {
  name = "${var.environment}-scr-service-${var.build_id}"
  cluster = var.cluster_id
  task_definition = aws_ecs_task_definition.scr-service-task.arn
  desired_count = 1
  launch_type = "EC2"
}

resource "aws_ecs_task_definition" "scr-service-task" {
  family = "${var.environment}-scr-service-task-${var.build_id}"

  container_definitions = jsonencode(
  [
    {
      name = "${var.environment}-scr-service"
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
  memory = "256"
  requires_compatibilities = [
    "EC2"
  ]
  execution_role_arn = var.task_execution_role
}