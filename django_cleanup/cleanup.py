'''Public utilities'''
from __future__ import unicode_literals

from .cache import make_cleanup_cache as _make_cleanup_cache


__all__ = ['refresh']


def refresh(instance):
    '''Refresh the cache for an instance'''
    return _make_cleanup_cache(instance)
