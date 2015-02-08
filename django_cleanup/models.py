import os
import logging
import django
from django.db import models
from django.db.models.signals import pre_save, post_delete

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

def remove_old_files(sender, instance, **kwargs):
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
        new_file = getattr(instance, field.name)
        if old_file != new_file:
            delete_file(old_file)

def remove_files(sender, instance, **kwargs):
    for field in instance._meta.fields:
        if not isinstance(field, models.FileField):
            continue
        file_to_delete = getattr(instance, field.name)
        delete_file(file_to_delete)

def delete_file(file_):
    if not file_.name:
        return
    storage = file_.storage
    if storage and storage.exists(file_.name):
        try:
            cleanup_pre_delete.send(sender=None, file=file_)
            storage.delete(file_.name)
            cleanup_post_delete.send(sender=None, file=file_)
        except Exception:
            logger.exception("Unexpected exception while attempting to delete file '%s'" % file_.name)

def connect_signals():
    for model in find_models_with_filefield():
        pre_save.connect(remove_old_files, sender=model)
        post_delete.connect(remove_files, sender=model)


if django.VERSION < (1, 7):
    connect_signals()
