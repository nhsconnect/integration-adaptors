resource "aws_docdb_cluster_instance" "nhais_db_instance" {
  count = var.docdb_instance_count
  identifier         = "${replace(local.resource_prefix,"_","-")}-dbinstance-${count.index}"
  cluster_identifier = aws_docdb_cluster.nhais_db_cluster.id
  instance_class     = var.docdb_instance_class
  apply_immediately  = true
  availability_zone  = local.availability_zones[ count.index ]
  
  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-dbinstance-${count.index}"
  })
}