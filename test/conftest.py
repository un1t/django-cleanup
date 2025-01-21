import copy
import os
import shutil

from django.conf import settings as django_settings
from django.db.models.signals import post_delete, post_init, post_save, pre_save

import pytest

from django_cleanup import cache, handlers

from .testing_helpers import get_random_pic_name


pytest_plugins = ()

def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.django_db(transaction=True))


@pytest.fixture(autouse=True)
def setup_django_cleanup_state(request, settings):
    settings_marker = request.node.get_closest_marker("cleanup_settings")
    settings.CLEANUP = settings_marker.args[0] if settings_marker else None

    for model in cache.cleanup_models():
        suffix = f'_django_cleanup_{cache.get_model_name(model)}'
        post_init.disconnect(None, sender=model,
                             dispatch_uid=f'post_init{suffix}')
        pre_save.disconnect(None, sender=model,
                            dispatch_uid=f'pre_save{suffix}')
        post_save.disconnect(None, sender=model,
                             dispatch_uid=f'post_save{suffix}')
        post_delete.disconnect(None, sender=model,
                               dispatch_uid=f'post_delete{suffix}')
    cache.FIELDS.clear()
    cache.prepare(request.node.get_closest_marker('cleanup_selected_config') is not None)
    handlers.connect()

    stroage_marker = request.node.get_closest_marker('django_storage')
    if stroage_marker is not None:
        storages = copy.deepcopy(settings.STORAGES)
        for key, value in stroage_marker.kwargs.items():
            storages[key]['BACKEND'] = value
        settings.STORAGES = storages


@pytest.fixture(params=[django_settings.MEDIA_ROOT])
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
