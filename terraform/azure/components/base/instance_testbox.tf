resource "azurerm_network_interface" "base_testbox_nic" {
  name                = "${local.resource_prefix}-testbox_nic"
  resource_group_name = data.terraform_remote_state.account.outputs.resource_group_name
  location            = data.terraform_remote_state.account.outputs.resource_group_location

  ip_configuration {
    name                          = "vmNicConfiguration"
    subnet_id                     = azurerm_subnet.base_testbox_subnet.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_linux_virtual_machine" "base_testbox" {
  name                            = "${local.resource_prefix}-testbox"
  resource_group_name = data.terraform_remote_state.account.outputs.resource_group_name
  location            = data.terraform_remote_state.account.outputs.resource_group_location
  network_interface_ids           = [ azurerm_network_interface.base_testbox_nic.id ]
  size                            = "Standard_DS1_v2"
  computer_name                   = "${local.resource_prefix}-testbox"
  admin_username                  = var.jumpbox_user
  disable_password_authentication = true

  admin_ssh_key {
    username = var.jumpbox_user
    public_key = file("../account/files/azure_account_jumpbox.pub")
  }

  os_disk {
    name                 = "${local.resource_prefix}-testbox_disk"
    caching              = "ReadWrite"
    storage_account_type = var.base_testbox_storage_type
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-testbox"
  })

  provisioner "remote-exec" {
    connection {
      host     = self.private_ip_address
      type     = "ssh"
      user     = var.jumpbox_user
      private_key = file(var.jumpbox_private_key_location)
      bastion_host = data.terraform_remote_state.account.outputs.jumpbox_ip
      bastion_user = var.jumpbox_user
      bastion_private_key = file(var.jumpbox_private_key_location)
    }

    inline = [
      "sudo apt-get update && sudo apt-get install -y apt-transport-https gnupg2",
      "curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -",
      "echo 'deb https://apt.kubernetes.io/ kubernetes-xenial main' | sudo tee -a /etc/apt/sources.list.d/kubernetes.list",
      "sudo apt-get update",
      "sudo apt-get install -y kubectl",
      "curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    ]
  }
}
