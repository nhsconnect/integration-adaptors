FROM nhsdev/nia-sds-base:latest

WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --deploy --ignore-pipfile

COPY . .

EXPOSE 80
ENTRYPOINT ["pipenv", "run", "start", "--logging=DEBUG"]
