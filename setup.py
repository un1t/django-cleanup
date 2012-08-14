#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2012 Ilya Shalyapin
#
#  django-cleanup is free software under terms of the MIT License.
#

import os
from setuptools import setup


readme = open(os.path.join(os.path.dirname(__file__), 'README.markdown')).read()

setup(
    name     = 'django-cleanup',
    version  = '0.1',
    packages = ['django_cleanup'],

    requires = ['python (>= 2.5)', 'django (>= 1.3)'],

    description  = 'Deletes old files.',
    long_description = readme,
    author       = 'Ilya Shalyapin',
    author_email = 'ishalyapin@gmail.com',
    url          = 'https://github.com/un1t/django-cleanup',
    download_url = 'https://github.com/un1t/django-cleanup/tarball/master',
    license      = 'MIT License',
    keywords     = 'django',
    classifiers  = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)
