FROM python:3.7-slim as base

RUN apt-get update && \
    apt-get install -y build-essential libssl-dev swig pkg-config

RUN sed -i 's/SECLEVEL=2/SECLEVEL=1/' /etc/ssl/openssl.cnf # Temporarily lower security to workaround opentest certs with SHA1 signatures
