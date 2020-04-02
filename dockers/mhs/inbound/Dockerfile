FROM nhsdev/nia-mhs-inbound-base:latest

RUN mkdir -p /usr/src/app/mhs/inbound

COPY mhs/inbound/Pipfile /usr/src/app
COPY mhs/inbound/Pipfile.lock /usr/src/app

RUN pip install pipenv

COPY common/ /usr/src/app/common/
COPY mhs/common/ /usr/src/app/mhs/common/
COPY mhs/inbound/ /usr/src/app/mhs/inbound

WORKDIR /usr/src/app/mhs/inbound

RUN pipenv install --deploy --ignore-pipfile

EXPOSE 443 80

ENTRYPOINT pipenv run start-inbound