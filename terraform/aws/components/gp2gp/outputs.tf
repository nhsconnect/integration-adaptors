output "gp2gp_url" {
  value = aws_route53_record.gp2gp_lb_record.name
  description = "The DNS name of the Route53 record pointing to the gp2gp service's load balancer."
}

output "gp2gp_lb_sg_id" {
  value = module.gp2gp_ecs_service.loadbalancer_sg_id
  description = "Security Group ID for gp2gp load balancer, use it create rules to allow other components to connect"
}
# TODO - In case of chicken and egg situation - cross dependency between components - create SG and rules in base components and supply the SG IDs to componnets and ECS modules

output "gp2gp_lb_port" {
  value = var.gp2gp_service_application_port
  description = "Port on which gp2gp LB is listening"
}

output "gp2gp_lb_arn" {
  value =  module.gp2gp_ecs_service.loadbalancer_arn
  description = "ARN of Service loadbalancer"
}

output "gp2gp_lb_target_group_arn" {
  value =  module.gp2gp_ecs_service.loadbalancer_tg_arn
  description = "ARN of Service loadbalancers target group"
}
