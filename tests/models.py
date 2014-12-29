from django.db import models


class TestModel1(models.Model):
    test_file = models.FileField(upload_to="test")


class TestModel2(models.Model):
    name = models.CharField(max_length=10)
