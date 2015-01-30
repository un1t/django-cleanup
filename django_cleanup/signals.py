from django.dispatch import Signal

cleanup_pre_delete = Signal(providing_args=["file"])
cleanup_post_delete = Signal(providing_args=["file"])
