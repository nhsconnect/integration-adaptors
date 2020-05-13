# fake-spine security group
resource "aws_security_group" "fake_spine_security_group" {
  name = "Fake Spine Security Group"
  description = "The security group used to control traffic for the fake-spine component."
  vpc_id = data.terraform_remote_state.mhs.outputs.vpc_id

  tags = {
    Name = "${var.environment_id}-fake-spine-sg"
    EnvironmentId = var.environment_id
  }
}

resource "aws_security_group" "fake_spine_alb_security_group" { 
  name = "Fake Spine ALB Security Group"
  description = "The security group used by Application Load Balancer in front of fakespine"
  vpc_id = data.terraform_remote_state.mhs.outputs.vpc_id

  tags = {
    Name = "${var.environment_id}-fake-spine-alb-sg"
    EnvironmentId = var.environment_id
  }
}