# django-cleanup

django-cleanup automatically deletes old file for FileField, ImageField and subclasses,
and it also deletes files on models instance deletion.

**Warning! If you use transactions you may lose you files if transaction will rollback. 
If you are concerned about it you need other solution for old file deletion in your project.**

Most django projects I've seen don't use transactions and this app is designed for such projects.

## How does it work?

django-cleanup connects pre_save and post_delete signals to special functions(these functions 
delete old files) for each model which app is listed in INSTALLED_APPS above than 'django_cleanup'.

## Installation
    
    pip install django-cleanup


## Configuration

Add django_cleanup to settings.py

    INSTALLED_APPS = (
        ...
        'django_cleanup', # should go after your apps
    )

**django_cleanup** should be placed after all your apps. (At least after those apps which need to remove files.)

