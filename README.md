
## Wait for db before running the server
- Add a management command to wait for db
- Configure docker-compose

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
   environment:
     - DB_HOST=db
     - DB_NAME=app
     - DB_USER=kocibar
     - DB_PASS=supersecret
   depends_on:
     - db

 db:
   image: postgres:10-alpine
   environment:
     - POSTGRES_DB=app
     - POSTGRES_USER=kocibar
     - POSTGRES_PASSWORD=supersecret

```
