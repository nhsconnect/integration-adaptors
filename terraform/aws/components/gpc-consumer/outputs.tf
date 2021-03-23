output "gpc-consumer_url" {
  value = aws_route53_record.gpc-consumer_lb_record.name
  description = "The DNS name of the Route53 record pointing to the GPC-CONSUMER service's load balancer."
}

output "gpc-consumer_lb_sg_id" {
  value = module.gpc-consumer_ecs_service.loadbalancer_sg_id
  description = "Security Group ID for GPC-CONSUMER load balancer, use it create rules to allow other components to connect"
}
# TODO - In case of chicken and egg situation - cross dependency between components - create SG and rules in base components and supply the SG IDs to components and ECS modules

output "gpc-consumer_lb_port" {
  value = var.gpc-consumer_service_application_port
  description = "Port on which GPC-CONSUMER LB is listening"
}

output "gpc-consumer_lb_arn" {
  value =  module.gpc-consumer_ecs_service.loadbalancer_arn
  description = "ARN of Service loadbalancer"
}

output "gpc-consumer_lb_target_group_arn" {
  value =  module.gpc-consumer_ecs_service.loadbalancer_tg_arn
  description = "ARN of Service loadbalancers target group"
}

output "gpc-consumer_external_access_sg_id" {
  value = aws_security_group.gpc-consumer_external_access.id
  description = "ID of the security group allowing GPC-CONSUMER to call other services"
}

output "gpc-consumer_service_subnets" {
  value = aws_subnet.service_subnet.*.id
  description = "Subnets used by GPC-CONSUMER service"
}