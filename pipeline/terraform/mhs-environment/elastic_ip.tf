resource "aws_eip" "inbound_lb_eip" { 
  vpc = true
  associate_with_private_ip = "10.239.66.139" # Resolves to http://test1-x26.nhsdnia.thirdparty.nhs.uk/ in NHS DNS - our assigned adress
}
