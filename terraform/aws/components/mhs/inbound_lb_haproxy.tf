# EC2 instance serving as LB for inbound, used for monitoring the connectivity to inbound
# and verify the incomming traffic

data "aws_ami" "amazon_linux_2" {
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

resource "aws_instance" "haproxy" {
  #count = var.create_opentest_instance ? 1 : 0
  availability_zone = local.availability_zones[0]
  ami = data.aws_ami.amazon_linux_2.id
  instance_type = "t2.micro"
  key_name = "kainos-dev"
  iam_instance_profile        = "TerraformJumpboxRole"
  vpc_security_group_ids      = [ module.mhs_inbound_ecs_service.loadbalancer_sg_id ]
  subnet_id                   = data.terraform_remote_state.base.outputs.ptl_lb_subnet_ids[0]
  user_data                   = data.template_cloudinit_config.haproxy_user_data.rendered
  associate_public_ip_address = false
  private_ip = var.mhs_inbound_lb_ip

  tags = merge(local.default_tags, {
     Name = "${local.resource_prefix}-haproxy"
  })
}

data "template_file" "haproxy_cloudinit_template" {
  template = file("${path.module}/files/haproxy.sh")
  vars = {}
}

data "template_cloudinit_config" "haproxy_user_data" {
  gzip = true
  base64_encode = true
  part {
    content_type = "text/x-shellscript"
    content = data.template_file.haproxy_cloudinit_template.rendered
  }
}

resource "aws_security_group_rule" "haproxy_22_from_jumpbox" {
  description = "Allow SSH connection from listed CIDRS"
  type = "ingress"
  from_port = 22
  to_port = 22
  protocol = "tcp"
  security_group_id = module.mhs_inbound_ecs_service.loadbalancer_sg_id
  source_security_group_id = data.terraform_remote_state.account.outputs.jumpbox_sg_id
}
