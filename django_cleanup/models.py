import os
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.db.models.loading import cache


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

def remove_old_files(sender, instance, **kwargs):
    if not instance.id:
        return
    old_instance = instance.__class__.objects.get(id=instance.id)
    for field in instance._meta.fields:
        if not isinstance(field, models.FileField):
            continue
        old_file = getattr(old_instance, field.name)
        new_file = getattr(instance, field.name)
        if old_file and old_file != new_file and os.path.exists(old_file.path):
            try:
                os.remove(old_file.path)
            except OSError:
                pass

def remove_files(sender, instance, **kwargs):
    for field in instance._meta.fields:
        if not isinstance(field, models.FileField):
            continue
        file = getattr(instance, field.name)
        if file and os.path.exists(file.path):
            try:
                os.remove(file.path)
            except OSError:
                pass


for model in find_models_with_filefield():
    pre_save.connect(remove_old_files, sender=model)
    post_delete.connect(remove_files, sender=model)

