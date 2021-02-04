resource "azurerm_network_interface" "base_jumpbox_nic" {
  name                = "${local.resource_prefix}-jumpbox_nic"
  resource_group_name = var.account_resource_group
  location            = var.location

  ip_configuration {
    name                          = "vmNicConfiguration"
    subnet_id                     = azurerm_subnet.base_jumpbox_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.base_jumpbox_pip.id
  }
}

resource "azurerm_linux_virtual_machine" "base_jumpbox" {
  name                            = "${local.resource_prefix}-jumpbox"
  resource_group_name             = var.account_resource_group
  location                        = var.location
  network_interface_ids           = [ azurerm_network_interface.base_jumpbox_nic.id ]
  size                            = "Standard_DS1_v2"
  computer_name                   = "${local.resource_prefix}-jumpbox"
  admin_username                  = var.jumpbox_user
  admin_password                  = random_password.adminpassword.result
  #disable_password_authentication = true
  disable_password_authentication = false

  admin_ssh_key {
    username = var.jumpbox_user
    public_key = file("files/azure_base_jumpbox.pub")
  }

  os_disk {
    name                 = "${local.resource_prefix}-jumpbox_disk"
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
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

  # provisioner "remote-exec" {
  #   connection {
  #     host     = self.public_ip_address
  #     type     = "ssh"
  #     user     = var.jumpbox_user
  #     private_key = file("~/.ssh/azure_mhs_jumpbox")
  #   }

  #   inline = [
  #     "sudo apt-get update && sudo apt-get install -y apt-transport-https gnupg2",
  #     "curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -",
  #     "echo 'deb https://apt.kubernetes.io/ kubernetes-xenial main' | sudo tee -a /etc/apt/sources.list.d/kubernetes.list",
  #     "sudo apt-get update",
  #     "sudo apt-get install -y kubectl",
  #     "curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
  #   ]
  # }
}

resource "random_password" "adminpassword" {
  keepers = {
    resource_group = var.account_resource_group
  }

  length      = 25
  min_lower   = 2
  min_upper   = 2
  min_numeric = 2
}

output "jumpbox_password" {
  description = "Jumpbox VM admin password"
  value       = random_password.adminpassword.result
}
