# coding: utf-8
'''
    django-cleanup automatically deletes files for FileField, ImageField, and
    subclasses. It will delete old files when a new file is being save and it
    will delete files on model instance deletion.
'''
__version__ = '0.4.2'
default_app_config = 'django_cleanup.apps.CleanupConfig'
