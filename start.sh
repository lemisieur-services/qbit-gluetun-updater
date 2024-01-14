#!/bin/bash

echo "Container starting..."
echo "-----------------------------------------------------------"
echo ":: Welcome to the Qbit Gluetun Updater!"
echo ":: This container will update your qBittorent instance with the latest port forwarded by Gluetun."
echo "::"
echo ":: Here are the current settings:"
echo ":: qBittorent host: $QBIT_HOST"
echo ":: qBittorrent username: $QBIT_USERNAME"
echo ":: qBittorrent password: $QBIT_PASSWORD"
echo ":: Gluetun FQDN: $GLUETUN_FQDN"
echo ":: Gluetun control port: $GLUETUN_CTRL_PORT"
echo "-----------------------------------------------------------"
echo "For more information, please visit: https://github.com/lemisieur-services/qbit-gluetun-updater"
echo "Have fun!"
echo "-----------------------------------------------------------"
echo ""

while true; do python /app/updater.py; sleep 60; done

echo "Container stopped."