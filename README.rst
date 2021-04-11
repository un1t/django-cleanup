Django Cleanup
**************
|Version| |Status| |License|

Features
========
The django-cleanup app automatically deletes files for :code:`FileField`, :code:`ImageField` and
subclasses. When a :code:`FileField`'s value is changed and the model is saved, the old file is
deleted. When a model that has a :code:`FileField` is deleted, the file is also deleted. A file that
is set as the :code:`FileField`'s default value will not be deleted.

Compatibility
-------------
- Django 2.2, 3.0, 3.1, 3.2 (`See Django Supported Versions <https://www.djangoproject.com/download/#supported-versions>`_)
- Python 3.5+
- Compatible with `sorl-thumbnail <https://github.com/jazzband/sorl-thumbnail>`_
- Compatible with `easy-thumbnail <https://github.com/SmileyChris/easy-thumbnails>`_

How does it work?
=================
In order to track changes of a :code:`FileField` and facilitate file deletions, django-cleanup
connects :code:`post_init`, :code:`pre_save`, :code:`post_save` and :code:`post_delete` signals to
signal handlers for each :code:`INSTALLED_APPS` model that has a :code:`FileField`. In order to tell
whether or not a :code:`FileField`'s value has changed a local cache of original values is kept on
the model instance. If a condition is detected that should result in a file deletion, a function to
delete the file is setup and inserted into the commit phase of the current transaction.

**Warning! If you are using a database that does not support transactions you may lose files if a
transaction will rollback at the right instance. This outcome is mitigated by our use of
post_save and post_delete signals, and by following the recommended configuration below. This
outcome will still occur if there are signals registered after app initialization and there are
exceptions when those signals are handled. In this case, the old file will be lost and the new file
will not be referenced in a model, though the new file will likely still exist on disk. If you are
concerned about this behavior you will need another solution for old file deletion in your project.**

Installation
============
::

    pip install django-cleanup


Configuration
=============
Add ``django_cleanup`` to the bottom of ``INSTALLED_APPS`` in ``settings.py``

.. code-block:: py

    INSTALLED_APPS = (
        ...,
        'django_cleanup.apps.CleanupConfig',
    )

That is all, no other configuration is necessary.

Note: Order of ``INSTALLED_APPS`` is important. To ensure that exceptions inside other apps' signal
handlers do not affect the integrity of file deletions within transactions, ``django_cleanup``
should be placed last in ``INSTALLED_APPS``.

Troubleshooting
===============
If you notice that ``django-cleanup`` is not removing files when expected, check that your models
are being properly
`loaded <https://docs.djangoproject.com/en/stable/ref/applications/#how-applications-are-loaded>`_:

    You must define or import all models in your application's models.py or models/__init__.py.
    Otherwise, the application registry may not be fully populated at this point, which could cause
    the ORM to malfunction.

If your models are not loaded, ``django-cleanup`` will not be able to discover their
``FileField``'s.

You can check if your ``Model`` is loaded by using

.. code-block:: py

    from django.apps import apps
    apps.get_models()

Advanced
========
This section contains additional functionality that can be used to interact with django-cleanup for
special cases.

Signals
-------
To facilitate interactions with other django apps django-cleanup sends the following signals which
can be imported from :code:`django_cleanup.signals`:

- :code:`cleanup_pre_delete`: just before a file is deleted. Passes a :code:`file` keyword argument.
- :code:`cleanup_post_delete`: just after a file is deleted. Passes a :code:`file` keyword argument.

Signals example for sorl.thumbnail:

.. code-block:: py

    from django_cleanup.signals import cleanup_pre_delete
    from sorl.thumbnail import delete

    def sorl_delete(**kwargs):
        delete(kwargs['file'])

    cleanup_pre_delete.connect(sorl_delete)

Refresh the cache
-----------------
There have been rare cases where the cache would need to be refreshed. To do so the
:code:`django_cleanup.cleanup.refresh` method can be used:

.. code-block:: py

    from django_cleanup import cleanup

    cleanup.refresh(model_instance)

Ignore cleanup for a specific model
-----------------------------------
Ignore a model and do not perform cleanup when the model is deleted or its files change.

.. code-block:: py

    from django_cleanup import cleanup

    @cleanup.ignore
    class MyModel(models.Model):
        image = models.FileField()

How to run tests
================
Install, setup and use pyenv_ to install all the required versions of cPython
(see the `tox.ini <https://github.com/un1t/django-cleanup/blob/master/tox.ini>`_).

Setup pyenv_ to have all versions of python activated within your local django-cleanup repository.
Ensuring that the python 3.8 that was installed is first priority.

Install tox_ on python 3.8 and run the :code:`tox` command from your local django-cleanup
repository.

How to write tests
==================
This app requires the use of django.test.TransactionTestCase_ when writing tests.

For details on why this is required see `here
<https://docs.djangoproject.com/en/stable/topics/db/transactions/#use-in-tests>`_:

    Django's :code:`TestCase` class wraps each test in a transaction and rolls back that transaction
    after each test, in order to provide test isolation. This means that no transaction is ever
    actually committed, thus your :code:`on_commit()` callbacks will never be run. If you need to
    test the results of an :code:`on_commit()` callback, use a :code:`TransactionTestCase` instead.

License
=======
django-cleanup is free software under terms of the:

MIT License

Copyright (C) 2012 by Ilya Shalyapin, ishalyapin@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


.. _django.test.TransactionTestCase: https://docs.djangoproject.com/en/stable/topics/testing/tools/#django.test.TransactionTestCase
.. _pyenv: https://github.com/pyenv/pyenv
.. _tox: https://tox.readthedocs.io/en/latest/

.. |Version| image:: https://img.shields.io/pypi/v/django-cleanup.svg
   :target: https://pypi.python.org/pypi/django-cleanup/
   :alt: PyPI Package
.. |Status| image:: https://travis-ci.org/un1t/django-cleanup.svg?branch=master
   :target: https://travis-ci.org/un1t/django-cleanup
   :alt: Build Status
.. |License| image:: https://img.shields.io/badge/license-MIT-maroon
   :target: https://github.com/un1t/django-cleanup/blob/master/LICENSE
   :alt: MIT License
