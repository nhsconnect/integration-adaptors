import logging
import os
from pathlib import Path

from fabric import task

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.INFO)


@task
def setup_ec2_openvpn(c):
    # Install OpenVPN (note that Docker gets installed/setup by AWS ECS)
    c.sudo("yum install -y openvpn")
    logging.info("Installed OpenVPN")

    # Create up/down scripts
    for up_down in ["up.sh", "down.sh"]:
        c.put(str(Path(CURRENT_DIR) / f"openvpn-{up_down}"), remote=f"openvpn-{up_down}")
        c.run(f"sudo mv openvpn-{up_down} /etc/openvpn/{up_down}")
        c.sudo(f"chmod +x /etc/openvpn/{up_down}")

    # Add VPN config file
    vpn_conf_filename = "vpn-config.conf"
    vpn_conf_temp_filename = "vpn-config-first.conf"
    c.put(vpn_conf_filename, remote=vpn_conf_temp_filename)

    # Add up/down config to VPN config file
    extra_vpn_conf_filename = "additional-openvpn-config.conf"
    c.put(str(Path(CURRENT_DIR) / extra_vpn_conf_filename), remote=extra_vpn_conf_filename)
    c.run(
        fr"""printf '%s\n\n%s' "$(cat {extra_vpn_conf_filename})" "$(cat {vpn_conf_temp_filename})" > {vpn_conf_filename}""")
    c.sudo(f"mv {vpn_conf_filename} /etc/openvpn/{vpn_conf_filename}")

    logging.info("Configured OpenVPN")

    # Start OpenVPN
    c.sudo("service openvpn restart")
    logging.info("Started OpenVPN")

    # Start OpenVPN on server startup
    c.sudo("chkconfig --level 2345 openvpn on")
    logging.info("Set OpenVPN to be started on server startup")


@task
def setup_squid(c):
    """
    Install and configure Squid to act as a HTTP proxy for requests from MHS outbound to Spine
    """
    c.sudo("yum install -y squid")
    logging.info("Installed Squid")

    c.put(str(Path(CURRENT_DIR) / "squid.conf"), remote="squid.conf")
    c.run(f"sudo mv squid.conf /etc/squid/squid.conf")
    logging.info("Configured Squid")

    c.sudo("systemctl restart squid.service")
    logging.info("Started Squid")
    c.sudo("systemctl enable squid.service")
    logging.info("Set Squid to be started on server startup")
