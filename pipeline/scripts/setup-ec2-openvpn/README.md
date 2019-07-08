# EC2 OpenVPN Setup Script

This is a [Fabric](https://www.fabfile.org/) script that can be used to setup an EC2 instance (specifically, one that has been created by ECS) with an OpenVPN connection.

Usage:
- `pipenv install`
- Make sure that you have an ovpn file called `vpn-config.conf` in this folder.
- Make sure that `openvpn-up.sh` and `openvpn-down.sh` have Linux-style line endings, not Windows-style, otherwise the VPN connection won't get setup properly.
- `pipenv run fab -i ssh_key_file -H user@address setup-ec2-openvpn`
  - Note that `user` must have sudo access.
  - This script should be fairly safe to run multiple times.
