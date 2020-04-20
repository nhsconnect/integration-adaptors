# # Uncomment this for creating EC2 ASG for use with ECS cluster
# resource "aws_autoscaling_group" "ecs-autoscaling-group" {
#   name = "ec2-ecs-asg"
#   max_size = 3
#   min_size = 1
#   desired_capacity = 1
#   vpc_zone_identifier  = data.terraform_remote_state.mhs.outputs.subnet_ids
#   launch_configuration = aws_launch_configuration.ecs-launch-configuration.name
#   health_check_type    = "ELB"
# }

# resource "aws_launch_configuration" "ecs-launch-configuration" {
#     name                        = "ec2-ecs-lc"
#     image_id                    = "${var.image-id}"
#     instance_type               = "t2.micro"
#     iam_instance_profile        = "${var.ecs-instance-profile-name}" 
#     security_groups             = ["${var.security-group-id}"]
#     associate_public_ip_address = "true"
#     key_name                    = "kainos-dev"
#     user_data                   = "${template_file.ecs-launch-configuration-user-data.rendered}"
# }

# resource "template_file" "ecs-launch-configuration-user-data" {
#     template = "${file("${path.module}/user-data.tpl")}"

#     vars {
#         ecs-cluster-name = "${var.ecs-cluster-name}"
#     }
# }