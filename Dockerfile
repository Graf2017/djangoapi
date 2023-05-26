FROM python:3.9-alpine3.16

WORKDIR /project

COPY . .

#RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 8000


