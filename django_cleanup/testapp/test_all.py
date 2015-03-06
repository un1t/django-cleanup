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
def test_remove_blank_file():
    product = Product.objects.create(image='')
    flexmock(product.image.storage).should_call('exists').times(0)
    flexmock(product.image.storage).should_call('delete').times(0)
    product.delete()


@pytest.mark.django_db
def test_remove_not_exists():
    product = Product.objects.create(image='no-such-file.png')
    flexmock(product.image.storage).should_receive('exists').and_return(False).once()
    flexmock(product.image.storage).should_call('delete').times(0)
    product.delete()


@pytest.mark.django_db
def test_signals():
    product = Product.objects.create(image='123.png')
    flexmock(product.image.storage).should_receive('exists').and_return(True).once().ordered()
    flexmock(cleanup_pre_delete).should_call('send').once().ordered()
    flexmock(product.image.storage).should_call('delete').once().ordered()
    flexmock(cleanup_post_delete).should_call('send').once().ordered()
    product.delete()
