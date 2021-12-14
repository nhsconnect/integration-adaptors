resource "aws_db_parameter_group" "postgres_base_parameter" {
  name   = "${replace(local.resource_prefix,"_","-")}-postgres-parameters"
  family = "postgres13"

  /*parameter {
    name  = "ssl_min_protocol_version"
    value = "ssl_postgres_protocol"
  }*/


  tags = merge(local.default_tags,{
    Name = "${replace(local.resource_prefix,"_","-")}-postgres-parameters-36"
  })
}