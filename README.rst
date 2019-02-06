django-cleanup automatically deletes files for :code:`FileField`, :code:`ImageField`, and
subclasses. It will delete old files when a new file is being saved and it will delete
files on model instance deletion.

**Warning! If you are using a database that does not support transactions you may lose files if a
transaction will rollback at the right instance. Though this outcome is reduced by our use of
post_save and post_delete signals, this outcome will still occur if there are errors in signals that
are handled after our signals are handled. In this case, the old file will be lost and the new file
will not be referenced in a model, though the new file will likely still exist on disk. If you are
concerned about this behavior you will need another solution for old file deletion in your project.**

Features
========

- Support for Django 1.11, 2.0, 2.1
- Python 2.7 and 3.4+ support
- Compatible with sorl-thumbnail and easy-thumbnail

How does it work?
=================

When a :code:`FileField`'s value is changed and the model is saved, the old file is deleted. When a
model that has a :code:`FileField` is deleted, the file is also deleted. If the :code:`FileField`'s
value matches the :code:`FileField`'s default value then the file will not be deleted.

django-cleanup connects :code:`post_init`, :code:`pre_save`, :code:`post_save`, and
:code:`post_delete` signals to signal handlers for each model that has a :code:`FileField` and which
app is listed in :code:`INSTALLED_APPS`. In order to tell whether or not a :code:`FileField`'s value
has changed a local cache of original values is kept on the model instance.

Installation
============
::

    pip install django-cleanup


Configuration
=============

Add django_cleanup to settings.py ::

    INSTALLED_APPS = (
        ...
        'django_cleanup.apps.CleanupConfig',
    )

Signals
=======

django-cleanup sends the following signals which can be imported from
:code:`django_cleanup.signals`:

- **cleanup_pre_delete** just before a file is deleted. Passes a :code:`file` keyword argument.
- **cleanup_post_delete** just after a file is deleted. Passes a :code:`file` keyword argument.

Signals example for sorl.thumbnail
----------------------------------
::

    from django_cleanup.signals import cleanup_pre_delete, cleanup_post_delete

    def sorl_delete(**kwargs):
        from sorl.thumbnail import delete
        delete(kwargs['file'])

    cleanup_pre_delete.connect(sorl_delete)

Refresh the cache
=================
Refresh the cleanup cache on the instance.
::

    from django_cleanup import cleanup

    ...

    cleanup.refresh(instance)
    ...


How to run tests
================
::

    tox

How to write tests
==================
This library requires the use of django.test.TransactionTestCase_ when writing tests.

For details on why this is required see
`here <https://docs.djangoproject.com/en/2.1/topics/db/transactions/#use-in-tests>`_:

    Django’s :code:`TestCase` class wraps each test in a transaction and rolls back that transaction
    after each test, in order to provide test isolation. This means that no transaction is ever
    actually committed, thus your :code:`on_commit()` callbacks will never be run. If you need to
    test the results of an :code:`on_commit()` callback, use a :code:`TransactionTestCase` instead.

License
=======

django-cleanup is free software under terms of the MIT License.

Copyright (C) 2012 by Ilya Shalyapin, ishalyapin@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


.. _django.test.TransactionTestCase: https://docs.djangoproject.com/en/2.1/topics/testing/tools/#django.test.TransactionTestCase
