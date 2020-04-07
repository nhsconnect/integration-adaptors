locals {
    fake_spine_base_environment_variables = [
    {
      name = "FAKE_SPINE_PRIVATE_KEY",
      value = "TODO"
    },
    {
      name = "FAKE_SPINE_CERTIFICATE",
      value = "TODO"
    },
    {
      name = "FAKE_SPINE_CA_STORE",
      value = "TODO"
    },
    {
      name = "INBOUND_SERVER_BASE_URL",
      value = "TODO"
    },
    {
      name = "FAKE_SPINE_OUTBOUND_DELAY_MS",
      value = "TODO"
    },
    {
      name = "FAKE_SPINE_INBOUND_DELAY_MS",
      value = "TODO"
    },
    {
      name = "MHS_SECRET_PARTY_KEY",
      //valueFrom = var.party_key_arn
      value = "TODO"
    },
  ]
}