from python:3-slim


COPY . /app
WORKDIR /app/mhs/inbound


RUN pip install pipenv

RUN pipenv install --ignore-pipfile

CMD ["pipenv", "run", "start-inbound"]