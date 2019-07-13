# coding: utf-8
from __future__ import unicode_literals

import os
import random
import shutil
import string

from django.conf import settings
from django.db import router

import pytest


def get_using(instance):
    return router.db_for_write(instance.__class__, instance=instance)


def random_pic(length=20):
    return 'pic{}.jpg'.format(
        ''.join(random.choice(string.ascii_letters) for m in range(length)))


@pytest.yield_fixture
def pic1():
    src = os.path.join(settings.MEDIA_ROOT, 'pic.jpg')
    dst = os.path.join(settings.MEDIA_ROOT, random_pic())
    shutil.copyfile(src, dst)
    yield {
        'path': dst,
        'filename': os.path.split(dst)[-1],
        'srcpath': src
    }
    if os.path.exists(dst):
        os.remove(dst)
