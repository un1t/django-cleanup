import os
import logging
import django
from django.db import models
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete

from .signals import cleanup_pre_delete, cleanup_post_delete


logger = logging.getLogger(__name__)


def find_models_with_filefield():
    result = []
    for model in models.get_models():
        for field in model._meta.fields:
            if isinstance(field, models.FileField):
                result.append(model)
                break
    return result


def attach_old_files(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = instance.__class__.objects.get(pk=instance.pk)
    except instance.DoesNotExist:
        return

    for field in instance._meta.fields:
        if not isinstance(field, models.FileField):
            continue
        old_file = getattr(old_instance, field.name)
        setattr(instance, '_old_' + field.name, old_file)


def remove_old_files(sender, instance, **kwargs):
    if not instance.pk:
        return

    for field in instance._meta.fields:
        if not isinstance(field, models.FileField):
            continue
        old_file = getattr(instance, '_old_' + field.name, None)
        new_file = getattr(instance, field.name)
        if old_file and old_file != new_file:
            old_file.delete()


def remove_files(sender, instance, **kwargs):
    for field in instance._meta.fields:
        if not isinstance(field, models.FileField):
            continue
        file_to_delete = getattr(instance, field.name)
        file_to_delete.delete()


def connect_signals():
    for model in find_models_with_filefield():
        pre_save.connect(attach_old_files, sender=model)
        post_save.connect(remove_old_files, sender=model)
        pre_delete.connect(attach_old_files, sender=model)
        post_delete.connect(remove_files, sender=model)


if django.VERSION < (1, 7):
    connect_signals()
