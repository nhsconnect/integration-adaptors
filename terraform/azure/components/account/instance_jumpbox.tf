resource "azurerm_network_interface" "account_jumpbox_nic" {
  name                = "${local.resource_prefix}-jumpbox_nic"
  resource_group_name = azurerm_resource_group.account_resource_group.name
  location            = azurerm_resource_group.account_resource_group.location

  ip_configuration {
    name                          = "vmNicConfiguration"
    subnet_id                     = azurerm_subnet.account_jumpbox_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.account_jumpbox_pip.id
  }
}

resource "azurerm_linux_virtual_machine" "account_jumpbox" {
  name                            = "${local.resource_prefix}-jumpbox"
  resource_group_name             = var.account_resource_group
  location                        = var.location
  network_interface_ids           = [ azurerm_network_interface.account_jumpbox_nic.id ]
  size                            = "Standard_DS1_v2"
  computer_name                   = "${local.resource_prefix}-jumpbox"
  admin_username                  = var.jumpbox_user
  disable_password_authentication = true

  admin_ssh_key {
    username = var.jumpbox_user
    public_key = file("files/azure_account_jumpbox.pub")
  }

  os_disk {
    name                 = "${local.resource_prefix}-jumpbox_disk"
    caching              = "ReadWrite"
    storage_account_type = var.account_jumpbox_storage_type
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  tags = merge(local.default_tags,{
    Name = "${local.resource_prefix}-jumpbox"
  })

  provisioner "remote-exec" {
    connection {
      host     = self.public_ip_address
      type     = "ssh"
      user     = var.jumpbox_user
      private_key = file(var.jumpbox_private_key_location)
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
