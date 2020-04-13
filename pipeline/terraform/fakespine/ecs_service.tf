# Create an ECS service that runs a configurable number of instances of the fake-spine service container across all of the
# VPC's subnets. Each container is register with the route service's LB's target group.
resource "aws_ecs_service" "fake_spine_service" {
  name = "${var.environment_id}-fake-spine"
  # cluster = "arn:aws:ecs:eu-west-2:067756640211:cluster/testing-fake-spine"
  cluster = data.terraform_remote_state.mhs.outputs.cluster_id
  deployment_maximum_percent = 200
  deployment_minimum_healthy_percent = 100
  desired_count = var.fake_spine_service_minimum_instance_count
  launch_type = "FARGATE"
  scheduling_strategy = "REPLICA"
  task_definition = aws_ecs_task_definition.fake_spine_task.arn
  # health_check_grace_period_seconds = 120 // give two minutes before killing the service

  network_configuration {
    assign_public_ip = true
    security_groups = [
      aws_security_group.fake_spine_security_group.id
    ]
    subnets = data.terraform_remote_state.mhs.outputs.subnet_ids
  }

  # load_balancer {
  #   # In the MHS route task definition, we define only 1 container, and for that container, we expose only 1 port
  #   # That is why in these 2 lines below we do "[0]" to reference that one container and port definition.
  #   container_name = jsondecode(aws_ecs_task_definition.fake_spine_task.container_definitions)[0].name
  #   container_port = jsondecode(aws_ecs_task_definition.fake_spine_task.container_definitions)[0].portMappings[0].hostPort
  #   target_group_arn = aws_lb_target_group.fake_spine_alb_target_group.arn
  # }

  # depends_on = [
  #   aws_lb.fake_spine_alb
  # ]

  # Preserve the autoscaled instance count when this service is updated
  # lifecycle {
  #   ignore_changes = [
  #     "desired_count"
  #   ]
  # }
}
