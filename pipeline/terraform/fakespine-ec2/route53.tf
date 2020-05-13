# Route53 DNS record that is a domain name pointing to the fake spine load balancer
resource "aws_route53_record" "fake_spine_load_balancer_record" {
  zone_id = data.terraform_remote_state.mhs.outputs.mhs_hosted_zone_id
  name    = "fakespine.${data.terraform_remote_state.mhs.outputs.mhs_hosted_zone_name}"
  type    = "A"
  # ttl     = 300
  # records = [ aws_instance.fake_spine_instance.private_ip ]
 
  alias {
    name = aws_lb.fake_spine_load_balancer.dns_name
    zone_id = aws_lb.fake_spine_load_balancer.zone_id
    evaluate_target_health = false
  }
}
