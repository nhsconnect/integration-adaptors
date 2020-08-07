resource "aws_route53_record" "nhais_responder_lb_record" {
  zone_id = data.terraform_remote_state.base.outputs.r53_zone_id
  name = "nhais_responder.${data.terraform_remote_state.base.outputs.r53_zone_name}"
  type = "A"

  alias {
    name    = module.nhais_responder_ecs_service.loadbalancer_dns_name
    zone_id = module.nhais_responder_ecs_service.loadbalancer_zone_id
    evaluate_target_health = false
  }
}
