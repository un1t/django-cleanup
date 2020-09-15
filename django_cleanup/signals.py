'''
    django-cleanup sends the following signals
'''
from django.dispatch import Signal


__all__ = ['cleanup_pre_delete', 'cleanup_post_delete']


cleanup_pre_delete = Signal()
'''Called just before a file is deleted. Passes a `file` keyword argument.'''


cleanup_post_delete = Signal()
'''Called just after a file is deleted. Passes a `file` keyword argument.'''
