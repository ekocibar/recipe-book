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
