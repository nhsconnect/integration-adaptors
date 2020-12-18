output "OneOneOne_url" {
  value = aws_route53_record.OneOneOne_lb_record.name
  description = "The DNS name of the Route53 record pointing to the OneOneOne service's load balancer."
}

output "OneOneOne_lb_sg_id" {
  value = module.OneOneOne_ecs_service.loadbalancer_sg_id
  description = "Security Group ID for OneOneOne load balancer, use it create rules to allow other components to connect"
}
# TODO - In case of chicken and egg situation - cross dependency between components - create SG and rules in base components and supply the SG IDs to componnets and ECS modules

output "OneOneOne_lb_port" {
  value = var.OneOneOne_service_application_port
  description = "Port on which OneOneOne LB is listening"
}

output "OneOneOne_lb_arn" {
  value =  module.OneOneOne_ecs_service.loadbalancer_arn
  description = "ARN of Service loadbalancer"
}

output "OneOneOne_lb_target_group_arn" {
  value =  module.OneOneOne_ecs_service.loadbalancer_tg_arn
  description = "ARN of Service loadbalancers target group"
}
