# coding: utf-8
import os
import shutil
import pytest
from flexmock import flexmock
from django.conf import settings
from django.db import router
from django.db import transaction
from django_cleanup.signals import cleanup_pre_delete, cleanup_post_delete
from .models import Product, ProductProxy, ProductUnmanaged


def get_using(instance):
    return router.db_for_write(instance.__class__, instance=instance)


def _raise(message):
    def _func(x):
        raise Exception(message)
    return _func


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


@pytest.mark.django_db(transaction=True)
def test_replace_file(pic1):
    product = Product.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product.image = 'new.jpg'
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])
    assert product.image
    new_image_path = os.path.join(settings.MEDIA_ROOT, 'new.jpg')
    assert product.image.path == new_image_path


@pytest.mark.django_db(transaction=True)
def test_replace_file_proxy(pic1):
    product = ProductProxy.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product.image = 'new.jpg'
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db(transaction=True)
def test_replace_file_unmanaged(pic1):
    product = ProductUnmanaged.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product.image = 'new.jpg'
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db(transaction=True)
@pytest.mark.xfail(reason='https://code.djangoproject.com/ticket/18100')
def test_replace_file_deferred(pic1):
    '''probably shouldn't save from a deferred model but someone might do it'''
    product = Product.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product_deferred = Product.objects.defer('sorl_image').get(id=product.id)
    product_deferred.image = 'new.jpg'
    with transaction.atomic(get_using(product)):
        product_deferred.save()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db(transaction=True)
def test_remove_model_instance(pic1):
    product = Product.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db(transaction=True)
def test_remove_model_instance_proxy(pic1):
    product = ProductProxy.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db(transaction=True)
def test_remove_model_instance_unmanaged(pic1):
    product = ProductUnmanaged.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db(transaction=True)
@pytest.mark.xfail(reason='https://code.djangoproject.com/ticket/18100')
def test_remove_model_instance_deferred(pic1):
    product = Product.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product_deferred = Product.objects.defer('sorl_image').get(id=product.id)
    with transaction.atomic(get_using(product)):
        product_deferred.delete()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db(transaction=True)
def test_remove_blank_file(monkeypatch):
    product = Product.objects.create(image='')
    monkeypatch.setattr(
        product.image.storage, 'exists', _raise('should not call exists'))
    monkeypatch.setattr(
        product.image.storage, 'delete', _raise('should not call delete'))
    with transaction.atomic(get_using(product)):
        product.delete()


@pytest.mark.django_db(transaction=True)
def test_remove_not_exists():
    product = Product.objects.create(image='no-such-file')
    with transaction.atomic(get_using(product)):
        product.delete()


@pytest.mark.django_db(transaction=True)
def test_remove_none(monkeypatch):
    product = Product.objects.create(image=None)
    monkeypatch.setattr(
        product.image.storage, 'exists', _raise('should not call exists'))
    monkeypatch.setattr(
        product.image.storage, 'delete', _raise('should not call delete'))
    with transaction.atomic(get_using(product)):
        product.delete()


@pytest.mark.django_db(transaction=True)
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
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])
    assert not os.path.exists(thumbnail_path)


@pytest.mark.django_db(transaction=True)
def test_sorlthumbnail_delete(pic1):
    # https://github.com/mariocesar/sorl-thumbnail
    from sorl.thumbnail import get_thumbnail
    product = Product.objects.create(sorl_image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    im = get_thumbnail(
        product.sorl_image, '100x100', crop='center', quality=50)
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(pic1['path'])
    assert not os.path.exists(thumbnail_path)


@pytest.mark.django_db(transaction=True)
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
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])
    assert not os.path.exists(thumbnail_path)


@pytest.mark.django_db(transaction=True)
def test_easythumbnails_delete(pic1):
    # https://github.com/SmileyChris/easy-thumbnails
    from easy_thumbnails.files import get_thumbnailer
    product = Product.objects.create(easy_image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    im = get_thumbnailer(product.easy_image).get_thumbnail(
        {'size': (100, 100)})
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, im.name)
    assert os.path.exists(thumbnail_path)
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(pic1['path'])
    assert not os.path.exists(thumbnail_path)
