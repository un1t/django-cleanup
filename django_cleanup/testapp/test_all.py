import logging
import os
import pickle
import re

from django.conf import settings
from django.db import transaction
from django.db.models.fields import files

import pytest

from django_cleanup import cache, handlers

from . import storage
from .models.app import (
    BranchProduct, Product, ProductIgnore, ProductProxy, ProductUnmanaged, RootProduct)
from .testing_helpers import get_random_pic_name, get_using, picture


LINE = re.compile(r'line \d{1,3}')

TB = '''Traceback (most recent call last):
  File "{handlers}", line xxx, in run_on_commit
    file_.delete(save=False)
  File "{files}", line xxx, in delete
    self.storage.delete(self.name)
  File "{storage}", line xxx, in delete
    os.remove(name)
{error}: [Errno 2] No such file or directory: '{{picture}}\''''



def getTraceback():
    fileabspath = os.path.abspath
    error = 'FileNotFoundError'

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
def test_refresh_from_db_without_refresh(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.refresh_from_db()
    assert id(product.image.instance) == id(product)
    product.image = get_random_pic_name()
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])


@pytest.mark.django_db(transaction=True)
def test_cache_gone(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.image = get_random_pic_name()
    cache.remove_instance_cache(product)
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])


@pytest.mark.django_db(transaction=True)
def test_storage_gone(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.image = get_random_pic_name()
    product = pickle.loads(pickle.dumps(product))
    assert hasattr(product.image, 'storage')
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])


@pytest.mark.django_db(transaction=True)
def test_replace_file_with_file(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    random_pic_name = get_random_pic_name()
    product.image = random_pic_name
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])
    assert product.image
    new_image_path = os.path.join(settings.MEDIA_ROOT, random_pic_name)
    assert product.image.path == new_image_path


@pytest.mark.django_db(transaction=True)
def test_replace_file_with_blank(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.image = ''
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])
    assert not product.image
    assert product.image.name == ''


@pytest.mark.django_db(transaction=True)
def test_replace_file_with_none(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.image = None
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])
    assert not product.image
    assert product.image.name is None


@pytest.mark.django_db(transaction=True)
def test_replace_file_proxy(picture):
    product = ProductProxy.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.image = get_random_pic_name()
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])


@pytest.mark.django_db(transaction=True)
def test_replace_file_unmanaged(picture):
    product = ProductUnmanaged.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.image = get_random_pic_name()
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])


@pytest.mark.django_db(transaction=True)
def test_replace_file_deferred(picture):
    '''probably shouldn't save from a deferred model but someone might do it'''
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product_deferred = Product.objects.defer('image_default').get(id=product.id)
    product_deferred.image = get_random_pic_name()
    with transaction.atomic(get_using(product)):
        product_deferred.save()
    assert not os.path.exists(picture['path'])


@pytest.mark.django_db(transaction=True)
def test_remove_model_instance(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(picture['path'])


@pytest.mark.django_db(transaction=True)
def test_remove_model_instance_default(picture):
    product = Product.objects.create()
    assert product.image_default.path == picture['srcpath']
    assert product.image_default_callable.path == picture['srcpath']
    assert os.path.exists(picture['srcpath'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert os.path.exists(picture['srcpath'])


@pytest.mark.django_db(transaction=True)
def test_replace_file_with_file_default(picture):
    product = Product.objects.create()
    assert os.path.exists(picture['srcpath'])
    random_pic_name1 = get_random_pic_name()
    random_pic_name2 = get_random_pic_name()
    product.image_default = random_pic_name1
    product.image_default_callable = random_pic_name2
    with transaction.atomic(get_using(product)):
        product.save()
    assert os.path.exists(picture['srcpath'])


@pytest.mark.django_db(transaction=True)
def test_remove_model_instance_ignore(picture):
    product = ProductIgnore.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert os.path.exists(picture['path'])


@pytest.mark.django_db(transaction=True)
def test_replace_file_with_file_ignore(picture):
    product = ProductIgnore.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    random_pic_name = get_random_pic_name()
    product.image = random_pic_name
    with transaction.atomic(get_using(product)):
        product.save()
    assert os.path.exists(picture['path'])
    assert product.image
    new_image_path = os.path.join(settings.MEDIA_ROOT, random_pic_name)
    assert product.image.path == new_image_path


@pytest.mark.django_db(transaction=True)
def test_remove_model_instance_proxy(picture):
    product = ProductProxy.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(picture['path'])


@pytest.mark.django_db(transaction=True)
def test_remove_model_instance_unmanaged(picture):
    product = ProductUnmanaged.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(picture['path'])


@pytest.mark.django_db(transaction=True)
def test_remove_model_instance_deferred(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product_deferred = Product.objects.defer('image_default').get(id=product.id)
    with transaction.atomic(get_using(product)):
        product_deferred.delete()
    assert not os.path.exists(picture['path'])


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
def test_exception_on_save(settings, picture, caplog):
    settings.DEFAULT_FILE_STORAGE = 'django_cleanup.testapp.storage.DeleteErrorStorage'
    product = Product.objects.create(image=picture['filename'])
    # simulate a fieldfile that has a storage that raises a filenotfounderror on delete
    assert os.path.exists(picture['path'])
    product.image.delete(save=False)
    product.image = None
    assert not os.path.exists(picture['path'])
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])

    for record in caplog.records:
        assert LINE.sub('line xxx', record.exc_text) == getTraceback().format(picture=picture['path'])
    assert caplog.record_tuples == [
        (
            'django_cleanup.handlers',
            logging.ERROR,
            'There was an exception deleting the file `{}` on field `testapp.product.image`'.format(
                picture['filename'])
        )
    ]


@pytest.mark.django_db(transaction=True)
def test_cascade_delete(picture):
    root = RootProduct.objects.create()
    branch = BranchProduct.objects.create(root=root, image=picture['filename'])
    assert os.path.exists(picture['path'])
    root = RootProduct.objects.get()
    with transaction.atomic(get_using(root)):
        root.delete()
    assert not os.path.exists(picture['path'])
