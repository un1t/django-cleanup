django-cleanup automatically deletes files for FileField, ImageField, and
subclasses. It will delete old files when a new file is being save and it
will delete files on model instance deletion.

**Warning! If you use transactions you may lose files if a transaction will
rollback at the right instance. Though this outcome is reduced by our use of
post_save and post_delete signals, this outcome will still occur if there are
errors in signals that are handled after our signals are handled. In this case
the old file will be lost and the new file will not be referenced in a model,
though the new file will likely still exist on disk. If you are concerned about
it you need another solution for old file deletion in your project. This is fixed in Django 1.9+ if you are using a database that supports
transactions.**

Features
========

- Support for Django 1.7, 1.8, 1.9
- Python 3 support
- Compatible with sorl-thumbnail and easy-thumbnail

How does it work?
=================

django-cleanup connects post_init, pre_save, post_save, and post_delete signals
to signal handlers for each model that has a FileField and which app is listed
in INSTALLED_APPS. In order to tell whether or not a FileField's value has
changed a local cache of original values is kept on the model instance.

Installation
============
::

    pip install django-cleanup


Configuration
=============

Add django_cleanup to settings.py ::

    INSTALLED_APPS = (
        ...
        'django_cleanup',
    )

Signals
=======

django-cleanup sends the following signals which can be imported from `django_cleanup.signals`:

- **cleanup_pre_delete** just before a file is deleted. Passes a `file` keyword argument.
- **cleanup_post_delete** just after a file is deleted. Passes a `file` keyword argument.

Signals example for sorl.thumbnail
----------------------------------
::

    from django_cleanup.signals import cleanup_pre_delete, cleanup_post_delete

    def sorl_delete(**kwargs):
        from sorl.thumbnail import delete
        delete(kwargs['file'])

    cleanup_pre_delete.connect(sorl_delete)

Refresh from db
===============
Django 1.8 introduced the model method **refresh_from_db** which allows one to
get a fresh copy of data in their model instance. After a call to this method
you will also need to refresh the cleanup cache on the instance.
::

    from django_cleanup import cleanup

    ...

    instance.refresh_from_db()
    cleanup.refresh(instance)
    ...


How to run tests
================
::

    tox


License
=======

django-cleanup is free software under terms of the MIT License.

Copyright (C) 2012 by Ilya Shalyapin, ishalyapin@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
