FROM python:3.7-slim as base
RUN pip install pipenv
RUN mkdir -p /usr/src/app
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pipenv install --ignore-pipfile
EXPOSE 80
ENTRYPOINT pipenv run start
