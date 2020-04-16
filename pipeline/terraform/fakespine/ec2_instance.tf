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

# resource "aws_iam_instance_profile" "fake_spine_instance_profile" {
#  name = "${var.environment_id}-fake-spine_instance_profile"
#  role = data.aws_iam_role.fake_spine_iam_role.name
# }

# resource "aws_iam_role" "fake_spine_iam_role" {
#   name = "${var.environment_id}-fake-spine_iam_role"
#   assume_role_policy = data.aws_iam_policy_document.fake_spine_assume_role.json
# }

# data "aws_iam_policy_document" "fake_spine_assume_role" {
#   statement {
#     actions = ["sts:AssumeRole"]

#     principals {
#       type        = "Service"
#       identifiers = ["ec2.amazonaws.com"]
#     }
#   }
# }

# resource "aws_iam_role_policy_attachment" "fs_role_S3" {
#   policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
#   role       = data.aws_iam_role.fake_spine_iam_role.name
# }

# resource "aws_iam_role_policy_attachment" "fs_role_Secrets" {
#   policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
#   role       = data.aws_iam_role.fake_spine_iam_role.name
# }

# resource "aws_iam_role_policy_attachment" "fs_role_ECR" {
#   policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
#   role       = data.aws_iam_role.fake_spine_iam_role.name
# }

# resource "aws_iam_role_policy_attachment" "fs_role_CW" {
#   policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
#   role       = data.aws_iam_role.fake_spine_iam_role.name
# }

resource "aws_instance" "fake_spine_instance" {
  ami = data.aws_ami.base_linux.id
  instance_type = "t2.micro"
  key_name = "kainos-dev"
  security_groups = [aws_security_group.fake_spine_security_group.id]
  subnet_id = data.terraform_remote_state.mhs.outputs.subnet_ids[0]
  associate_public_ip_address = true
  availability_zone = "eu-west-2a"

  iam_instance_profile = "TerraformJumpboxRole"

  user_data = data.template_cloudinit_config.fake_spine_user_data.rendered

  tags = {
    EnvironmentId = var.environment_id
    Name = "${var.environment_id}-fake-spine_instance"
  }
}

data "template_cloudinit_config" "fake_spine_user_data" {
  gzip          = "true"
  base64_encode = "true"

    part {
    content_type = "text/x-shellscript"
    content      = file("${path.module}/files/cloudinit.sh")
  }
}

resource "aws_security_group_rule" "fake_spine_security_group_ingress_22" {
  security_group_id = aws_security_group.fake_spine_security_group.id
  type = "ingress"
  from_port = 22
  to_port = 22
  protocol = "tcp"
  cidr_blocks = ["91.222.71.98/32"]
  description = "Allow SSH inbound from Kainos Gdansk VPN"
}

resource "aws_security_group_rule" "fake_spine_security_group_egress_Internet_443" {
  security_group_id = aws_security_group.fake_spine_security_group.id
  type = "egress"
  from_port = 443
  to_port = 443
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  description = "HTTPS connections to Internet."
}

resource "aws_security_group_rule" "fake_spine_security_group_egress_Internet_80" {
  security_group_id = aws_security_group.fake_spine_security_group.id
  type = "egress"
  from_port = 80
  to_port = 80
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
  description = "HTTPS connections to Internet."
}