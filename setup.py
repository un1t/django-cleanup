#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2012 Ilya Shalyapin
#
#  django-cleanup is free software under terms of the MIT License.
#

import os
from setuptools import setup, find_packages


setup(
    name     = 'django-cleanup',
    version  = '0.1.12',
    packages = find_packages(),
    include_package_data=True,
    requires = ['python (>= 2.5)', 'django (>= 1.3)'],
    description  = 'Deletes old files.',
    long_description = open('README.markdown').read(), 
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
