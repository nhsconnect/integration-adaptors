# Cloudwatch log group for fake-spine service to log to
resource "aws_cloudwatch_log_group" "fake_spine_log_group" {
  name = "/ecs/${var.environment_id}-fake-spine"
  tags = {
    Name = "${var.environment_id}-fake-spine-log-group"
    EnvironmentId = var.environment_id
  }
}