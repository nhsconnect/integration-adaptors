FROM python:3.7-slim as base

RUN apt-get update && \
    apt-get install build-essential libcurl4-openssl-dev libssl-dev -y

RUN sed -i 's/SECLEVEL=2/SECLEVEL=1/' /etc/ssl/openssl.cnf # Temporarily lower security to workaround opentest certs with SHA1 signatures