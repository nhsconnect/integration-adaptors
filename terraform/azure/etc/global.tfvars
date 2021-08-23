project = "nia"
location = "UK West"

state_bucket_resource_group  = "nia-state-rg"
state_bucket_storage_account = "niastate"
state_bucket_name = "nia-state-container"

account_resource_group = "nia-rg"
account_bucket_storage_account = "niaaccount"

jumpbox_allowed_ips = [
  "91.222.71.98/32",   # Gdansk VPN
  "195.89.171.5/32",   # Belfast Office
  "62.254.63.50/32",   # Belfast VPN #1
  "62.254.63.52/32"    # Belfast VPN #2
]