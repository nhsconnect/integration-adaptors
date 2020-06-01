

# An autoscaling policy for the MHS route ECS service that scales services so that each instance handles the desired
# number of requests per minute.
resource "aws_appautoscaling_policy" "mhs_route_autoscaling_policy" {
  count = var.enable_load_balancing ? 1 : 0
  name               = "${local.resource_prefix}-autoscaling_policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.service_autoscaling_target[0].resource_id
  scalable_dimension = aws_appautoscaling_target.service_autoscaling_target[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.service_autoscaling_target[0].service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = var.service_target_request_count
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label = "${aws_lb.service_load_balancer[0].arn_suffix}/${aws_lb_target_group.service_target_group[0].arn_suffix}"
    }
  }
}
