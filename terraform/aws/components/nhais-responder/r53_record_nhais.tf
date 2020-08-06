resource "aws_route53_record" "nhais-responder_lb_record" {
  zone_id = data.terraform_remote_state.base.outputs.r53_zone_id
  name = "nhais-responder.${data.terraform_remote_state.base.outputs.r53_zone_name}"
  type = "A"

  alias {
    name    = module.nhais-responder_ecs_service.loadbalancer_dns_name
    zone_id = module.nhais-responder_ecs_service.loadbalancer_zone_id
    evaluate_target_health = false
  }
}
