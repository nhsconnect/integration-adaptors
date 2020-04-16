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

resource "aws_instance_profile" "fake_spine_instance_profile" {
 name = "${var.environment_id}-fake_spine_instance_profile"
 role = aws_iam_role.fake_spine_iam_role.name
}

resource "aws_iam_role" "fake_spine_iam_role" {
  name = "${var.environment_id}-iam_role"
  assume_role_policy = data.aws_iam_policy_document.fake_spine_assume_role.json
}

data "aws_iam_policy_document" "fake_spine_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "fs_role_S3" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  role       = aws_iam_role.fake_spine_iam_role.name
}

resource "aws_iam_role_policy_attachment" "fs_role_Secrets" {
  policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
  role       = aws_iam_role.fake_spine_iam_role.name
}

resource "aws_iam_role_policy_attachment" "fs_role_ECR" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
  role       = aws_iam_role.fake_spine_iam_role.name
}

resource "aws_iam_role_policy_attachment" "fs_role_CW" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
  role       = aws_iam_role.fake_spine_iam_role.name
}

resource "aws_instance" "fake_spine_instance" {
  count = locals.deploy_to_ec2 ? 1 : 0
  ami = data.aws_ami.base_linux.id
  instance_type = "t2.micro"
  key_name = "kainos-dev"
  security_groups = [aws_security_group.fake_spine_security_group.id]
  subnet_id = data.terraform_remote_state.mhs.outputs.subnet_ids[0]
  associate_public_ip_adress = true
  availability_zone = "eu-west-2a"

  iam_instance_profile = aws_instance_profile.fake_spine_instance_profile.name

  user_data = data.template_cloudinit_config.fake_spine_user_data.rendered

  tags = {
    EnvironmentId = var.environment_id
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