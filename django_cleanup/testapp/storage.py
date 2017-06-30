from __future__ import unicode_literals

import os

from django.core.files.storage import FileSystemStorage


class DeleteErrorStorage(FileSystemStorage):
    def delete(self, name):
        ''' delete modified to reraise FileNotFoundError '''
        name = self.path(name)
        # If the file or directory exists, delete it from the filesystem.
        if os.path.isdir(name):
            os.rmdir(name)
        else:
            os.remove(name)
