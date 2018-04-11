FROM python:alpine3.6

RUN apk update \
  && apk add \
    build-base \
    postgresql \
    postgresql-dev \
    libpq

WORKDIR /src/app/gordias
COPY ./requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8080	

COPY src ./