from easy_thumbnails.fields import ThumbnailerImageField
from sorl.thumbnail import ImageField

from .app import ProductAbstract


class ProductIntegrationAbstract(ProductAbstract):
    sorl_image = ImageField(upload_to='testapp', blank=True)
    easy_image = ThumbnailerImageField(upload_to='testapp', blank=True)

    class Meta:
        abstract = True


class ProductIntegration(ProductIntegrationAbstract):
    pass


def sorl_delete(**kwargs):
    from sorl.thumbnail import delete
    delete(kwargs['file'])
