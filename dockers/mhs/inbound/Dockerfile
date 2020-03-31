FROM python:3.7-slim as base

RUN apt-get update && \
    apt-get install -y build-essential libssl-dev swig pkg-config

RUN sed -i 's/SECLEVEL=2/SECLEVEL=1/' /etc/ssl/openssl.cnf # Temporarily lower security to workaround opentest certs with SHA1 signatures

FROM base as builder

RUN mkdir -p /usr/src/app/mhs/inbound

COPY mhs/inbound/Pipfile /usr/src/app
COPY mhs/inbound/Pipfile.lock /usr/src/app

RUN pip install pipenv

COPY common/ /usr/src/app/common/
COPY mhs/common/ /usr/src/app/mhs/common/
COPY mhs/inbound/ /usr/src/app/mhs/inbound

WORKDIR /usr/src/app/mhs/inbound

RUN pipenv install --deploy --ignore-pipfile

FROM builder

EXPOSE 443 80

ENTRYPOINT pipenv run start-inbound