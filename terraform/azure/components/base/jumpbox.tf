resource "azurerm_public_ip" "nia_jumpbox_pip" {
  name                = "nia_jumpbox_pip"
  resource_group_name             = azurerm_resource_group.nia_base.name
  location                        = azurerm_resource_group.nia_base.location
  allocation_method   = "Dynamic"
}

resource "azurerm_network_security_group" "jumpbox_sg" {
  name                = "jumpbox_sg"
  resource_group_name             = azurerm_resource_group.nia_base.name
  location                        = azurerm_resource_group.nia_base.location
}

resource "azurerm_network_security_rule" "SSH" {
    name                        = "SSH"
    priority                    = 1001
    direction                   = "Inbound"
    access                      = "Allow"
    protocol                    = "Tcp"
    source_port_range           = "*"
    destination_port_range      = "22"
    source_address_prefixes     = var.secret_jumpbox_allowed_ips
    destination_address_prefix  = "*"
    resource_group_name         = azurerm_resource_group.nia_base.name
    network_security_group_name = azurerm_network_security_group.jumpbox_sg.name
}

resource "azurerm_network_interface" "jumpbox_nic" {
  name                = "jumpbox-nic"
  resource_group_name             = azurerm_resource_group.nia_base.name
  location                        = azurerm_resource_group.nia_base.location

  ip_configuration {
    name                          = "vmNicConfiguration"
    subnet_id                     = azurerm_subnet.nia_jumpbox_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.nia_jumpbox_pip.id
  }
}

resource "azurerm_network_interface_security_group_association" "sg_association" {
  network_interface_id      = azurerm_network_interface.jumpbox_nic.id
  network_security_group_id = azurerm_network_security_group.jumpbox_sg.id
}


resource "azurerm_linux_virtual_machine" "nia_jumpbox" {
  name                            = "nia_jumpbox"
  resource_group_name             = azurerm_resource_group.nia_base.name
  location                        = azurerm_resource_group.nia_base.location
  network_interface_ids           = [azurerm_network_interface.jumpbox_nic.id]
  size                            = "Standard_DS1_v2"
  computer_name                   = "jumpboxvm"
  admin_username                  = var.jumpbox_user
  disable_password_authentication = true

  admin_ssh_key {
    username = var.jumpbox_user
    public_key = file("../files/admin_ssh_key.pub")
  }

  os_disk {
    name                 = "jumpboxOsDisk"
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  provisioner "remote-exec" {
    connection {
      host     = self.public_ip_address
      type     = "ssh"
      user     = var.jumpbox_user
      private_key = file("~/.ssh/azure_mhs_jumpbox")
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

output "jumpbox_ip" {
  description = "Jumpbox VM IP"
  value       = azurerm_linux_virtual_machine.nia_jumpbox.public_ip_address
}

output "jumpbox_username" {
  description = "Jumpbox VM username"
  value       = var.jumpbox_user
}

output "jumpbox_connect" {
  description = "Command for connecting to jumpbox"
  value = "ssh ${var.jumpbox_user}@${azurerm_linux_virtual_machine.nia_jumpbox.public_ip_address} -i ~/.ssh/azure_mhs_jumpbox"
}