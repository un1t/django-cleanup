# coding: utf-8
from flexmock import flexmock
from django.test import TestCase
from .models import Product


class CleanupTest(TestCase):

    def test_replace_file(self):
        product = Product.objects.create(image='123.png')
        flexmock(product.image.storage).should_receive('exists').and_return(True).times(1)
        flexmock(product.image.storage).should_call('delete').times(1)
        product.image = 'new.png'
        product.save()

    def test_remove_model_instance(self):
        product = Product.objects.create(image='123.png')
        flexmock(product.image.storage).should_receive('exists').and_return(True).times(1)
        flexmock(product.image.storage).should_call('delete').times(1)
        product.delete()

    def test_remove_blank_file(self):
        product = Product.objects.create(image='')
        flexmock(product.image.storage).should_call('exists').times(0)
        flexmock(product.image.storage).should_call('delete').times(0)
        product.delete()

    def test_remove_not_exists(self):
        product = Product.objects.create(image='no-such-file.png')
        flexmock(product.image.storage).should_receive('exists').and_return(False).times(1)
        product.delete()
