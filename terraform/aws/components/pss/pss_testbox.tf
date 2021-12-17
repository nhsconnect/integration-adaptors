resource "aws_instance" "pss_testbox" {
  availability_zone = local.availability_zones[0]

  ami           = data.aws_ami.base_linux.id
  instance_type = "t2.micro"
  host_id  = "pss_testbox"
  key_name = "pss_testbox"
  vpc_security_group_ids = [aws_security_group.pss_testbox_sg.id]
  subnet_id = aws_subnet.service_subnet[0].id

  tags = merge(local.default_tags, {
     Name = "${local.resource_prefix}-pss_testbox"
  })
}