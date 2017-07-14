# coding: utf-8
''' Our local cache of filefields and some workarounds, everything is private to
    this package.'''
from __future__ import unicode_literals

from collections import defaultdict

from django.apps import apps
from django.db import models
from django.utils import six
from django.utils.module_loading import import_string


CACHE_NAME = '_django_cleanup_original_cache'


def fields_default():
    return set()
FIELDS = defaultdict(fields_default)


def fields_dict_default():
    return {}
FIELDS_FIELDS = defaultdict(fields_dict_default)
FIELDS_STORAGE = defaultdict(fields_dict_default)
if six.PY3:
    DOTTED_PATH = '{klass.__module__}.{klass.__qualname__}'
else:
    DOTTED_PATH = '{klass.__module__}.{klass.__name__}'


# cache init ##


def prepare():
    '''Prepare the cache for all models, non-reentrant'''
    if len(FIELDS) > 0:  # pragma: no cover
        return

    for model in apps.get_models():
        opts = model._meta
        name = get_model_name(model)
        if model_has_filefields(name):  # pragma: no cover
            return
        for field in opts.get_fields():
            if isinstance(field, models.FileField):
                add_field_for_model(name, field.name, field)


def add_field_for_model(model_name, field_name, field):
    '''Centralized function to make all our local caches.'''
    # store models that have filefields and the field names
    FIELDS[model_name].add(field_name)
    # store the dotted path of the field class for each field
    # in case we need to restore it later on
    FIELDS_FIELDS[model_name][field_name] = get_dotted_path(field)
    # also store the dotted path of the storage for the same reason
    FIELDS_STORAGE[model_name][field_name] = get_dotted_path(field.storage)


# work arounds ##


def get_field_instance(instance, field_name, using=None):
    '''
        Fieldfile sometimes references the wrong instance, correct this.
        Used in the `fallback_pre_save` and to fix Django Bug #25547

        Can use the `using` kwarg to change the instance that the `FieldFile`
        will receive.
    '''
    if using is None:  # pragma: no cover
        using = instance
    fieldfile = getattr(instance, field_name, None)
    # next line fixes the bug in django 1.8, remove when 1.8 dropped
    fieldfile.instance = using
    return fieldfile.__class__(using, fieldfile.field, fieldfile.name)


# generators ##


def get_fields_for_model(model_name, exclude=None):
    '''Get the filefields for a model if it has them'''
    if model_has_filefields(model_name):
        fields = FIELDS[model_name]

        if exclude is not None:
            assert isinstance(exclude, set)
            fields = fields.difference(exclude)

        for field_name in fields:
            yield field_name


def fields_for_model_instance(instance, using=None):
    '''
        Yields (name, descriptor) for each file field given an instance

        Can use the `using` kwarg to change the instance that the `FieldFile`
        will receive.
    '''
    if using is None:
        using = instance
    model_name = get_model_name(instance)

    deferred_fields = instance.get_deferred_fields()

    for field_name in get_fields_for_model(model_name, exclude=deferred_fields):
        fieldfile = get_field_instance(instance, field_name, using=using)
        yield field_name, fieldfile.__class__(using, fieldfile.field, fieldfile.name)


# restore ##


def get_field(model_name, field_name):
    '''Restore a field from its dotted path'''
    return import_string(FIELDS_FIELDS[model_name][field_name])


def get_field_storage(model_name, field_name):
    '''Restore a storage from its dotted path'''
    return import_string(FIELDS_STORAGE[model_name][field_name])


# utilities ##


def get_dotted_path(object_):
    '''get the dotted path for an object'''
    return DOTTED_PATH.format(klass=object_.__class__)


def get_model_name(model):
    '''returns a unique model name'''
    return '{opt.app_label}.{opt.model_name}'.format(opt=model._meta)


# booleans ##


def model_has_filefields(model_name):
    '''Check if a model has filefields'''
    return model_name in FIELDS


# instance functions ##


def remove_instance_cache(instance):
    '''Remove the cache from an instance'''
    if has_cache(instance):
        delattr(instance, CACHE_NAME)


def make_cleanup_cache(instance, source=None):
    '''
        Make the cleanup cache for an instance.

        Can also change the source of the data with the `source` kwarg.
    '''

    if source is None:
        source = instance
    setattr(instance, CACHE_NAME, dict(
        fields_for_model_instance(source, using=instance)))


def has_cache(instance):
    '''Check if an instance has a cache on it'''
    return hasattr(instance, CACHE_NAME)


def get_field_attr(instance, field_name):
    '''Get a value from the cache on an instance'''
    return getattr(instance, CACHE_NAME)[field_name]


# data sharing ##


def cleanup_models():
    '''Get all the models we have in the FIELDS cache'''
    for model_name in FIELDS:
        yield apps.get_model(model_name)


def cleanup_fields():
    '''Get a copy of the FIELDS cache'''
    return FIELDS.copy()
