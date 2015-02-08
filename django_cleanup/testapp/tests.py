# coding: utf-8
from django.test import TestCase
from .models import Product


class CleanupTest(TestCase):

     def test_remove_blank_file(self):
        product = Product.objects.create(image='')
        product.delete()

     def test_remove_not_exists(self):
        product = Product.objects.create(image='no-such-file.png')
        product.delete()
