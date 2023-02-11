import os

from django.core.files.storage import FileSystemStorage


class DeleteErrorStorage(FileSystemStorage):
    def delete(self, name):
        ''' delete modified to not catch FileNotFoundError
            does not support deleting directories
        '''
        name = self.path(name)
        # If the file or directory exists, delete it from the filesystem.
        os.remove(name)
