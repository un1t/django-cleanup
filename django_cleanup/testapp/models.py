# coding: utf-8
from __future__ import unicode_literals

import os

from django.conf import settings
from django.db import models

from easy_thumbnails.fields import ThumbnailerImageField
from sorl.thumbnail import ImageField


def default_image():
    return os.path.join(settings.MEDIA_ROOT, 'pic.jpg')


class ProductAbstract(models.Model):
    image = models.FileField(upload_to='testapp', blank=True, null=True)
    image_default = models.FileField(
        upload_to='testapp', blank=True, null=True,
        default=(os.path.join(settings.MEDIA_ROOT, 'pic.jpg')))
    image_default_callable = models.FileField(
        upload_to='testapp', blank=True, null=True, default=default_image)
    sorl_image = ImageField(upload_to='testapp', blank=True)
    easy_image = ThumbnailerImageField(upload_to='testapp', blank=True)

    class Meta:
        abstract = True


class Product(ProductAbstract):
    pass


class ProductProxy(Product):
    class Meta:
        proxy = True


class ProductUnmanaged(ProductAbstract):
    id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'testapp_product'


def sorl_delete(**kwargs):
    from sorl.thumbnail import delete
    delete(kwargs['file'])
