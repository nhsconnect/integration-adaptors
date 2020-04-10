FROM python:3.7-slim

RUN apt-get update
RUN apt-get install build-essential -y

WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --deploy --ignore-pipfile

COPY . .

EXPOSE 80
#ENTRYPOINT ["pipenv", "run", "start", "--logging=DEBUG"]
ENTRYPOINT echo "Starting up, env variables:";  env | grep FAKE_SPINE ; pipenv run start --logging=DEBUG
