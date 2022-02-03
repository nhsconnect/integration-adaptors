resource "aws_appautoscaling_scheduled_action" "ecs_schedule_stop" {
  name               = "${local.resource_prefix}_schedule_stop"
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_service.ecs_service.cluster}/${aws_ecs_service.ecs_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  schedule           = "at(2022-02-03T12:30:00)"

  scalable_target_action {
    min_capacity = 0
    max_capacity = 1
  }
}