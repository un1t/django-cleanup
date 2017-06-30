# coding: utf-8
'''
    django-cleanup sends the following signals
'''
from __future__ import unicode_literals

from django.dispatch import Signal


__all__ = ['cleanup_pre_delete', 'cleanup_post_delete']

cleanup_pre_delete = Signal(providing_args=["file"])
cleanup_post_delete = Signal(providing_args=["file"])
