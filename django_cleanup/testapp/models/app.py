from django.db import models

from django_cleanup import cleanup
from django_cleanup.cleanup import cleanup_ignore


def default_image():
    return 'pic.jpg'


# ignore this cleanup_ignore decorator
# it is only here to test that name mangling is in place
# so that ignores on parent classes don't impact subclasses
# and is not a demonstration on how to use this decorator
# see the ProductIgnore model below for how to use the decorator
@cleanup_ignore
class ProductAbstract(models.Model):
    image = models.FileField(upload_to='testapp', blank=True, null=True)
    image_default = models.FileField(
        upload_to='testapp', blank=True, null=True,
        default='pic.jpg')
    image_default_callable = models.FileField(
        upload_to='testapp', blank=True, null=True, default=default_image)

    class Meta:
        abstract = True


class Product(ProductAbstract):
    pass


@cleanup.ignore
class ProductIgnore(ProductAbstract):
    pass


class ProductProxy(Product):
    class Meta:
        proxy = True


class ProductUnmanaged(ProductAbstract):
    id = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'testapp_product'

class RootProduct(models.Model):
    pass

class BranchProduct(models.Model):
    root = models.ForeignKey(RootProduct, on_delete=models.CASCADE)
    image = models.FileField(upload_to='testapp', blank=True, null=True)
