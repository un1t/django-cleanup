# coding: utf-8
import os
import shutil
import pytest
from flexmock import flexmock
from django.conf import settings
from django_cleanup.signals import cleanup_pre_delete, cleanup_post_delete
from .models import Product


@pytest.yield_fixture
def pic1():
    src = os.path.join(settings.MEDIA_ROOT, 'pic.jpg')
    dst = os.path.join(settings.MEDIA_ROOT, 'pic1.jpg')
    shutil.copyfile(src, dst)
    yield {
        'path': dst,
        'filename': os.path.split(dst)[-1]
    }
    if os.path.exists(dst):
        os.remove(dst)


@pytest.mark.django_db
def test_replace_file(pic1):
    product = Product.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product.image = 'new.jpg'
    product.save()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db
def test_remove_model_instance(pic1):
    product = Product.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product.delete()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db
def test_remove_blank_file(monkeypatch):
    def _raise(message):
        raise Exception(message)

    product = Product.objects.create(image='')
    monkeypatch.setattr(product.image.storage, 'exists', lambda x: _raise('should not call exists'))
    monkeypatch.setattr(product.image.storage, 'delete', lambda x: _raise('should not call delete'))
    product.delete()


@pytest.mark.django_db
def test_remove_not_exists():
    product = Product.objects.create(image='no-such-file')
    product.delete()


@pytest.mark.django_db
def test_sorlthumbnail_replace(pic1):
    # https://github.com/mariocesar/sorl-thumbnail
    from sorl.thumbnail import get_thumbnail
    product = Product.objects.create(sorl_image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    im = get_thumbnail(
        product.sorl_image, '100x100', crop='center', quality=50)
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    product.sorl_image = 'new.png'
    product.save()
    assert not os.path.exists(pic1['path'])
    assert not os.path.exists(thumbnail_path)


@pytest.mark.django_db
def test_sorlthumbnail_delete(pic1):
    # https://github.com/mariocesar/sorl-thumbnail
    from sorl.thumbnail import get_thumbnail
    product = Product.objects.create(sorl_image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    im = get_thumbnail(
        product.sorl_image, '100x100', crop='center', quality=50)
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    product.delete()
    assert not os.path.exists(pic1['path'])
    assert not os.path.exists(thumbnail_path)


@pytest.mark.django_db
def test_easythumbnails_replace(pic1):
    # https://github.com/SmileyChris/easy-thumbnails
    from easy_thumbnails.files import get_thumbnailer
    product = Product.objects.create(easy_image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    im = get_thumbnailer(product.easy_image).get_thumbnail(
        {'size': (100, 100)})
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    product.easy_image = 'new.png'
    product.save()
    assert not os.path.exists(pic1['path'])
    assert not os.path.exists(thumbnail_path)


@pytest.mark.django_db
def test_easythumbnails_delete(pic1):
    # https://github.com/SmileyChris/easy-thumbnails
    from easy_thumbnails.files import get_thumbnailer
    product = Product.objects.create(easy_image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    im = get_thumbnailer(product.easy_image).get_thumbnail(
        {'size': (100, 100)})
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    product.delete()
    assert not os.path.exists(pic1['path'])
    assert not os.path.exists(thumbnail_path)
