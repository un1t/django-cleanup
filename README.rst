django-cleanup automatically deletes old file for FileField, ImageField and subclasses,
and it also deletes files on models instance deletion.

**Warning! If you use transactions you may lose you files if transaction will rollback.
If you are concerned about it you need other solution for old file deletion in your project.**

Most django projects I've seen don't use transactions and this app is designed for such projects.

Features
========
django-cleanup automatically deletes old file for FileField, ImageField and subclasses,
and it also deletes files on models instance deletion.

**Warning! If you use transactions you may lose you files if transaction will rollback.
If you are concerned about it you need other solution for old file deletion in your project.**

Most django projects I've seen don't use transactions and this app is designed for such projects.

Features
========

- Support for Django 1.3, 1.4, 1.5, 1.6, 1.7 and 1.8
- Python 3 support
- Compatible with sorl-thumbnail and easy-thumbnail

How does it work?
=================

django-cleanup connects pre_save and post_delete signals to special functions(these functions
delete old files) for each model which app is listed in INSTALLED_APPS above than 'django_cleanup'.

Installation
============

    pip install django-cleanup


Configuration
=============

Add django_cleanup to settings.py ::

    INSTALLED_APPS = (
        ...
        'django_cleanup', # should go after your apps
    )

**django_cleanup** should be placed after all your apps. (At least after those apps which need to remove files.)


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

How to run tests
================

    tox


License
=======

django-cleanup is free software under terms of the MIT License.

Copyright (C) 2012 by Ilya Shalyapin, ishalyapin@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
