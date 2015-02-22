# coding: utf-8
import pytest
from flexmock import flexmock
from .models import Product
from django_cleanup.signals import cleanup_pre_delete, cleanup_post_delete


@pytest.mark.django_db
def test_replace_file():
    product = Product.objects.create(image='123.png')
    flexmock(product.image.storage).should_receive('exists').and_return(True).once()
    flexmock(product.image.storage).should_call('delete').with_args('123.png').once()
    product.image = 'new.png'
    product.save()

@pytest.mark.django_db
def test_remove_model_instance():
    product = Product.objects.create(image='123.png')
    flexmock(product.image.storage).should_receive('exists').and_return(True).once()
    flexmock(product.image.storage).should_call('delete').with_args('123.png').once()
    product.delete()

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
