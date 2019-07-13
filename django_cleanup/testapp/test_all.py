# coding: utf-8
from __future__ import unicode_literals

import logging
import os
import re
import sys

from django.conf import settings
from django.db import transaction
from django.db.models.fields import files

import pytest

from django_cleanup import cache, handlers

from . import storage
from .models.app import Product, ProductIgnore, ProductProxy, ProductUnmanaged
from .testing_helpers import get_using, pic1, random_pic


PY3 = sys.version_info[0] == 3

LINE = re.compile(r'line \d{1,3}')

TB = '''Traceback (most recent call last):
  File "{handlers}", line xxx, in run_on_commit
    file_.delete(save=False)
  File "{files}", line xxx, in delete
    self.storage.delete(self.name)
  File "{storage}", line xxx, in delete
    os.remove(name)
{error}: [Errno 2] No such file or directory: '{{pic1}}\''''

if PY3:
    import pickle
else:
    import cPickle as pickle


def getTraceback():
    if PY3:
        fileabspath = os.path.abspath
        error = 'FileNotFoundError'
    else:
        fileabspath = lambda x: os.path.abspath(x).replace('.pyc', '.py')
        error = 'OSError'

    return TB.format(
        handlers=fileabspath(handlers.__file__),
        files=fileabspath(files.__file__),
        storage=fileabspath(storage.__file__),
        error=error)


def _raise(message):
    def _func(x):  # pragma: no cover
        raise Exception(message)
    return _func


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
    product_deferred = Product.objects.defer('image_default').get(id=product.id)
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
def test_remove_model_instance_default(pic1):
    product = Product.objects.create()
    assert product.image_default == pic1['srcpath']
    assert product.image_default_callable == pic1['srcpath']
    assert os.path.exists(pic1['srcpath'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert os.path.exists(pic1['srcpath'])


@pytest.mark.django_db(transaction=True)
def test_replace_file_with_file_default(pic1):
    product = Product.objects.create()
    assert os.path.exists(pic1['srcpath'])
    randomPic1 = random_pic()
    randomPic2 = random_pic()
    product.image_default = randomPic1
    product.image_default_callable = randomPic2
    with transaction.atomic(get_using(product)):
        product.save()
    assert os.path.exists(pic1['srcpath'])


@pytest.mark.django_db(transaction=True)
def test_remove_model_instance_ignore(pic1):
    product = ProductIgnore.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert os.path.exists(pic1['path'])


@pytest.mark.django_db(transaction=True)
def test_replace_file_with_file_ignore(pic1):
    product = ProductIgnore.objects.create(image=pic1['filename'])
    assert os.path.exists(pic1['path'])
    randomPic = random_pic()
    product.image = randomPic
    with transaction.atomic(get_using(product)):
        product.save()
    assert os.path.exists(pic1['path'])
    assert product.image
    new_image_path = os.path.join(settings.MEDIA_ROOT, randomPic)
    assert product.image.path == new_image_path


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
    product_deferred = Product.objects.defer('image_default').get(id=product.id)
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
