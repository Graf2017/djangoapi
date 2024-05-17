FROM python:3.9-alpine3.16

WORKDIR /usr/src/django_project

COPY . /usr/src/django_project

RUN apk add --no-cache build-base && \
    chmod +x ./entrypoint.dev.sh && \
    apk add postgresql-dev gcc musl-dev

RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["./entrypoint.dev.sh"]

