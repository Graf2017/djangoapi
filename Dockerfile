FROM python:3.9-alpine3.16

COPY requirements.txt /temp/requirements.txt
COPY api_webstore /api_marketplace
WORKDIR /service
EXPOSE 8000


