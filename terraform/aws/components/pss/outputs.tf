output "pss_url" {
  value = aws_route53_record.pss_lb_record.name
  description = "The DNS name of the Route53 record pointing to the pss service's load balancer."
}

output "pss_lb_sg_id" {
  value = module.pss_ecs_service.loadbalancer_sg_id
  description = "Security Group ID for pss load balancer, use it create rules to allow other components to connect"
}
# TODO - In case of chicken and egg situation - cross dependency between components - create SG and rules in base components and supply the SG IDs to components and ECS modules

output "pss_lb_port" {
  value = var.pss_service_application_port
  description = "Port on which pss LB is listening"
}

output "pss_lb_arn" {
  value =  module.pss_ecs_service.loadbalancer_arn
  description = "ARN of Service loadbalancer"
}

output "pss_lb_target_group_arn" {
  value =  module.pss_ecs_service.loadbalancer_tg_arn
  description = "ARN of Service loadbalancers target group"
}

output "pss_external_access_sg_id" {
  value = aws_security_group.pss_external_access.id
  description = "ID of the security group allowing pss to call other services"
}

output "pss_service_subnets" {
  value = aws_subnet.service_subnet.*.id
  description = "Subnets used by pss service"
}
