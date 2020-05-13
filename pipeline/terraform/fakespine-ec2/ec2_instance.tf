resource "aws_instance" "fake_spine_instance" {
  count = var.instance_count
  ami = data.aws_ami.base_linux.id
  instance_type = "t2.micro"
  key_name = "kainos-dev"
  security_groups = [aws_security_group.fake_spine_security_group.id]
  subnet_id = data.terraform_remote_state.mhs.outputs.subnet_ids[0]
  associate_public_ip_address = true
  availability_zone = "${var.region}a"

  iam_instance_profile = "TerraformJumpboxRole"

  user_data = data.template_cloudinit_config.fake_spine_user_data.rendered

  tags = {
    EnvironmentId = var.environment_id
    Name = "${var.environment_id}_fake-spine-instance_${var.build_id}"
  }
}
