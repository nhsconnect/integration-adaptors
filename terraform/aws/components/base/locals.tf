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
# but with icreasing number of adapters, we need more ips for LBs
# as when adding a new LB, at least 8 free adresses have to remain
# We need at least two of these for inbound load balancer
# We have to make sure that the assigned ip is always available to the Inbound Load Balancer
# For Inbound LB
# cidrsubnet("10.x.x.128/25",2,0) # 10.x.x.128/27 # zone a
# cidrsubnet("10.x.x.128/25",2,1) # 10.x.x.160/27 # zone b
# For everything else
# cidrsubnet("10.x.x.128/25",2,2) # 10.x.x.192/27 # zone a
# cidrsubnet("10.x.x.128/25",2,3) # 10.x.x.224/27 # zone b

  ptl_lb_subnet_cidrs = var.ptl_connected ? [
    cidrsubnet(var.ptl_assigned_cidr,2,0),
    cidrsubnet(var.ptl_assigned_cidr,2,1)
  ] : []

  ptl_containers_subnet_cidrs = var.ptl_connected ? [
    cidrsubnet(var.ptl_assigned_cidr,2,2),
    cidrsubnet(var.ptl_assigned_cidr,2,3),
  ] : []
}
