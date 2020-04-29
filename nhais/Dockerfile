FROM python:3.7-slim as base
RUN pip install pipenv
RUN mkdir -p /usr/src/app/nhais
# TODO: should just be . after NIAD-193
# COPY . /usr/src/app/nhais
COPY ./nhais/ /usr/src/app/nhais
# TODO: Remove common after NIAD-193
RUN mkdir -p /usr/src/app/common
COPY ./common/ /usr/src/app/common
WORKDIR /usr/src/app/nhais

FROM base as builder
# build-essential needed to by pipenv to compile dependencies but not needed at runtime
RUN apt-get update && apt-get install build-essential -y
RUN pipenv install --ignore-pipfile

FROM base
RUN mkdir -p /root/.local/share/virtualenvs
COPY --from=builder /root/.local/share/virtualenvs /root/.local/share/virtualenvs
EXPOSE 80
ENTRYPOINT pipenv run start
