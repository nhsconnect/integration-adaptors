FROM python:3-slim

RUN apt-get update
RUN apt-get install build-essential -y

WORKDIR /test

RUN pip install pipenv

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --dev --deploy --ignore-pipfile

COPY . .

ENV MHS_ADDRESS="outbound"
EXPOSE 80
ENTRYPOINT ["pipenv", "run", "componenttests"]
