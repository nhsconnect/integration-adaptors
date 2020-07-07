locals {
  default_tags = {
    Project = var.project
    Environment = var.environment
    Component = var.component
  }

  resource_prefix = "${var.project}-${var.environment}-${var.component}"
  availability_zones = ["${var.region}a", "${var.region}b", "${var.region}c"]
  ptl_lb_availability_zones = ["${var.region}a", "${var.region}b"]

# The minimal size for aws subnet is /28 - 14 hosts
# We need at least two of these for inbound load balancer
# We have to make sure that the assigned ip is always available to the Inbound Load Balancer
# For Inbound LB
# cidrsubnet("10.x.x.128/25",3,0) # 10.x.x.128/28 # zone a
# cidrsubnet("10.x.x.128/25",3,1) # 10.x.x.144/28 # zone b
# For everything else
# cidrsubnet("10.x.x.128/25",2,1) # 10.x.x.160/27 # zone a
# cidrsubnet("10.x.x.128/25",2,2) # 10.x.x.192/27 # zone b
# cidrsubnet("10.x.x.128/25",2,3) # 10.x.x.224/27 # zone c

  ptl_lb_subnet_cidrs = [
    cidrsubnet(var.ptl_assigned_cidr,3,0),
    cidrsubnet(var.ptl_assigned_cidr,3,1)
  ]

  ptl_containers_subnet_cidrs = [
    cidrsubnet(var.ptl_assigned_cidr,2,1),
    cidrsubnet(var.ptl_assigned_cidr,2,2),
    cidrsubnet(var.ptl_assigned_cidr,2,3)
  ]
}
