# An autoscaling policy for the MHS outbound ECS service that scales services so that each instance handles the desired
# number of requests per minute.
resource "aws_appautoscaling_policy" "mhs_outbound_autoscaling_policy" {
  name = "${var.environment_id}-mhs-outbound-autoscaling-policy"
  policy_type = "TargetTrackingScaling"
  resource_id = aws_appautoscaling_target.mhs_outbound_autoscaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.mhs_outbound_autoscaling_target.scalable_dimension
  service_namespace = aws_appautoscaling_target.mhs_outbound_autoscaling_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = var.mhs_outbound_service_target_request_count
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label = "${aws_lb.outbound_alb.arn_suffix}/${aws_lb_target_group.outbound_alb_target_group.arn_suffix}"
    }
  }
}
