output "mhs_outbound_url" {
  value = aws_route53_record.mhs_outbound_lb_record.name
  description = "The DNS name of the Route53 record pointing to the mhs service's load balancer."
}

output "mhs_outboubound_lb_sg_id" {
  value = module.mhs_outbound_ecs_service.loadbalancer_sg_id
  description = "Security Group ID for mhs load balancer, use it create rules to allow other components to connect"
}
# TODO - In case of chicken and egg situation - cross dependency between components - create SG and rules in base components and supply the SG IDs to componnets and ECS modules

output "mhs_outbout_lb_port" {
  value = var.mhs_service_application_port
  description = "Port on which mhs LB is listening"
}

output "mhs_outbound_lb_arn" {
  value =  module.mhs_outbound_ecs_service.loadbalancer_arn
  description = "ARN of Service loadbalancer"
}

output "mhs_outbound_lb_target_group_arn" {
  value =  module.mhs_outbound_ecs_service.loadbalancer_tg_arn
  description = "ARN of Service loadbalancers target group"
}
