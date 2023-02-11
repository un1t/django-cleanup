import os
import shutil

from django.conf import settings
from django.db.models.signals import post_delete, post_init, post_save, pre_save

import pytest

from django_cleanup import cache, handlers

from .testing_helpers import get_random_pic_name


pytest_plugins = ("test.pytest_plugin",)


@pytest.fixture(autouse=True)
def setup_django_cleanup_state(request):
    for model in cache.cleanup_models():
        key = '{{}}_django_cleanup_{}'.format(cache.get_model_name(model))
        post_init.disconnect(None, sender=model,
                             dispatch_uid=key.format('post_init'))
        pre_save.disconnect(None, sender=model,
                            dispatch_uid=key.format('pre_save'))
        post_save.disconnect(None, sender=model,
                             dispatch_uid=key.format('post_save'))
        post_delete.disconnect(None, sender=model,
                               dispatch_uid=key.format('post_delete'))
    cache.FIELDS.clear()
    selectedConfig = any(m.name == 'CleanupSelectedConfig' for m in request.node.iter_markers())

    cache.prepare(selectedConfig)
    handlers.connect()


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
