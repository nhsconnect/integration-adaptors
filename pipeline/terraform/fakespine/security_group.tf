# fake-spine security group
resource "aws_security_group" "fake_spine_security_group" {
  name = "Fake Spine Security Group"
  description = "The security group used to control traffic for the fake-spine component."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.environment_id}-fake-spine-sg"
    EnvironmentId = var.environment_id
  }
}
