'''Public utilities'''
from .cache import (
    get_mangled_ignore as _get_mangled_ignore, make_cleanup_cache as _make_cleanup_cache)


__all__ = ['refresh', 'cleanup_ignore']


def refresh(instance):
    '''Refresh the cache for an instance'''
    return _make_cleanup_cache(instance)


def ignore(cls):
    '''Mark a model to ignore for cleanup'''
    setattr(cls, _get_mangled_ignore(cls), None)
    return cls
cleanup_ignore = ignore
