data "aws_iam_role" "ecs_autoscale_role" {
  name = "AWSServiceRoleForApplicationAutoScaling_ECSService"
}
