region = "eu-west-2"
project = "nia"
account_id = "067756640211"

mq_broker_name = "nia-broker"
root_domain = "nhsredteam.internal.nhs.uk"

enable_dlt = false
opentest_vpc_id = "vpc-05df0513605dcbd32"
opentest_sg_id = "sg-02dce579551a289dc"
opentest_instance_id = "i-0c3796a9a8e712b69"
jenkins_worker_sg_id = "sg-09d9fdae9d92acce9"

jumpbox_allowed_ssh = [
 "82.28.74.154/32", # Answer digital VPN
 "20.68.179.45/32" # Made Tech VPN
]
