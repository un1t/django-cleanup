'''
    AppConfig for django-cleanup, prepare the cache and connect signal handlers
'''
from django.apps import AppConfig

from . import cache, handlers


class CleanupConfig(AppConfig):
    name = 'django_cleanup'
    verbose_name = 'Django Cleanup'

    def ready(self):
        cache.prepare()
        handlers.connect()
