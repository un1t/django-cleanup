# coding: utf-8
from collections import defaultdict

import django
from django.db import models
try:
    from django.apps import apps
    get_models = apps.get_models
except (ImportError, AttributeError):
    # remove after dropping django 1.6
    get_models = models.get_models
try:
    from django.db.transaction import on_commit
except ImportError:
    # remove after django 1.8 is deprecated(which will be awhile since it's LTS)
    def on_commit(func, using=None):
        func()
from django.db.models.signals import post_init, post_save, post_delete

from .signals import cleanup_pre_delete, cleanup_post_delete

FIELDS_DEFAULT = lambda: []
FIELDS = defaultdict(FIELDS_DEFAULT)
CACHE_NAME = '_django_cleanup_original_cache'


def get_model_name(model):
    '''returns a unique model name'''
    return '{opt.app_label}.{opt.model_name}'.format(opt=model._meta)


def fields_for_model_instance(instance):
    '''Yields (name, descriptor) for each file field given an instance'''
    model_name = get_model_name(instance)
    if model_name in FIELDS:
        for field_name in FIELDS[model_name]:
            yield field_name, getattr(instance, field_name, None)


def ensure_get_fields(opts):
    ''' this can be removed when django 1.7 support is dropped'''
    if hasattr(opts, 'get_fields'):
        return opts
    def get_fields():
        return opts.fields
    opts.get_fields = get_fields
    return opts


def cache_original_post_init(sender, instance, **kwargs):
    '''Post_init on all models with file fields, saves original values'''
    setattr(instance, CACHE_NAME, dict(fields_for_model_instance(instance)))


def delete_old_post_save(sender, instance, raw, created, update_fields, using,
                         **kwargs):
    '''Post_save on all models with file fields, deletes old files'''
    if raw or created:
        return

    for field_name, new_file in fields_for_model_instance(instance):
        if update_fields is None or field_name in update_fields:
            old_file = getattr(instance, CACHE_NAME)[field_name]
            if old_file != new_file:
                delete_file(old_file, using)


def delete_all_post_delete(sender, instance, using, **kwargs):
    '''Post_delete on all models with file fields, deletes all files'''
    for field_name, file_ in fields_for_model_instance(instance):
        delete_file(file_, using)


def delete_file(file_, using):
    '''Deletes a file'''
    if not file_.name:
        return

    # this will run after a successful commit for django 1.9+
    # assuming you are in a transaction and on a database that supports
    # transactions, otherwise it will run immediately
    def run_on_commit():
        cleanup_pre_delete.send(sender=None, file=file_)
        file_.delete(save=False)
        cleanup_post_delete.send(sender=None, file=file_)

    on_commit(run_on_commit, using)


def connect_signals():
    if len(FIELDS) > 0:
            return

    def find_models_with_filefield():
        for model in get_models():
            opts = ensure_get_fields(model._meta)
            name = get_model_name(model)
            for field in opts.get_fields():
                if isinstance(field, models.FileField):
                    FIELDS[name].append(field.name)

            if name in FIELDS:
                yield model

    for model in find_models_with_filefield():
        key = '{{}}_django_cleanup_{}'.format(get_model_name(model))
        post_init.connect(cache_original_post_init, sender=model,
                          dispatch_uid=key.format('post_init'))
        post_save.connect(delete_old_post_save, sender=model,
                          dispatch_uid=key.format('post_save'))
        post_delete.connect(delete_all_post_delete, sender=model,
                            dispatch_uid=key.format('post_delete'))

if django.VERSION < (1, 7):
    connect_signals()
