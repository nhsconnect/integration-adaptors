# The autoscaling target that configures autoscaling for the MHS route ECS service.
resource "aws_appautoscaling_target" "fake_spine_autoscaling_target" {
  max_capacity = var.fake_spine_service_maximum_instance_count
  min_capacity = var.fake_spine_service_minimum_instance_count
  resource_id = "service/${data.terraform_remote_state.mhs.outputs.cluster_name}/${aws_ecs_service.fake_spine_service.name}"
  role_arn = var.task_scaling_role_arn
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace = "ecs"
}
