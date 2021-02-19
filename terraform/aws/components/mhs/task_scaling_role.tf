data "aws_iam_role" "ecs_autoscale_role" {
  name = "aws-service-role/ecs.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_ECSService"
}
