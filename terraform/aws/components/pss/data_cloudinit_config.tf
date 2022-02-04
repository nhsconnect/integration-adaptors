data "template_file" "testbox_cloudinit_template" {
  template = file("${path.module}/files/pss_testbox.sh")
  vars = {}
}

data "template_cloudinit_config" "testbox_user_data" {
  gzip = true
  base64_encode = true
  part {
    content_type = "text/x-shellscript"
    content = data.template_file.testbox_cloudinit_template.rendered
  }
}
