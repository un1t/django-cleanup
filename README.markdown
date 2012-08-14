# django-cleanup

django-cleanup automatically deletes old file for FileField, ImageField and subclasses,
and it also deletes files on models instance deletion.


## Installation
    
    pip install django-cleanup


## Configuration

Add django_cleanup to settings.py

    INSTALLED_APPS = (
        ...
        'django_cleanup', # should go after your apps
    )

Warning! django_cleanup should be placed after all your apps. (At least after those apps which need to remove files.)

