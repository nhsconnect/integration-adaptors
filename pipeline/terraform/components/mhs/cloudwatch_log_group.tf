# Cloudwatch log group for MHS outbound to log to
resource "aws_cloudwatch_log_group" "mhs_outbound_log_group" {
  name = "/ecs/${var.environment_id}-mhs-outbound"
  tags = {
    Name = "${var.environment_id}-mhs-outbound-log-group"
    EnvironmentId = var.environment_id
  }
}

# Cloudwatch log group for MHS inbound to log to
resource "aws_cloudwatch_log_group" "mhs_inbound_log_group" {
  name = "/ecs/${var.environment_id}-mhs-inbound"
  tags = {
    Name = "${var.environment_id}-mhs-inbound-log-group"
    EnvironmentId = var.environment_id
  }
}

# Cloudwatch log group for MHS route service to log to
resource "aws_cloudwatch_log_group" "mhs_route_log_group" {
  name = "/ecs/${var.environment_id}-mhs-route"
  tags = {
    Name = "${var.environment_id}-mhs-route-log-group"
    EnvironmentId = var.environment_id
  }
}
