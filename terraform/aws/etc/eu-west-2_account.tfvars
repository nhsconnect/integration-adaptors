ecr_repositories = [
  {
    name = "OneOneOne",
    scan = false,
    expire_PR_after = 14,
    prefix_to_keep  = "master",
    number_to_keep  = 10
  },
  # {
  #   name = "nhais",
  #   scan = false,
  #   expire_PR_after = 14,
  #   prefix_to_keep = "develop"
  #   number_to_keep = 10
  # },
]