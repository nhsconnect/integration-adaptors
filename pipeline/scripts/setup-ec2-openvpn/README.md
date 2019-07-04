# EC2 OpenVPN Setup Script

This is a Fabric script that can be used to setup an EC2 instance (specifically, one that has been created by ECS) with an OpenVPN connection.

Usage:
- `pipenv install`
- Make sure that you have an ovpn file called `vpn-config.conf` in this folder.
- `pipenv run fab -i ssh_key_file -H user@address setup-ec2-openvpn`
  - Note that `user` must have sudo access.
