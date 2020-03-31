# Terraform output variable of the fake-spine load balancer's target group ARN
output "fake_spine_lb_target_group_arn" {
  value = aws_lb_target_group.fake_spine_alb_target_group.arn
  description = "The ARN of the fake-spine service load balancers's target group."
}
