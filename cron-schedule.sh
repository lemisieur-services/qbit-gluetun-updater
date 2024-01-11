#!/bin/bash

# Define environment variables
echo "export CRON_SCHEDULE=\"$CRON_SCHEDULE\"" >> /tmp/.env
echo "export QBIT_HOST=\"$QBIT_HOST\"" >> /tmp/.env
echo "export QBIT_USERNAME=\"$QBIT_USERNAME\"" >> /tmp/.env
echo "export QBIT_PASSWORD=\"$QBIT_PASSWORD\"" >> /tmp/.env
echo "export GLUETUN_FQDN=\"$GLUETUN_FQDN"\" >> /tmp/.env
echo "export GLUETUN_CTRL_PORT=\"$GLUETUN_CTRL_PORT\"" >> /tmp/.env

# Define the cron job
CRON_JOB="$CRON_SCHEDULE source /tmp/.env && /usr/local/bin/python /app/updater.py >> /var/log/cron.log 2>&1"

# Add the cron job to the crontab
echo "$CRON_JOB" | crontab -