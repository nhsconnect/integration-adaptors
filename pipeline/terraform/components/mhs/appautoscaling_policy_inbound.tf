# An autoscaling policy for the MHS inbound ECS service that scales services so that each instance handles the desired
# number of requests per minute.
resource "aws_appautoscaling_policy" "mhs_inbound_autoscaling_policy" {
  name = "${var.environment_id}-mhs-inbound-autoscaling-policy"
  policy_type = "TargetTrackingScaling"
  resource_id = aws_appautoscaling_target.mhs_inbound_autoscaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.mhs_inbound_autoscaling_target.scalable_dimension
  service_namespace = aws_appautoscaling_target.mhs_inbound_autoscaling_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = var.mhs_inbound_service_target_cpu_utilization
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}
