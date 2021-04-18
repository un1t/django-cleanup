'''
    django-cleanup automatically deletes files for FileField, ImageField, and
    subclasses. It will delete old files when a new file is being save and it
    will delete files on model instance deletion.
'''
__version__ = '5.2.0'
default_app_config = 'django_cleanup.apps.CleanupConfig'
