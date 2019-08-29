resource "aws_security_group" "mhs_outbound_security_group" {
  name = "MHS Outbound Security Group"
  description = "The security group used to control traffic for the MHS Outbound component."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-mhs-outbound-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "mhs_route_security_group" {
  name = "MHS Route Security Group"
  description = "The security group used to control traffic for the MHS Routing component."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-mhs-route-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "mhs_inbound_security_group" {
  name = "MHS Inbound Security Group"
  description = "The security group used to control traffic for the MHS Inbound component."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-mhs-inbound-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "dynamo_db_security_group" {
  name = "DynamoDB Security Group"
  description = "The security group used to control traffic for the DynamoDB endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-dynamo-db-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "sds_cache_security_group" {
  name = "SDS Cache Security Group"
  description = "The security group used to control traffic for the SDS cache endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-sds-cache-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "alb_outbound_security_group" {
  name = "Outbound ALB Security Group"
  description = "The security group used to control traffic for the outbound MHS Application Load Balancer."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-alb-outbound-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "alb_route_security_group" {
  name = "Route ALB Security Group"
  description = "The security group used to control traffic for the MHS routing component Application Load Balancer."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-alb-route-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "alb_inbound_security_group" {
  name = "Inbound ALB Security Group"
  description = "The security group used to control traffic for the inbound MHS Application Load Balancer."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-alb-inbound-sg"
    BuildId = var.build_id
  }
}

resource "aws_security_group" "async_response_queue_security_group" {
  name = "Async Response Queue Security Group"
  description = "The security group used to control traffic for the asynchronous response queue endpoint."
  vpc_id = aws_vpc.mhs_vpc.id

  tags = {
    Name = "${var.build_id}-async-response-queue-sg"
    BuildId = var.build_id
  }
}
