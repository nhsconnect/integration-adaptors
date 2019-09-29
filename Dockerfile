FROM python:3-slim

RUN apt-get update
RUN apt-get install build-essential -y

WORKDIR /test

RUN pip install pipenv

COPY . .
WORKDIR integration-tests/integration_tests
RUN pipenv install --dev --deploy --ignore-pipfile

ENV MHS_ADDRESS="outbound"
EXPOSE 80
ENTRYPOINT ["pipenv", "run", "componenttests"]
