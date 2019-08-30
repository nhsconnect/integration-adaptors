resource "aws_vpc_endpoint" "dynamodb_endpoint" {
  vpc_id = aws_vpc.mhs_vpc.id
  service_name = "com.amazonaws.${var.region}.dynamodb"

  tags = {
    Name = "${var.build_id}-dynamodb-endpoint"
    BuildId = var.build_id
  }
}

resource "aws_vpc_endpoint_route_table_association" "example" {
  route_table_id = aws_vpc.mhs_vpc.main_route_table_id
  vpc_endpoint_id = aws_vpc_endpoint.dynamodb_endpoint.id
}
