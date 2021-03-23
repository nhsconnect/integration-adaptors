data "aws_mq_broker" "gpc-consumer_mq_broker" {
  broker_name = var.mq_broker_name
}