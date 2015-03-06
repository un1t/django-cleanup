# coding: utf-8
from django.db import models
from sorl.thumbnail import ImageField
from easy_thumbnails.fields import ThumbnailerImageField
from django_cleanup.signals import cleanup_pre_delete, cleanup_post_delete


class Product(models.Model):
    image = models.FileField(upload_to='testapp', blank=True)
    sorl_image = ImageField(upload_to='testapp', blank=True)
    easy_image = ThumbnailerImageField(upload_to='testapp', blank=True)


def sorl_delete(**kwargs):
    from sorl.thumbnail import delete
    delete(kwargs['file'])

cleanup_pre_delete.connect(sorl_delete)
