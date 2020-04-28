data "template_file" "fake_spine_app_variables_template" {
  template = file("${path.module}/files/variables.sh")
  vars = {
    INBOUND_SERVER_BASE_URL         = local.mhs_inbound_url,
    FAKE_SPINE_OUTBOUND_DELAY_MS    = var.outbound_delay_ms,
    FAKE_SPINE_INBOUND_DELAY_MS     = var.inbound_delay_ms,
    FAKE_SPINE_OUTBOUND_SSL_ENABLED = var.fake_spine_outbound_ssl,
    FAKE_SPINE_PORT                 = var.fake_spine_port,
    REGION                          = var.region,
    FAKE_SPINE_PRIVATE_KEY_ARN      = var.fake_spine_private_key,
    FAKE_SPINE_CERTIFICATE_ARN      = var.fake_spine_certificate,
    FAKE_SPINE_CA_STORE_ARN         = var.fake_spine_ca_store,
    MHS_SECRET_PARTY_KEY_ARN        = var.party_key_arn
    FAKE_SPINE_PROXY_VALIDATE_CERT  = var.fake_spine_proxy_validate_cert
  }
}

data "template_file" "fake_spine_init_template" {
  template = file("${path.module}/files/cloudinit.sh")
  vars = {
    GIT_BRANCH = var.git_branch_name,
    GIT_REPO   = var.git_repo_url,
    BUILD_TAG  = var.build_id
  }
}

data "template_cloudinit_config" "fake_spine_user_data" {
  gzip          = "true"
  base64_encode = "true"

  part {
    content_type ="text/x-shellscript"
    content = data.template_file.fake_spine_app_variables_template.rendered
  }  

  part {
    content_type = "text/x-shellscript"
    content      = data.template_file.fake_spine_init_template.rendered
  }
} 