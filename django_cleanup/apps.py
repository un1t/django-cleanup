# coding: utf-8
import django
if django.VERSION >= (1, 7):

    from django.apps import AppConfig
    from .models import connect_signals

    class CleanupConfig(AppConfig):
        name = 'django_cleanup'

        def ready(self):
            connect_signals()
