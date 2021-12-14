data "aws_mq_broker" "pss_mq_broker" {
  broker_name = var.mq_broker_name
}

data "aws_mq_broker" "mhs_mq_broker" {
  broker_name = var.mq_broker_name
}