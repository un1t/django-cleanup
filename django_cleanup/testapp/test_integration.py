import os

from django.conf import settings
from django.db import transaction

import pytest

from django_cleanup.signals import cleanup_pre_delete

from .testing_helpers import get_using, picture


@pytest.mark.django_db(transaction=True)
def test_sorlthumbnail_replace(settings, picture):
    # https://github.com/mariocesar/sorl-thumbnail
    models = pytest.importorskip("django_cleanup.testapp.models.integration")
    ProductIntegration = models.ProductIntegration
    sorl_delete = models.sorl_delete
    cleanup_pre_delete.connect(sorl_delete)
    from sorl.thumbnail import get_thumbnail
    product = ProductIntegration.objects.create(sorl_image=picture['filename'])
    assert os.path.exists(picture['path'])
    im = get_thumbnail(
        product.sorl_image, '100x100', crop='center', quality=50)
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    product.sorl_image = 'new.png'
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])
    assert not os.path.exists(thumbnail_path)
    cleanup_pre_delete.disconnect(sorl_delete)


@pytest.mark.django_db(transaction=True)
def test_sorlthumbnail_delete(picture):
    # https://github.com/mariocesar/sorl-thumbnail
    models = pytest.importorskip("django_cleanup.testapp.models.integration")
    ProductIntegration = models.ProductIntegration
    sorl_delete = models.sorl_delete
    cleanup_pre_delete.connect(sorl_delete)
    from sorl.thumbnail import get_thumbnail
    product = ProductIntegration.objects.create(sorl_image=picture['filename'])
    assert os.path.exists(picture['path'])
    im = get_thumbnail(
        product.sorl_image, '100x100', crop='center', quality=50)
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(picture['path'])
    assert not os.path.exists(thumbnail_path)
    cleanup_pre_delete.disconnect(sorl_delete)


@pytest.mark.django_db(transaction=True)
def test_easythumbnails_replace(picture):
    # https://github.com/SmileyChris/easy-thumbnails
    models = pytest.importorskip("django_cleanup.testapp.models.integration")
    ProductIntegration = models.ProductIntegration
    from easy_thumbnails.files import get_thumbnailer
    product = ProductIntegration.objects.create(easy_image=picture['filename'])
    assert os.path.exists(picture['path'])
    im = get_thumbnailer(product.easy_image).get_thumbnail(
        {'size': (100, 100)})
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    product.easy_image = 'new.png'
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])
    assert not os.path.exists(thumbnail_path)


@pytest.mark.django_db(transaction=True)
def test_easythumbnails_delete(picture):
    # https://github.com/SmileyChris/easy-thumbnails
    models = pytest.importorskip("django_cleanup.testapp.models.integration")
    ProductIntegration = models.ProductIntegration
    from easy_thumbnails.files import get_thumbnailer
    product = ProductIntegration.objects.create(easy_image=picture['filename'])
    assert os.path.exists(picture['path'])
    im = get_thumbnailer(product.easy_image).get_thumbnail(
        {'size': (100, 100)})
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(picture['path'])
    assert not os.path.exists(thumbnail_path)
