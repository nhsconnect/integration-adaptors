#!/bin/bash -e

if [ -z "${DNS_SERVER_1}" ]; then
  echo "DNS_SERVER_1 must be set"
  exit 1;
fi

if [ -z "${DNS_SERVER_2}" ]; then
  echo "DNS_SERVER_2 must be set"
  exit 1;
fi

cat << EOF > /etc/resolv.conf
nameserver ${DNS_SERVER_1}
nameserver ${DNS_SERVER_2}
EOF

# Run anything passed as arguments
$@
