import pytest

from django.db import models

from mock import Mock, patch

from django_cleanup import models as cleanup_models

from .models import TestModel1, TestModel2


def test_models_with_filefield():
    models.get_models = Mock(return_value=[TestModel1, TestModel2])
    assert cleanup_models.find_models_with_filefield() == [TestModel1]


@pytest.mark.django_db
def test_remove_old_files_same_file():
    test_obj = TestModel1()
    test_obj.test_file = "test_filename"
    test_obj.save()

    with patch('django_cleanup.models.remove_file') as mock:
        cleanup_models.remove_old_files(TestModel1, test_obj)

        assert not mock.called


@pytest.mark.django_db
def test_remove_old_files_different_file():
    test_obj = TestModel1()
    test_obj.test_file = "test_filename1"
    test_obj.save()

    test_obj.test_file = Mock()
    test_obj.test_file.name = "test_filename2"

    with patch('django_cleanup.models.remove_file') as mock:
        cleanup_models.remove_old_files(TestModel1, test_obj)

        assert mock.called
        assert mock.call_args[0][0].name == "test_filename1"


def test_remove_files():
    test_obj = TestModel1()
    test_obj.test_file = Mock()
    test_obj.test_file.name = "test_filename"

    with patch('django_cleanup.models.remove_file') as mock:
        cleanup_models.remove_files(TestModel1, test_obj)

        mock.assert_called_with(test_obj.test_file)
