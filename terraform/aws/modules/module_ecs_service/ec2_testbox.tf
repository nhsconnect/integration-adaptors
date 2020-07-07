# Test Box for testing connectivity in the same subnet and security group as the containers

data "aws_ami" "base_linux" {
  most_recent      = true
  name_regex       = "^amzn2-ami-hvm-2.0*"
  owners           = ["137112412989"]

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
      name = "image-type"
      values = ["machine"]
  }

  filter {
      name = "is-public"
      values = ["true"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

resource "aws_instance" "testbox" {
  count = var.create_testbox ? 1 : 0
  availability_zone = "eu-west-2a"

  ami = data.aws_ami.base_linux.id
  instance_type = "t2.micro"
  key_name = "kainos-dev"
  iam_instance_profile = "TerraformJumpboxRole"
  vpc_security_group_ids = concat(var.additional_security_groups,[aws_security_group.service_sg.id, aws_security_group.testbox_sg[0].id])
  subnet_id = var.container_subnet_ids[0]
  #user_data = data.template_cloudinit_config.jumpbox_user_data.rendered
  associate_public_ip_address = false

  tags = merge(local.default_tags, {
     Name = "${local.resource_prefix}-testbox"
  })
}

resource "aws_security_group" "testbox_sg" {
  count = var.create_testbox ? 1 : 0
  name = "${local.resource_prefix}-testbox_sg"
  description = "SG for controlling in and out of ${var.environment}/${var.component} Testbox"
  vpc_id = var.vpc_id

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-testbox_sg"
  })
}

resource "aws_security_group_rule" "allow_ssh_from_jumpbox" {
  count = var.create_testbox ? 1 : 0
  type = "ingress"
  from_port = 22
  to_port = 22
  protocol = "tcp"
  security_group_id = aws_security_group.testbox_sg[0].id
  source_security_group_id = var.jumpbox_sg_id
}
