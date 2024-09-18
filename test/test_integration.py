import os

from django.conf import settings as django_settings
from django.db import transaction

import pytest

from django_cleanup.signals import cleanup_pre_delete

from .testing_helpers import get_using


def test_sorlthumbnail_replace(picture):
    # https://github.com/mariocesar/sorl-thumbnail
    get_thumbnail = pytest.importorskip('sorl.thumbnail').get_thumbnail
    models = pytest.importorskip('test.models.integration')
    product_integration = models.ProductIntegration
    sorl_delete = models.sorl_delete
    cleanup_pre_delete.connect(sorl_delete)
    product = product_integration.objects.create(sorl_image=picture['filename'])
    assert os.path.exists(picture['path'])
    im = get_thumbnail(
        product.sorl_image, '100x100', crop='center', quality=50)
    thumbnail_path = os.path.join(django_settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    product.sorl_image = 'new.png'
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])
    assert not os.path.exists(thumbnail_path)
    cleanup_pre_delete.disconnect(sorl_delete)


def test_sorlthumbnail_delete(picture):
    # https://github.com/mariocesar/sorl-thumbnail
    get_thumbnail = pytest.importorskip('sorl.thumbnail').get_thumbnail
    models = pytest.importorskip( 'test.models.integration')
    product_integration = models.ProductIntegration
    sorl_delete = models.sorl_delete
    cleanup_pre_delete.connect(sorl_delete)
    product = product_integration.objects.create(sorl_image=picture['filename'])
    assert os.path.exists(picture['path'])
    im = get_thumbnail(
        product.sorl_image, '100x100', crop='center', quality=50)
    thumbnail_path = os.path.join(django_settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(picture['path'])
    assert not os.path.exists(thumbnail_path)
    cleanup_pre_delete.disconnect(sorl_delete)


def test_easythumbnails_replace(picture):
    # https://github.com/SmileyChris/easy-thumbnails
    get_thumbnailer = pytest.importorskip('easy_thumbnails.files').get_thumbnailer
    models = pytest.importorskip( 'test.models.integration')
    product_integration = models.ProductIntegration
    product = product_integration.objects.create(easy_image=picture['filename'])
    assert os.path.exists(picture['path'])
    im = get_thumbnailer(product.easy_image).get_thumbnail(
        {'size': (100, 100)})
    thumbnail_path = os.path.join(django_settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    product.easy_image = 'new.png'
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])
    assert not os.path.exists(thumbnail_path)


def test_easythumbnails_delete(picture):
    # https://github.com/SmileyChris/easy-thumbnails
    get_thumbnailer = pytest.importorskip('easy_thumbnails.files').get_thumbnailer
    models = pytest.importorskip( 'test.models.integration')
    product_integration = models.ProductIntegration
    product = product_integration.objects.create(easy_image=picture['filename'])
    assert os.path.exists(picture['path'])
    im = get_thumbnailer(product.easy_image).get_thumbnail(
        {'size': (100, 100)})
    thumbnail_path = os.path.join(django_settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(picture['path'])
    assert not os.path.exists(thumbnail_path)
