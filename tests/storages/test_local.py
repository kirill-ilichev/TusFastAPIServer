import pytest
import os
import tempfile
from unittest import mock
from freezegun import freeze_time

from tusfastapiserver.config import Config, StorageStrategyType
from tusfastapiserver.schemas import UploadMetadata
from tusfastapiserver.storages.local import LocalStorageStrategy


@pytest.fixture(scope="class")
def config():
    return Config(storage_strategy_type=StorageStrategyType.LOCAL, file_path="TEST_TEST")


@pytest.fixture(scope="class")
def local_storage_strategy(config):
    return LocalStorageStrategy(config)


@freeze_time("2025-01-01 00:00:00")
class TestLocalStorageStrategy:
    def test_generate_file_path(self, local_storage_strategy):
        file_id = "123"
        assert (
            local_storage_strategy.generate_file_path(file_id)
            == "TEST_TEST/123/123"
        )

    def test_is_file_exists_with_temp_file(self, local_storage_strategy):
        file_id = "123"
        with tempfile.TemporaryDirectory() as temp_dir:
            local_storage_strategy.config.file_path = temp_dir
            file_path = local_storage_strategy.generate_file_path(file_id)
            assert local_storage_strategy.is_file_exists(file_id) == False
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write("")
            assert local_storage_strategy.is_file_exists(file_id) == True

    def test_is_file_exists_without_temp_file(self, local_storage_strategy):
        file_id = "123"
        assert local_storage_strategy.is_file_exists(file_id) == False

    def test_initialize(self, local_storage_strategy):
        upload_metadata = UploadMetadata(
            id="123",
            upload_storage_path="test",
            upload_metadata_path="test",
            storage_strategy_type=StorageStrategyType.LOCAL,
            metadata_strategy_type=StorageStrategyType.LOCAL,
        )
        with mock.patch.object(
            local_storage_strategy, "_check_or_make_folder"
        ) as mock_check_or_make_folder, mock.patch.object(
            local_storage_strategy, "_create_empty_file"
        ) as mock_create_empty_file:
            local_storage_strategy.initialize(upload_metadata)
            mock_check_or_make_folder.assert_called_once_with(
                upload_metadata.upload_storage_path
            )
            mock_create_empty_file.assert_called_once_with(upload_metadata.upload_storage_path)

    def test_update(self, local_storage_strategy):
        upload_metadata = UploadMetadata(
            id="123",
            upload_storage_path="test",
            upload_metadata_path="test",
            storage_strategy_type=StorageStrategyType.LOCAL,
            metadata_strategy_type=StorageStrategyType.LOCAL,
        )
        chunk = b"test data"
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            local_storage_strategy.update(upload_metadata, chunk)
            mock_file.assert_called_once_with(upload_metadata.upload_storage_path, 'ab')
            mock_file().write.assert_called_once_with(chunk)
