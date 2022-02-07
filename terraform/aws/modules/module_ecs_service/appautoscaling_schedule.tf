resource "aws_appautoscaling_scheduled_action" "ecs_schedule_stop" {
  count              = var.enable_ecs_schedule ? 1 : 0
  name               = "${local.resource_prefix}_schedule_stop"
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_service.ecs_service.cluster}/${aws_ecs_service.ecs_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  schedule           = var.ecs_scheduler_stop_time

  scalable_target_action {
    min_capacity = var.ecs_schedule_stop_capacity
    max_capacity = var.ecs_schedule_stop_capacity
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
    min_capacity = var.ecs_schedule_start_capacity
    max_capacity = var.ecs_schedule_start_capacity
  }
}