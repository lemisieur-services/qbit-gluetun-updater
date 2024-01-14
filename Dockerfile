# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Use environment variable for cron schedule
ENV QBIT_HOST= \
    QBIT_USERNAME= \
    QBIT_PASSWORD= \
    GLUETUN_FQDN= \
    GLUETUN_CTRL_PORT=

# Set the working directory in the container to /app
WORKDIR /app
ADD . /app

# Install requirements
RUN apt-get update && \
    apt-get -y install cron && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod +x /app/start.sh

# Start launch script
CMD /app/start.sh