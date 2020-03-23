FROM python:3.7-slim as base

RUN apt-get update && \
  apt-get install build-essential libcurl4-openssl-dev libssl-dev -y

RUN sed -i 's/SECLEVEL=2/SECLEVEL=1/' /etc/ssl/openssl.cnf # Temporarily lower security to workaround opentest certs with SHA1 signatures"

FROM base as builder

RUN mkdir -p /usr/src/app/SCRWebService

COPY SCRWebService/Pipfile /usr/src/app
COPY SCRWebService/Pipfile.lock /usr/src/app

RUN pip install pipenv


COPY common/ /usr/src/app/common/
COPY SCR/ /usr/src/app/SCR/
COPY SCRWebService/ /usr/src/app/SCRWebService


WORKDIR /usr/src/app/SCRWebService

RUN pipenv install --deploy --ignore-pipfile

FROM builder

EXPOSE 80

ENTRYPOINT pipenv run scr-server

