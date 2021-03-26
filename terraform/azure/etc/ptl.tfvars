environment          = "ptl"
base_cidr            = "10.22.0.0/16"
ptl_cidr             = "172.28.65.0/24"
ptl_connected        = true
base_aks_cidr        = "172.28.65.128/25"
base_ptl_next_hop    = "172.17.166.116"
base_ptl_prefixes    = [ "172.17.0.0/16", "155.231.231.0/29", "10.239.0.0/16" ]
base_ptl_dns_servers = [ "155.231.231.1", "155.231.231.2" ]
base_redis_cidr      = "10.22.101.0/24"
base_testbox_cidr    = "172.28.65.0/26"

# variable "N3_next_hop" {
#   default = "172.17.166.116"
# }

# variable "N3_prefixes" {
#   default = [
#     "172.17.0.0/16",
#     "155.231.231.0/29", # for DNS 155.231.231.1 155.231.231.2
#     "10.239.0.0/16"
#   ]
# }

# variable "N3_dns_servers" {
#   default = [ "155.231.231.1", "155.231.231.2" ]
# }

# variable "mhs_vnet_cidr" {
#   default = "172.28.65.0/24"
