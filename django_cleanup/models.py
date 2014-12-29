import os
import logging
import django
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.conf import settings

files_to_delete = []

logger = logging.getLogger(__name__)


def remove_file(file_obj):
    DJANGO_CLEANUP_DELETE_ON_MIDDLEWARE = getattr(settings, 'DJANGO_CLEANUP_DELETE_ON_MIDDLEWARE', False)
    if DJANGO_CLEANUP_DELETE_ON_MIDDLEWARE:
        files_to_delete.append(file_obj)
        return None

    storage = file_obj.storage
    if storage and storage.exists(file_obj.name):
        try:
            storage.delete(file_obj.name)
        except Exception:
            logger.exception("Unexpected exception while attempting to delete old file '%s'" % file_obj.name)


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
        if old_file and old_file != new_file:
            remove_file(old_file)


def remove_files(sender, instance, **kwargs):
    for field in instance._meta.fields:
        if not isinstance(field, models.FileField):
            continue
        file_to_delete = getattr(instance, field.name)

        if file_to_delete:
            remove_file(file_to_delete)


def connect_signals():
    for model in find_models_with_filefield():
        pre_save.connect(remove_old_files, sender=model)
        post_delete.connect(remove_files, sender=model)


if django.VERSION < (1, 7):
    connect_signals()
