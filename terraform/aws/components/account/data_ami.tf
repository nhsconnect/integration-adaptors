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
