# coding: utf-8
from __future__ import unicode_literals

import logging
import os
import random
import re
import shutil
import string

import django
from django.conf import settings
from django.db import router, transaction
from django.db.models.fields import files
from django.utils import six
from django.utils.six.moves import cPickle as pickle

import pytest

from django_cleanup import cache, cleanup, handlers
from django_cleanup.signals import cleanup_pre_delete

from . import storage
from .models import Product, ProductProxy, ProductUnmanaged, sorl_delete


LINE = re.compile(r'line \d{1,3}')

TB = '''Traceback (most recent call last):
  File "{handlers}", line xxx, in run_on_commit
    file_.delete(save=False)
  File "{files}", line xxx, in delete
    self.storage.delete(self.name)
  File "{storage}", line xxx, in delete
    os.remove(name)
{error}: [Errno 2] No such file or directory: '{{pic1}}\''''


def getTraceback():
    if six.PY2:
        fileabspath = lambda x : os.path.abspath(x).replace('.pyc', '.py')
        error = 'OSError'
    else:
        fileabspath = os.path.abspath
        error = 'FileNotFoundError'

    return TB.format(
        handlers=fileabspath(handlers.__file__),
        files=fileabspath(files.__file__),
        storage=fileabspath(storage.__file__),
        error=error)


def get_using(instance):
    return router.db_for_write(instance.__class__, instance=instance)


def _raise(message):
    def _func(x):  # pragma: no cover
        raise Exception(message)
    return _func


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
        'filename': os.path.split(dst)[-1]
    }
    if os.path.exists(dst):
        os.remove(dst)


@pytest.mark.django_db(transaction=True)
def test_refresh_from_db_without_refresh(pic1):
    product = Product.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product.refresh_from_db()
    assert id(product.image.instance) == id(product)
    product.image = random_pic()
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db(transaction=True)
def test_cache_gone(pic1):
    product = Product.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product.image = random_pic()
    cache.remove_instance_cache(product)
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db(transaction=True)
def test_storage_gone(pic1):
    product = Product.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product.image = random_pic()
    product = pickle.loads(pickle.dumps(product))
    assert hasattr(product.image, 'storage')
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db(transaction=True)
def test_replace_file_with_file(pic1):
    product = Product.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    randomPic = random_pic()
    product.image = randomPic
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])
    assert product.image
    new_image_path = os.path.join(settings.MEDIA_ROOT, randomPic)
    assert product.image.path == new_image_path


@pytest.mark.django_db(transaction=True)
def test_replace_file_with_blank(pic1):
    product = Product.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product.image = ''
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])
    assert not product.image
    assert product.image.name == ''


@pytest.mark.django_db(transaction=True)
def test_replace_file_with_none(pic1):
    product = Product.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product.image = None
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])
    assert not product.image
    assert product.image.name is None


@pytest.mark.django_db(transaction=True)
def test_replace_file_proxy(pic1):
    product = ProductProxy.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product.image = random_pic()
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db(transaction=True)
def test_replace_file_unmanaged(pic1):
    product = ProductUnmanaged.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product.image = random_pic()
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])


@pytest.mark.django_db(transaction=True)
def test_replace_file_deferred(pic1):
    '''probably shouldn't save from a deferred model but someone might do it'''
    product = Product.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    product_deferred = Product.objects.defer('sorl_image').get(id=product.id)
    product_deferred.image = random_pic()
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
    cleanup_pre_delete.connect(sorl_delete)
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
    cleanup_pre_delete.disconnect(sorl_delete)


@pytest.mark.django_db(transaction=True)
def test_sorlthumbnail_delete(pic1):
    # https://github.com/mariocesar/sorl-thumbnail
    cleanup_pre_delete.connect(sorl_delete)
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
    cleanup_pre_delete.disconnect(sorl_delete)


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


@pytest.mark.django_db(transaction=True)
def test_exception_on_save(settings, pic1, caplog):
    settings.DEFAULT_FILE_STORAGE = 'django_cleanup.testapp.storage.DeleteErrorStorage'
    product = Product.objects.create(image=pic1['filename'])
    # simulate a fieldfile that has a storage that raises a filenotfounderror on delete
    assert os.path.exists(pic1['path'])
    product.image.delete(save=False)
    product.image = None
    assert not os.path.exists(pic1['path'])
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(pic1['path'])

    for record in caplog.records:
        assert LINE.sub('line xxx', record.exc_text) == getTraceback().format(pic1=pic1['path'])
    assert caplog.record_tuples == [
        (
            'django_cleanup.handlers',
            logging.ERROR,
            'There was an exception deleting the file `{}` on field `testapp.product.image`'.format(
                pic1['filename'])
        )
    ]
