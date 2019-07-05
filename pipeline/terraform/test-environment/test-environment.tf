provider "aws" {
  profile = "default"
  region = var.region
}

# TODO: Load Opentest certificates. Simplest approach would be to mount a directory on the host machine.

resource "aws_ecs_task_definition" "test-environment-mhs-task" {
  family = "${var.build_id}-mhs-task"

  # TODO: Get from ECR repo - See https://docs.aws.amazon.com/AmazonECR/latest/userguide/ECR_on_ECS.html
  container_definitions = jsonencode(
  [
    {
      name = "mhs"
      # TODO: Use our container image
      image = "nginx:latest"
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group = "/ecs/test-environment"
          awslogs-region = var.region
          awslogs-stream-prefix = var.build_id
        }
      }

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

resource "aws_ecs_service" "test-environment-service" {
  name = "${var.build_id}-service"
  cluster = var.cluster_id
  task_definition = aws_ecs_task_definition.test-environment-mhs-task.arn
  desired_count = 1
  launch_type = "EC2"
}
