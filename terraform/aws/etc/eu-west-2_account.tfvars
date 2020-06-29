ecr_repositories = [
  {
    name = "111",
    scan = false,
    expire_PR_after = 10,
    prefix_to_keep  = "master",
    number_to_keep  = 10
  },
  # {
  #   name = "nhais",
  #   scan = false,
  #   expire_PR_after = 10,
  #   prefix_to_keep = "develop"
  #   number_to_keep = 10
  # },
]

account_cidr_block = "10.10.0.0/16"

jumpbox_allowed_ssh = [
  "91.222.71.98/32",   # Gdansk VPN
  "195.89.171.5/32",   # Belfast Office
  "62.254.63.50/32",   # Belfast VPN #1
  "62.254.63.52/32"    # Belfast VPN #2
]
