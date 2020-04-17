FROM python:3.7-slim
RUN apt-get update
RUN apt-get install build-essential -y
RUN mkdir -p /usr/src/app/mhs/fakespine
RUN pip install pipenv
COPY common/ /usr/src/app/common/
COPY integration-tests/fake_spine/ /usr/src/app/mhs/fakespine
WORKDIR /usr/src/app/mhs/fakespine
COPY integration-tests/fake_spine/Pipfile /usr/src/app
COPY integration-tests/fake_spine/Pipfile.lock /usr/src/app
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile
COPY . .
EXPOSE 80 443
ENTRYPOINT ["pipenv", "run", "start", "--logging=DEBUG"]
