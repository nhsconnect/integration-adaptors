resource "aws_appautoscaling_scheduled_action" "ecs_schedule_stop" {
  count              = var.enable_ecs_schedule ? 1 : 0
  name               = "${local.resource_prefix}_schedule_stop"
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_service.ecs_service.cluster}/${aws_ecs_service.ecs_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  schedule           = var.ecs_scheduler_stop_time

  scalable_target_action {
    min_capacity = 0
    max_capacity = 0
  }
}

resource "aws_appautoscaling_scheduled_action" "ecs_schedule_start" {
  count              = var.enable_ecs_schedule ? 1 : 0  
  name               = "${local.resource_prefix}_schedule_start"
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_service.ecs_service.cluster}/${aws_ecs_service.ecs_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  schedule           = var.ecs_scheduler_start_time

  scalable_target_action {
    min_capacity = 1
    max_capacity = 1
  }
}