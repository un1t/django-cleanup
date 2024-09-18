import os

import django


BASE_DIR = os.path.dirname(__file__)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'test',
    'django_cleanup',
)

INSTALLED_APPS_INTEGRATION = (
    'sorl.thumbnail',
    'easy_thumbnails',
)

try:
    import easy_thumbnails.fields
    import sorl.thumbnail
except ImportError:
    pass
except (django.core.exceptions.AppRegistryNotReady, django.core.exceptions.ImproperlyConfigured):
    INSTALLED_APPS = INSTALLED_APPS + INSTALLED_APPS_INTEGRATION

MIDDLEWARE_CLASSES = []
SECRET_KEY = '123'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

## workaround: https://github.com/SmileyChris/easy-thumbnails/issues/641#issuecomment-2291098096
THUMBNAIL_DEFAULT_STORAGE_ALIAS = 'default'
