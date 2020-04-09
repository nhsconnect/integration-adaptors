# Fake Spine ECS task definition
resource "aws_ecs_task_definition" "fake_spine_task" {
  family = "${var.environment_id}-fake-spine"
  container_definitions = jsonencode(
  [
    {
      name = "fake-spine"
      image = "${var.ecr_address}/fake-spine:${var.build_id}"
      environment = local.fake_spine_base_environment_variables
      secrets = []
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group = aws_cloudwatch_log_group.fake_spine_log_group.name
          awslogs-region = var.region
          awslogs-stream-prefix = var.build_id
          awslogs-datetime-format = "\\[%Y-%m-%dT%H:%M:%S\\.%fZ\\]"
        }
      }
      portMappings = [
        {
          containerPort = 443
          hostPort = 443
          protocol = "tcp"
        },
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
    Name = "${var.environment_id}-fake-spine-task"
    EnvironmentId = var.environment_id
  }
  task_role_arn = var.task_role_arn
  execution_role_arn = var.execution_role_arn
}
