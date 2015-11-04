'''Public utilities'''
from .cache import make_cleanup_cache as _make_cleanup_cache


def refresh(instance):
    '''Refresh the cache for an instance'''
    return _make_cleanup_cache(instance)
