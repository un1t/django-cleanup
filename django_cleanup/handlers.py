'''
    Signal handlers to manage FileField files.
'''
import logging

from django.db.models.signals import post_delete, post_init, post_save, pre_save
from django.db.transaction import on_commit

from . import cache
from .signals import cleanup_post_delete, cleanup_pre_delete


logger = logging.getLogger(__name__)


class FakeInstance:
    '''A Fake model instance to ensure an instance is not modified'''


def cache_original_post_init(sender, instance, **kwargs):
    '''Post_init on all models with file fields, saves original values'''
    cache.make_cleanup_cache(instance)


def fallback_pre_save(sender, instance, raw, update_fields, using, **kwargs):
    '''Fallback to the database to remake the cleanup cache if there is none'''
    if raw:  # pragma: no cover
        return

    if instance.pk and not cache.has_cache(instance):
        try:
            db_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:  # pragma: no cover
            return
        cache.make_cleanup_cache(instance, source=db_instance)


def delete_old_post_save(sender, instance, raw, created, update_fields, using,
                         **kwargs):
    '''Post_save on all models with file fields, deletes old files'''
    if raw or created:
        return

    for field_name, new_file in cache.fields_for_model_instance(instance):
        if update_fields is None or field_name in update_fields:
            old_file = cache.get_field_attr(instance, field_name)
            if old_file != new_file:
                delete_file(instance, field_name, old_file, using)

    # reset cache
    cache.make_cleanup_cache(instance)


def delete_all_post_delete(sender, instance, using, **kwargs):
    '''Post_delete on all models with file fields, deletes all files'''
    for field_name, file_ in cache.fields_for_model_instance(instance):
        delete_file(instance, field_name, file_, using)


def delete_file(instance, field_name, file_, using):
    '''Deletes a file'''

    if not file_.name:
        return

    # add a fake instance to the file being deleted to avoid
    # any changes to the real instance.
    file_.instance = FakeInstance()

    # pickled filefields lose lots of data, and contrary to how it is
    # documented, the file descriptor does not recover them

    model_name = cache.get_model_name(instance)

    # recover the 'field' if necessary
    if not hasattr(file_, 'field'):
        file_.field = cache.get_field(model_name, field_name)()
        file_.field.name = field_name

    # if our file name is default don't delete
    default = file_.field.default if not callable(file_.field.default) else file_.field.default()

    if file_.name == default:
        return

    # recover the 'storage' if necessary
    if not hasattr(file_, 'storage'):
        file_.storage = cache.get_field_storage(model_name, field_name)()

    # this will run after a successful commit
    # assuming you are in a transaction and on a database that supports
    # transactions, otherwise it will run immediately
    def run_on_commit():
        cleanup_pre_delete.send(sender=None, file=file_)
        try:
            file_.delete(save=False)
        except Exception:
            opts = instance._meta
            logger.exception(
                'There was an exception deleting the file `%s` on field `%s.%s.%s`',
                file_, opts.app_label, opts.model_name, field_name)
        cleanup_post_delete.send(sender=None, file=file_)

    on_commit(run_on_commit, using)


def connect():
    '''Connect signals to the cleanup models'''
    for model in cache.cleanup_models():
        key = '{{}}_django_cleanup_{}'.format(cache.get_model_name(model))
        post_init.connect(cache_original_post_init, sender=model,
                          dispatch_uid=key.format('post_init'))
        pre_save.connect(fallback_pre_save, sender=model,
                         dispatch_uid=key.format('pre_save'))
        post_save.connect(delete_old_post_save, sender=model,
                          dispatch_uid=key.format('post_save'))
        post_delete.connect(delete_all_post_delete, sender=model,
                            dispatch_uid=key.format('post_delete'))
