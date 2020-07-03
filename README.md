
## Postgres Configuration
- Add postgres dependecy
- Configure docker-compose
- Configure Dockerfile
- Configure Django settings

#### requirements.txt
`psycopg2` is advised package for PostgreSQL

`requirements.txt`
```diff
language: python
  Django>=3.0.7,<3.1.0
  djangorestframework>=3.11.0,<3.12.0
+ psycopg2>=2.8.5,<2.9.0

  flake8>=3.8.3,<3.9.0

```

#### docker-compose.yml

`docker-compose.yml`
```diff
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
+   environment:
+     - DB_HOST=db
+     - DB_NAME=app
+     - DB_USER=kocibar
+     - DB_PASS=supersecret
+   depends_on:
+     - db
+
+ db:
+   image: postgres:10-alpine
+   environment:
+     - POSTGRES_DB=app
+     - POSTGRES_USER=kocibar
+     - POSTGRES_PASSWORD=supersecret

```

#### Dockerfile
Here we try to keep the image size as small as possible,
- install the packeges with `no-cache` flags to keep no cache,
- remove the unnecessary packages when they are not required anymore(line 77)

`Dockerfile`
```diff
  FROM python:3.7-alpine

  # Recommended when run python on docker
  # It doesnt buffer python on execution, prints directly
  ENV PYTHONUNBUFFERED 1

  COPY ./requirements.txt /requirements.txt
+ # Install postgres app
+ RUN apk add --update --no-cache postgresql-client
+ # Install required apps to install postgres app
+ # set an alias in order to remove them afterwards
+ RUN apk add --update --no-cache --virtual .tmp-build-deps \
+       gcc libc-dev linux-headers postgresql-dev
  RUN pip install -r /requirements.txt
  # Remove temporary apps
+ RUN apk del .tmp-build-deps

  RUN mkdir /app
  WORKDIR /app
  COPY ./app /app

  # Create a user, do not use root
  RUN adduser -D user
  USER user


```

#### settings.py
Here we use `os.environ` to get db credentials,
makes it safer and easier when deploying on production

`settings.py`
```diff
  # Database
  # https://docs.djangoproject.com/en/3.0/ref/settings/#databases

  DATABASES = {
      'default': {
+         'ENGINE': 'django.db.backends.postgresql',
+         'HOST': os.environ.get('DB_HOST'),
+         'NAME': os.environ.get('DB_NAME'),
+         'USER': os.environ.get('DB_USER'),
+         'PASSWORD': os.environ.get('DB_PASS'),
      }
  }


```
