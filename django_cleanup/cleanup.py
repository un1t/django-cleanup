'''Public utilities'''
from __future__ import unicode_literals

from .cache import make_cleanup_cache as _make_cleanup_cache
from .cache import get_mangled_ignore as _get_mangled_ignore


__all__ = ['refresh', 'cleanup_ignore']


def refresh(instance):
    '''Refresh the cache for an instance'''
    return _make_cleanup_cache(instance)


def ignore(cls):
    setattr(cls, _get_mangled_ignore(cls), None)
    return cls
cleanup_ignore = ignore
