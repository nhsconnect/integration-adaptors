FROM python:3.7-alpine as base
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
# dependencies needed to by pipenv install but not required at runtime
RUN apk add --update alpine-sdk libxml2-dev libxslt-dev
RUN pipenv install --ignore-pipfile

FROM base
RUN mkdir -p /root/.local/share/virtualenvs
COPY --from=builder /root/.local/share/virtualenvs /root/.local/share/virtualenvs
EXPOSE 80
ENTRYPOINT pipenv run start
