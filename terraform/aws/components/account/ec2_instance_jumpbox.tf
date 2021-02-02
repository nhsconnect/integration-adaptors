resource "aws_instance" "jumpbox" {
  availability_zone = local.availability_zones[0]

  ami = data.aws_ami.base_linux.id
  instance_type = var.jumpbox_size
  key_name = "kainos-dev"
  iam_instance_profile = "TerraformJumpboxRole"
  vpc_security_group_ids = [aws_security_group.jumpbox_sg.id]
  subnet_id = aws_subnet.public_subnet.id
  user_data = data.template_cloudinit_config.jumpbox_user_data.rendered
  associate_public_ip_address = true

  root_block_device {
    delete_on_termination = true
    volume_size = var.jumpbox_volume_size
  }

  tags = merge(local.default_tags, {
     Name = "${local.resource_prefix}-jumpbox"
  })
}
