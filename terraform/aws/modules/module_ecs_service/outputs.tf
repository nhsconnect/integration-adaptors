output "loadbalancer_sg_id" {
  value =  var.enable_load_balancing ? aws_security_group.service_lb_sg.id : null
}

output "service_sg_id" {
  value =  aws_security_group.service_sg.id
}

output "loadbalancer_dns_name" {
  value =  var.enable_load_balancing ? aws_lb.service_load_balancer[0].dns_name : null
}

output "loadbalancer_zone_id" {
  value =  var.enable_load_balancing ? aws_lb.service_load_balancer[0].zone_id : null
}

output "loadbalancer_arn" {
  value =  var.enable_load_balancing ? aws_lb.service_load_balancer[0].arn : null
  description = "ARN of Service loadbalancer"
}

output "loadbalancer_tg_arn" {
  value =  var.enable_load_balancing ? aws_lb_target_group.service_target_group[0].arn : null
  description = "ARN of Service loadbalancers target group"
}

output "cloudwatch_log_group" {
  value = aws_cloudwatch_log_group.ecs_service_cw_log_group.name
  description = "Cloudwatch log group for logs from the service"
}

output "testbox_hostname" {
    value = var.create_testbox ? aws_instance.testbox[0].private_dns : null
}
