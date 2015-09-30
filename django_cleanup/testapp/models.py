# coding: utf-8
from __future__ import unicode_literals

from django.db import models
from sorl.thumbnail import ImageField
from easy_thumbnails.fields import ThumbnailerImageField
from django_cleanup.signals import cleanup_pre_delete, cleanup_post_delete


class ProductAbstract(models.Model):
    image = models.FileField(upload_to='testapp', blank=True, null=True)
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

cleanup_pre_delete.connect(sorl_delete)
