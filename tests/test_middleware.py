import pytest

from mock import Mock

from django_cleanup import models as cleanup_models
from django_cleanup.middleware import CleanupMiddleware

from .models import TestModel1


@pytest.mark.django_db
def test_remove_old_files_same_file_with_middleware(settings):
    settings.DJANGO_CLEANUP_DELETE_ON_MIDDLEWARE = True
    cleanup_models.files_to_delete = []

    test_obj = TestModel1()
    test_obj.test_file = "test_filename"
    test_obj.save()

    cleanup_models.remove_old_files(TestModel1, test_obj)

    assert len(cleanup_models.files_to_delete) == 0


@pytest.mark.django_db
def test_remove_old_files_different_file_with_middleware(settings):
    settings.DJANGO_CLEANUP_DELETE_ON_MIDDLEWARE = True
    cleanup_models.files_to_delete = []

    test_obj = TestModel1()
    test_obj.test_file = "test_filename1"
    test_obj.save()

    test_obj.test_file = Mock()
    test_obj.test_file.name = "test_filename2"

    cleanup_models.remove_old_files(TestModel1, test_obj)

    assert len(cleanup_models.files_to_delete) == 1
    assert cleanup_models.files_to_delete[0].name == "test_filename1"


def test_remove_files_with_middleware(settings):
    settings.DJANGO_CLEANUP_DELETE_ON_MIDDLEWARE = True
    cleanup_models.files_to_delete = []

    test_obj = TestModel1()
    test_obj.test_file = Mock()
    test_obj.test_file.name = "test_filename"

    cleanup_models.remove_files(TestModel1, test_obj)

    assert len(cleanup_models.files_to_delete) == 1
    assert cleanup_models.files_to_delete[0] == test_obj.test_file


def test_middleware_without_exception(settings):
    mock = Mock()
    mock.name = "test_filename"
    mock.storage = Mock()
    mock.storage.exists = Mock(return_value=True)
    mock.storage.delete = Mock()
    cleanup_models.files_to_delete = [mock]

    CleanupMiddleware().process_response(None, None)

    assert mock.storage.delete.called


def test_middleware_with_exception(settings):
    mock = Mock()
    mock.name = "test_filename"
    mock.storage = Mock()
    mock.storage.exists = Mock(return_value=True)
    mock.storage.delete = Mock()
    cleanup_models.files_to_delete = [Mock()]

    CleanupMiddleware().process_exception(None, None)
    CleanupMiddleware().process_response(None, None)

    assert not mock.storage.delete.called
