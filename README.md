
## Wait for db before running the server
- There is a known problem that sometimes postgres db is not available directly,
thats why we need to wait till it becomes available before running the server.
- Add a management command as `wait_for_db` (wait until db is available)
- Configure `command` section in `docker-compose` accordingly.

#### Add tests
Mock django's `ConnectionHandler` utilty to test `wait_for_db` command.

`app/core/tests/test_commands.py`
```diff
from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """ Test waiting for db when db is ready"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """ Test waiting for db"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
```

#### Add `wait_for_db` command
Add a command to wait until db is available.
- Inherit from `BaseCommand` to add `wait_for_db` command.
- Used directory is django convention.

`app/core/management/commands/wait_for_db.py`
```diff
import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Django command to pause exevution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waitin for database...')
        db_connection = None
        while not db_connection:
            try:
                db_connection = connections['default']
            except OperationalError:
                self.stdout.write(('Database is unavailable, '
                                   'waiting for 1 second...'))
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
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
-     sh -c "python manage.py runserver 0.0.0.0:8000"
+     sh -c "python manage.py wait_for_db &&
+            python manage.py migrate &&
+            python manage.py runserver 0.0.0.0:8000"
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
