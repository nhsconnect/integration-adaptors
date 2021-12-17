resource "aws_instance" "pss_testbox" {
  availability_zone = local.availability_zones[0]

  ami           = data.aws_ami.base_linux.id
  instance_type = "t2.micro"
  key_name = "kainos-dev"
  vpc_security_group_ids = [aws_security_group.pss_testbox_sg.id]
  subnet_id = aws_subnet.service_subnet.id[count.index]

  tags = merge(local.default_tags, {
     Name = "${local.resource_prefix}-pss_testbox"
  })
}