from django.db import models


class Product(models.Model):
     image = models.ImageField(upload_to='testapp', blank=True)
