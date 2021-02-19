## Initial Setup 
- Initial setup of Docker, docker-compose and django app

`Dockerfile`
```sh
FROM python:3.7-alpine

# Recommended when run python on docker
# It doesnt buffer python on execution, prints directly
ENV PYTHONUNBUFFERED 1  

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

# Create a user, do not use root
RUN adduser -D user
USER user
```
-
`docker-compose.yml`
```sh
version: "3.8"

services:
  app:
    build: 
      context: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app
    command: >
      sh -c "python manage.py runserver 0.0.0.0:8000"
```

### Commands used

``` sh
docker build .
docker images
docker image rm 67bda6f6d148
docker-compose build
docker-compose run app sh -c "django-admin.py startproject app ."
```

### Do not forget to!
- add `requirements.txt` before building docker images
```sh
Django>=3.0.7,<3.1.0
djangorestframework>=3.11.0,<3.12.0
```
