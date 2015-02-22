DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'django_cleanup.testapp',
    'django_cleanup',
)

MIDDLEWARE_CLASSES = []

SECRET_KEY = '123'
