import os
import random
import shutil
import string

from django.conf import settings
from django.db import router

import pytest


def get_using(instance):
    return router.db_for_write(instance.__class__, instance=instance)


def get_random_pic_name(length=20):
    return 'pic{}.jpg'.format(
        ''.join(random.choice(string.ascii_letters) for m in range(length)))


@pytest.fixture(params=[settings.MEDIA_ROOT])
def picture(request):
    src = os.path.join(request.param, 'pic.jpg')
    dst = os.path.join(request.param, get_random_pic_name())
    shutil.copyfile(src, dst)
    try:
        yield {
            'path': dst,
            'filename': os.path.split(dst)[-1],
            'srcpath': src
        }
    finally:
        if os.path.exists(dst):
            os.remove(dst)
