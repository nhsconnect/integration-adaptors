resource "aws_autoscaling_group" "jumpbox" {
  name = "${local.resource_prefix}-jmp_asg"
  max_size = 1
  min_size = 0
  desired_capacity = 1
  launch_template {
    id = aws_launch_template.jumpbox_lt.id
    version = "$Latest"
  }
  //role_arn = "TODO"
  availability_zones = local.availability_zones

  # tags = merge(local.default_tags, {
  #   Name = "${local.resource_prefix}-jmp_asg"
  # })
}

resource "aws_launch_template" "jumpbox_lt" {
  name_prefix = "${local.resource_prefix}-jmp_lt"
  image_id = data.aws_ami.base_linux.id
  instance_type = "t2.micro"
  key_name = "kainos-dev"
  iam_instance_profile {
    name = "TerraformJumpboxRole"
  }
  network_interfaces {
    associate_public_ip_address = true
    delete_on_termination = true
    security_groups = [aws_security_group.jumpbox_sg.id]
    subnet_id = aws_subnet.public_subnet.id
  }
  //vpc_security_group_ids = []
  user_data = data.template_cloudinit_config.jumpbox_user_data.rendered
  tag_specifications {
    resource_type = "instance"
    tags = merge(local.default_tags, {
      Name = "${local.resource_prefix}-jmp_asg"
    })
  }
}

# resource "aws_autoscaling_schedule" "jumpbox_schedule" {
#   scheduled_action_name = "COB shutdown"
#   autoscaling_group_name = aws_autoscaling_group.jumpbox.name
#   min_size = 0
#   max_size = 1
#   desired_capacity = 0
#   start_time = "TODO"
#   end_time = "TODO"
#   recurrence = "TODO"
# }

# resource "aws_autoscaling_schedule" "jumpbox_schedule" {
#   scheduled_action_name = "SOB startup"
#   autoscaling_group_name = aws_autoscaling_group.jumpbox.name
#   min_size = 0
#   max_size = 1
#   desired_capacity = 1
#   start_time = "TODO"
#   end_time = "TODO"
#   recurrence = "TODO"
# }
