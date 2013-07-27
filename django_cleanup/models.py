import os
import logging
from django.db import models
from django.db.models.signals import pre_save, post_delete, post_save
from django.db.models.loading import cache
from django.core.files.storage import get_storage_class

logger = logging.getLogger(__name__)

def find_models_with_filefield():
    result = []
    for app in cache.get_apps():
        model_list = cache.get_models(app)
        for model in model_list:
            for field in model._meta.fields:
                if isinstance(field, models.FileField):
                    result.append(model)
                    break
    return result

def set_old_instance(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        instance.old = instance.__class__.objects.get(pk=instance.pk)
    except instance.DoesNotExist:
        return

def update_old_files(sender, instance, **kwargs):
    for field in instance._meta.fields:
        if not isinstance(field, models.FileField):
            continue
        old_file = getattr(instance.old, field.name)

        try:
            old_file_thumbnail = old_file.thumbnail
        except AttributeError:
            old_file_thumbnail = None

        new_file = getattr(instance, field.name)

        try:
            new_file_thumbnail = new_file.thumbnail
        except AttributeError:
            new_file_thumbnail = None

        storage = old_file.storage
        if old_file and old_file != new_file and old_file.name != new_file.name and storage and storage.exists(old_file.name):
            try:
                storage.delete(old_file.name)
            except Exception:
                logger.exception("Unexpected exception while attempting to delete old file '%s'" % old_file.name)

        if old_file_thumbnail != None:
            storage = old_file_thumbnail.storage
            if old_file_thumbnail and old_file_thumbnail != new_file_thumbnail and old_file_thumbnail.name != new_file_thumbnail.name and storage and storage.exists(old_file_thumbnail.name):
                try:
                    storage.delete(old_file_thumbnail.name)
                except Exception:
                    logger.exception("Unexpected exception while attempting to delete old file '%s'" % old_file_thumbnail.name)

def remove_irrelevance_files(sender, instance, **kwargs):
    for field in instance._meta.fields:
        if not isinstance(field, models.FileField):
            continue
        file_to_delete = getattr(instance, field.name)

        try:
            thumb_to_delete = file_to_delete.thumbnail
        except AttributeError:
            thumb_to_delete = None

        storage = file_to_delete.storage
        if file_to_delete and storage and storage.exists(file_to_delete.name):
            try:
                storage.delete(file_to_delete.name)
            except Exception:
                logger.exception("Unexpected exception while attempting to delete file '%s'" % file_to_delete.name)

        if thumb_to_delete != None:
            storage = thumb_to_delete.storage
            if thumb_to_delete and storage and storage.exists(thumb_to_delete.name):
                try:
                    storage.delete(thumb_to_delete.name)
                except Exception:
                    logger.exception("Unexpected exception while attempting to delete file '%s'" % thumb_to_delete.name)

for model in find_models_with_filefield():
    pre_save.connect(set_old_instance, sender=model)
    post_save.connect(update_old_files, sender=model)
    post_delete.connect(remove_irrelevance_files, sender=model)
