# An autoscaling policy for the MHS route ECS service that scales services so that each instance handles the desired
# number of requests per minute.
# resource "aws_appautoscaling_policy" "fake_spine_autoscaling_policy" {
#   name = "${var.environment_id}-fake-spine-autoscaling-policy"
#   policy_type = "TargetTrackingScaling"
#   resource_id = aws_appautoscaling_target.fake_spine_autoscaling_target.resource_id
#   scalable_dimension = aws_appautoscaling_target.fake_spine_autoscaling_target.scalable_dimension
#   service_namespace = aws_appautoscaling_target.fake_spine_autoscaling_target.service_namespace

#   target_tracking_scaling_policy_configuration {
#     target_value = var.fake_spine_service_target_request_count
#     predefined_metric_specification {
#       predefined_metric_type = "ALBRequestCountPerTarget"
#       resource_label = "${aws_lb.fake_spine_alb.arn_suffix}/${aws_lb_target_group.fake_spine_alb_target_group.arn_suffix}"
#     }
#   }
# }
