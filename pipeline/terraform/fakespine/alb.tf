##############
# fake-spine load balancer
##############

# Application load balancer for MHS outbound
resource "aws_lb" "fake_spine_alb" {
  internal = true
  load_balancer_type = "application"
  subnets = aws_subnet.mhs_subnet.*.id
  security_groups = [
    aws_security_group.alb_fake_spine_security_group.id
  ]

  access_logs {
    bucket = aws_s3_bucket.mhs_access_logs_bucket.bucket
    prefix = "fake_spine-${var.build_id}"
    enabled = true
  }

  # We need the S3 bucket to have the policy set in order for the
  # load balancer to have access to store access logs
  depends_on = [
    aws_s3_bucket_policy.mhs_access_logs_bucket_policy
  ]

  tags = {
    Name = "${var.environment_id}-fake-spine-alb"
    EnvironmentId = var.environment_id
  }
}
