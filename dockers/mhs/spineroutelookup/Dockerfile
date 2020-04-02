FROM nhsdev/nia-sds-base:latest

RUN mkdir -p /usr/src/app/mhs/spineroutelookup

COPY mhs/spineroutelookup/Pipfile /usr/src/app
COPY mhs/spineroutelookup/Pipfile.lock /usr/src/app

RUN pip install pipenv

COPY common/ /usr/src/app/common/
COPY mhs/common/ /usr/src/app/mhs/common/
COPY mhs/spineroutelookup/ /usr/src/app/mhs/spineroutelookup

WORKDIR /usr/src/app/mhs/spineroutelookup

RUN pipenv install --deploy --ignore-pipfile

EXPOSE 80

ENTRYPOINT pipenv run start