FROM python:3-slim

RUN apt-get update
RUN apt-get install build-essential -y

WORKDIR /app

RUN pip install pipenv
COPY . .
RUN pipenv install --deploy --ignore-pipfile

EXPOSE 80
ENTRYPOINT ["pipenv", "run", "start", "--logging=DEBUG"]
