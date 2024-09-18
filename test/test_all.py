import logging
import os
import pickle
import re
import tempfile

from django.conf import settings as django_settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models.fields import NOT_PROVIDED, files

import pytest

from django_cleanup import cache, handlers
from django_cleanup.signals import cleanup_post_delete, cleanup_pre_delete

from . import storage
from .models.app import (
    BranchProduct, Product, ProductIgnore, ProductProxy, ProductUnmanaged, RootProduct)
from .testing_helpers import get_random_pic_name, get_using


LINE = re.compile(r'line \d{1,3}')

TB = '''Traceback (most recent call last):
  File "{handlers}", line xxx, in run_on_commit
    file_.delete(save=False)
  File "{files}", line xxx, in delete
    self.storage.delete(self.name)
  File "{storage}", line xxx, in delete
    os.remove(name)
{error}: [Errno 2] No such file or directory: '{{picture}}\''''



def get_traceback(picture):
    fileabspath = os.path.abspath
    error = 'FileNotFoundError'

    return f'''Traceback (most recent call last):
  File "{fileabspath(handlers.__file__)}", line xxx, in run_on_commit
    file_.delete(save=False)
  File "{fileabspath(files.__file__)}", line xxx, in delete
    self.storage.delete(self.name)
  File "{fileabspath(storage.__file__)}", line xxx, in delete
    os.remove(name)
{error}: [Errno 2] No such file or directory: '{picture}\''''


def _raise(message):
    def _func(x):  # pragma: no cover
        raise Exception(message)
    return _func


def test_refresh_from_db_without_refresh(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.refresh_from_db()
    assert id(product.image.instance) == id(product)
    product.image = get_random_pic_name()
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])


def test_cache_gone(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.image = get_random_pic_name()
    cache.remove_instance_cache(product)
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])


def test_storage_gone(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.image = get_random_pic_name()
    product = pickle.loads(pickle.dumps(product))
    assert hasattr(product.image, 'storage')
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])


def test_replace_file_with_file(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    random_pic_name = get_random_pic_name()
    product.image = random_pic_name
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])
    assert product.image
    new_image_path = os.path.join(django_settings.MEDIA_ROOT, random_pic_name)
    assert product.image.path == new_image_path


def test_replace_file_with_blank(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.image = ''
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])
    assert not product.image
    assert product.image.name == ''


def test_replace_file_with_none(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.image = None
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])
    assert not product.image
    assert product.image.name is None


def test_replace_file_proxy(picture):
    product = ProductProxy.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.image = get_random_pic_name()
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])


def test_replace_file_unmanaged(picture):
    product = ProductUnmanaged.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product.image = get_random_pic_name()
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])


def test_replace_file_deferred(picture):
    '''probably shouldn't save from a deferred model but someone might do it'''
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product_deferred = Product.objects.defer('image_default').get(id=product.id)
    product_deferred.image = get_random_pic_name()
    with transaction.atomic(get_using(product)):
        product_deferred.save()
    assert not os.path.exists(picture['path'])


def test_remove_model_instance(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(picture['path'])


def test_remove_model_instance_default(picture):
    product = Product.objects.create()
    assert product.image_default.path == picture['srcpath']
    assert product.image_default_callable.path == picture['srcpath']
    assert os.path.exists(picture['srcpath'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert os.path.exists(picture['srcpath'])


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


def test_remove_model_instance_ignore(picture):
    product = ProductIgnore.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert os.path.exists(picture['path'])


def test_replace_file_with_file_ignore(picture):
    product = ProductIgnore.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    random_pic_name = get_random_pic_name()
    product.image = random_pic_name
    with transaction.atomic(get_using(product)):
        product.save()
    assert os.path.exists(picture['path'])
    assert product.image
    new_image_path = os.path.join(django_settings.MEDIA_ROOT, random_pic_name)
    assert product.image.path == new_image_path


def test_remove_model_instance_proxy(picture):
    product = ProductProxy.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(picture['path'])


def test_remove_model_instance_unmanaged(picture):
    product = ProductUnmanaged.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    with transaction.atomic(get_using(product)):
        product.delete()
    assert not os.path.exists(picture['path'])


def test_remove_model_instance_deferred(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    product_deferred = Product.objects.defer('image_default').get(id=product.id)
    with transaction.atomic(get_using(product)):
        product_deferred.delete()
    assert not os.path.exists(picture['path'])


def test_remove_blank_file(monkeypatch):
    product = Product.objects.create(image='')
    monkeypatch.setattr(
        product.image.storage, 'exists', _raise('should not call exists'))
    monkeypatch.setattr(
        product.image.storage, 'delete', _raise('should not call delete'))
    with transaction.atomic(get_using(product)):
        product.delete()


def test_remove_not_exists():
    product = Product.objects.create(image='no-such-file')
    with transaction.atomic(get_using(product)):
        product.delete()


def test_remove_none(monkeypatch):
    product = Product.objects.create(image=None)
    monkeypatch.setattr(
        product.image.storage, 'exists', _raise('should not call exists'))
    monkeypatch.setattr(
        product.image.storage, 'delete', _raise('should not call delete'))
    with transaction.atomic(get_using(product)):
        product.delete()


@pytest.mark.django_storage(default='test.storage.DeleteErrorStorage')
def test_exception_on_save(picture, caplog):
    filename = picture['filename']
    product = Product.objects.create(image=filename)
    # simulate a fieldfile that has a storage that raises a filenotfounderror on delete
    assert os.path.exists(picture['path'])
    product.image.delete(save=False)
    product.image = None
    assert not os.path.exists(picture['path'])
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])

    for record in caplog.records:
        assert LINE.sub('line xxx', record.exc_text) == get_traceback(picture['path'])
    assert caplog.record_tuples == [
        (
            'django_cleanup.handlers',
            logging.ERROR,
            f'There was an exception deleting the file `{filename}` on field `test.product.image`'
        )
    ]


def test_cascade_delete(picture):
    root = RootProduct.objects.create()
    branch = BranchProduct.objects.create(root=root, image=picture['filename'])
    assert os.path.exists(picture['path'])
    root = RootProduct.objects.get()
    with transaction.atomic(get_using(root)):
        root.delete()
    assert not os.path.exists(picture['path'])


def test_file_exists_on_create_and_update():
    # If a filepath is specified which already exists,
    # the FileField generates a random suffix to choose a different location.
    # We need to make sure, that we fetch this change and would delete the correct one
    # on further edits or the final deletion.
    # In this test case it is simulated by using a temporary file located
    # directly within the same directory as the image would be uploaded to.

    upload_to = Product._meta.get_field("image").upload_to
    dst_directory = os.path.join(django_settings.MEDIA_ROOT, upload_to)
    if not os.path.isdir(dst_directory):
        os.makedirs(dst_directory)

    # create the new product with a file to simulate an "upload"
    # a file aleady exists so the new file is renamed then saved
    with tempfile.NamedTemporaryFile(prefix="f1__", dir=dst_directory) as f1:
        with transaction.atomic():
            product = Product.objects.create(
                image=File(f1, name=os.path.join(upload_to, os.path.basename(f1.name))))

        assert f1.name != product.image.path
        assert os.path.exists(f1.name)
        assert os.path.exists(product.image.path)

        path_prior_to_edit = product.image.path

        # edit the product to change the product file to a different file
        # check that it deletes the renamed file, not the original existing file
        with tempfile.NamedTemporaryFile(prefix="f2__", dir=dst_directory) as f2:
            with transaction.atomic(get_using(product)):
                product.image = File(f2, name=os.path.join(upload_to, os.path.basename(f2.name)))
                assert f2.name == product.image.path
                product.save()

            assert f1.name != product.image.path
            assert os.path.exists(f1.name)
            assert f2.name != product.image.path
            assert os.path.isfile(f2.name)
            assert os.path.isfile(product.image.path)
            assert not os.path.isfile(path_prior_to_edit)

            with transaction.atomic(get_using(product)):
                product.delete()

            assert os.path.isfile(f1.name)
            assert os.path.isfile(f2.name)
            assert not os.path.isfile(product.image.path)


def test_signals(picture):
    prekwargs = {}
    postkwargs = {}
    def assn_prekwargs(**kwargs):
        nonlocal prekwargs
        prekwargs = kwargs

    def assn_postkwargs(**kwargs):
        nonlocal postkwargs
        postkwargs = kwargs

    cleanup_pre_delete.connect(
        assn_prekwargs, dispatch_uid='pre_test_replace_file_with_file_signals')
    cleanup_post_delete.connect(
        assn_postkwargs, dispatch_uid='post_test_replace_file_with_file_signals')
    product = Product.objects.create(image=picture['filename'])
    random_pic_name = get_random_pic_name()
    product.image = random_pic_name
    with transaction.atomic(get_using(product)):
        product.save()

    assert prekwargs['deleted'] is False
    assert prekwargs['updated'] is True
    assert prekwargs['instance'] == product
    assert prekwargs['file'] is not None
    assert prekwargs['file_name'] == picture['filename']
    assert isinstance(prekwargs['default_file_name'], NOT_PROVIDED)
    assert prekwargs['model_name'] == 'test.product'
    assert prekwargs['field_name'] == 'image'

    assert postkwargs['deleted'] is False
    assert postkwargs['updated'] is True
    assert postkwargs['instance'] == product
    assert postkwargs['file'] is not None
    assert postkwargs['file_name'] == picture['filename']
    assert isinstance(postkwargs['default_file_name'], NOT_PROVIDED)
    assert postkwargs['model_name'] == 'test.product'
    assert postkwargs['field_name'] == 'image'
    assert postkwargs['success'] is True
    assert postkwargs['error'] is None

    with transaction.atomic(get_using(product)):
        product.delete()

    assert prekwargs['deleted'] is True
    assert prekwargs['updated'] is False
    assert prekwargs['instance'] == product
    assert prekwargs['file'] is not None
    assert prekwargs['file_name'] == random_pic_name
    assert isinstance(prekwargs['default_file_name'], NOT_PROVIDED)
    assert prekwargs['model_name'] == 'test.product'
    assert prekwargs['field_name'] == 'image'

    assert postkwargs['deleted'] is True
    assert postkwargs['updated'] is False
    assert postkwargs['instance'] == product
    assert postkwargs['file'] is not None
    assert postkwargs['file_name'] == random_pic_name
    assert isinstance(postkwargs['default_file_name'], NOT_PROVIDED)
    assert postkwargs['model_name'] == 'test.product'
    assert postkwargs['field_name'] == 'image'
    print(postkwargs['error'])
    assert postkwargs['success'] is True
    assert postkwargs['error'] is None

    cleanup_pre_delete.disconnect(None, dispatch_uid='pre_test_replace_file_with_file_signals')
    cleanup_post_delete.disconnect(None, dispatch_uid='post_test_replace_file_with_file_signals')


#region select config
@pytest.mark.cleanup_selected_config
def test__select_config__replace_file_with_file(picture):
    product = Product.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    random_pic_name = get_random_pic_name()
    product.image = random_pic_name
    with transaction.atomic(get_using(product)):
        product.save()
    assert not os.path.exists(picture['path'])
    assert product.image
    new_image_path = os.path.join(django_settings.MEDIA_ROOT, random_pic_name)
    assert product.image.path == new_image_path


@pytest.mark.cleanup_selected_config
def test__select_config__replace_file_with_file_ignore(picture):
    product = ProductIgnore.objects.create(image=picture['filename'])
    assert os.path.exists(picture['path'])
    random_pic_name = get_random_pic_name()
    product.image = random_pic_name
    with transaction.atomic(get_using(product)):
        product.save()
    assert os.path.exists(picture['path'])
    assert product.image
    new_image_path = os.path.join(django_settings.MEDIA_ROOT, random_pic_name)
    assert product.image.path == new_image_path
#endregion
