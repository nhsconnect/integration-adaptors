data "template_file" "jumpbox_cloudinit_template" {
  template = file("${path.module}/files/jumpbox.sh")
  vars = {}
}

data "template_cloudinit_config" "jumpbox_user_data" {
  gzip = true
  base64_encode = true
  part {
    content_type = "text/x-shellscript"
    content = data.template_file.jumpbox_cloudinit_template.rendered
  }
}
