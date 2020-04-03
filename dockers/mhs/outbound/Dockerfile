FROM nhsdev/nia-mhs-outbound-base:latest

RUN mkdir -p /usr/src/app/mhs/outbound

COPY mhs/outbound/Pipfile /usr/src/app
COPY mhs/outbound/Pipfile.lock /usr/src/app

RUN pip install pipenv

COPY common/ /usr/src/app/common/
COPY mhs/common/ /usr/src/app/mhs/common/
COPY mhs/outbound/ /usr/src/app/mhs/outbound

WORKDIR /usr/src/app/mhs/outbound

RUN pipenv install --deploy --ignore-pipfile

EXPOSE 80

ENTRYPOINT pipenv run start-outbound