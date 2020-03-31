FROM python:3.7-slim as base

RUN apt-get update && \
    apt-get install build-essential -y

RUN sed -i 's/SECLEVEL=2/SECLEVEL=1/' /etc/ssl/openssl.cnf # Temporarily lower security to workaround opentest certs with SHA1 signatures

FROM base as builder

RUN mkdir -p /usr/src/app/mhs/spineroutelookup

COPY mhs/spineroutelookup/Pipfile /usr/src/app
COPY mhs/spineroutelookup/Pipfile.lock /usr/src/app

RUN pip install pipenv


COPY common/ /usr/src/app/common/
COPY mhs/common/ /usr/src/app/mhs/common/
COPY mhs/spineroutelookup/ /usr/src/app/mhs/spineroutelookup


WORKDIR /usr/src/app/mhs/spineroutelookup

RUN pipenv install --deploy --ignore-pipfile

FROM builder


EXPOSE 80

ENTRYPOINT pipenv run start