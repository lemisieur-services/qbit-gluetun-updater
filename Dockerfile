# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Use environment variable for cron schedule
ENV CRON_SCHEDULE="* * * * *" \
    QBIT_HOST= \
    QBIT_USERNAME= \
    QBIT_PASSWORD= \
    GLUETUN_FQDN= \
    GLUETUN_CTRL_PORT=

# Set the working directory in the container to /app
WORKDIR /app
ADD . /app

# Copy the cron job script to the container
COPY cron-schedule.sh /tmp/cron-schedule.sh

# Install requirements
RUN apt-get update && \
    apt-get -y install cron && \
    pip install --no-cache-dir -r requirements.txt && \
    touch /var/log/cron.log && \
    chmod +x /tmp/cron-schedule.sh

# Inject cron job & run the command on container startup
CMD /tmp/cron-schedule.sh && cron && tail -f /var/log/cron.log