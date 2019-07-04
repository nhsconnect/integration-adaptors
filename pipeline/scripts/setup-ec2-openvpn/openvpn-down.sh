#!/bin/sh
# Copyright (c) 2007-2008 Roy Marples <roy@marples.name>
# Amended by Kristian Gunstone for manjaro-openrc
# Released under the 2-clause BSD license.

export RC_SERVICE=/etc/init.d/$SVCNAME
export RC_SVCNAME=$SVCNAME
# If we have a service specific script, run this now
[ -x "${RC_SVCNAME}"-down.sh ] && "${RC_SVCNAME}"-down.sh

# Restore resolv.conf to how it was
if type resolvconf >/dev/null 2>&1; then
    resolvconf -d "${dev}"
elif [ -e /etc/resolv.conf-"${dev}".sv ]; then
    # Important that we copy instead of move incase resolv.conf is
    # a symlink and not an actual file
    cp -p /etc/resolv.conf-"${dev}".sv /etc/resolv.conf
    rm -f /etc/resolv.conf-"${dev}".sv
fi

# Re-enter the init script to stop any dependant services
if [ -x "${RC_SERVICE}" ]; then
    if "${RC_SERVICE}" --quiet status; then
        export IN_BACKGROUND=YES
        "${RC_SERVICE}" --quiet stop
    fi
fi

exit 0
# File taken from https://gist.github.com/gammy/b821ff02abfb23d0e41524f96d8a1b0a
