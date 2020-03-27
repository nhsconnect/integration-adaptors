# The ECS cluster within which all MHS tasks will run
resource "aws_ecs_cluster" "base_cluster" {
  name = "${var.environment_id}-base-cluster"

  tags = {
    Name = "${var.environment_id}-base-cluster"
    EnvironmentId = var.environment_id
  }
}