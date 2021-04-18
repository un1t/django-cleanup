#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2012 Ilya Shalyapin
#
#  django-cleanup is free software under terms of the MIT License.
#

import os
import re
from codecs import open as codecs_open

from setuptools import find_packages, setup


def read(*parts):
    file_path = os.path.join(os.path.dirname(__file__), *parts)
    return codecs_open(file_path, encoding='utf-8').read()


def find_version(*parts):
    version_file = read(*parts)
    version_match = re.search(
        r'''^__version__ = ['"]([^'"]*)['"]''', version_file, re.M)
    if version_match:
        return str(version_match.group(1))
    raise RuntimeError('Unable to find version string.')


setup(
    name='django-cleanup',
    version=find_version('django_cleanup', '__init__.py'),
    packages=['django_cleanup'],
    include_package_data=True,
    requires=['python (>=3.5)', 'django (>=2.2)'],
    description='Deletes old files.',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    author='Ilya Shalyapin',
    author_email='ishalyapin@gmail.com',
    url='https://github.com/un1t/django-cleanup',
    download_url='https://github.com/un1t/django-cleanup/tarball/master',
    license='MIT License',
    keywords='django',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
)
