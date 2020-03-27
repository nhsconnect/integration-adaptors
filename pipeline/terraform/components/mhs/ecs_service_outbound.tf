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