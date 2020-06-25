resource "aws_instance" "jumpbox" {
  name = "${local.resource_prefix}-jumpbox"
  availability_zones = local.availability_zones[0]

  image_id = data.aws_ami.base_linux.id
  instance_type = "t2.micro"
  key_name = "kainos-dev"
  iam_instance_profile = "TerraformJumpboxRole"
  vpc_security_groups = [aws_security_group.jumpbox_sg.id]
  subnet_id = aws_subnet.public_subnet.id
  user_data = data.template_cloudinit_config.jumpbox_user_data.rendered
  associate_public_ip_address = true

  tags = merge(local.default_tags, {
     Name = "${local.resource_prefix}-jumpbox"
  })
}
