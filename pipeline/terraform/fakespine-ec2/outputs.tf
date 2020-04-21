output "instance_private_ip" {
  value = aws_instance.fake_spine_instance.private_ip
}

output "instance_public_ip" {
  value = aws_instance.fake_spine_instance.public_ip
}

output "instance_public_hostname" {
  value = aws_instance.fake_spine_instance.public_dns
}

output "instance_private_R53_record" {
  value = aws_route53_record.fake_spine_load_balancer_record.fqdn
}