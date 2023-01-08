'''Public utilities'''
from .cache import (
    get_mangled_ignore as _get_mangled_ignore, get_mangled_select as _get_mangled_select,
    make_cleanup_cache as _make_cleanup_cache)


__all__ = ['refresh', 'cleanup_ignore', 'cleanup_select']


def refresh(instance):
    '''Refresh the cache for an instance'''
    return _make_cleanup_cache(instance)


def ignore(cls):
    '''Mark a model to ignore for cleanup'''
    setattr(cls, _get_mangled_ignore(cls), None)
    return cls
cleanup_ignore = ignore


def select(cls):
    '''Mark a model to select for cleanup'''
    setattr(cls, _get_mangled_select(cls), None)
    return cls
cleanup_select = select
