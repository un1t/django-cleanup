import logging

from . import models

logger = logging.getLogger(__name__)


class CleanupMiddleware(object):
    def process_exception(self, request, response):
        models.files_to_delete = []
        return response


    def process_response(self, request, response):
        for file_obj in models.files_to_delete:
            storage = file_obj.storage
            if storage and storage.exists(file_obj.name):
                try:
                    storage.delete(file_obj.name)
                except Exception:
                    logger.exception("Unexpected exception while attempting to delete old file '%s'" % file_obj.name)

        models.files_to_delete = []
        return response
