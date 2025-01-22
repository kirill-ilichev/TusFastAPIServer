import pytest
import os
import tempfile
import json
from unittest import mock
from freezegun import freeze_time

from tusfastapiserver.config import Config
from tusfastapiserver.config import MetadataStrategyType
from tusfastapiserver.config import StorageStrategyType
from tusfastapiserver.metadata import LocalMetadataStrategy
from tusfastapiserver.schemas import UploadMetadata


@pytest.fixture(scope="class")
def config():
    return Config(
        metadata_strategy_type=MetadataStrategyType.LOCAL, metadata_path="TEST_TEST"
    )


@pytest.fixture(scope="class")
def local_metadata_strategy(config):
    return LocalMetadataStrategy(config)


@freeze_time("2025-01-01 00:00:00")
class TestLocalMetadataStrategy:
    def test_generate_metadata_path(self, local_metadata_strategy):
        file_id = "123"
        assert (
            local_metadata_strategy.generate_metadata_path(file_id)
            == "TEST_TEST/123/123.json"
        )

    def test_is_metadata_exists_with_temp_file(self, local_metadata_strategy):
        file_id = "123"
        with tempfile.TemporaryDirectory() as temp_dir:
            local_metadata_strategy.config.metadata_path = temp_dir
            metadata_path = local_metadata_strategy.generate_metadata_path(file_id)
            assert local_metadata_strategy.is_metadata_exists(file_id) == False
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
            with open(metadata_path, "w") as f:
                f.write("{}")
            assert local_metadata_strategy.is_metadata_exists(file_id) == True

    def test_is_metadata_exists_without_temp_file(self, local_metadata_strategy):
        file_id = "123"
        assert local_metadata_strategy.is_metadata_exists(file_id) == False

    def test_get_metadata_with_temp_file(self, local_metadata_strategy):
        file_id = "123"
        with tempfile.TemporaryDirectory() as temp_dir:
            local_metadata_strategy.config.metadata_path = temp_dir
            metadata_path = local_metadata_strategy.generate_metadata_path(file_id)
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
            with open(metadata_path, "w") as f:
                f.write(
                    json.dumps(
                        {
                            "upload_storage_path": "test",
                            "upload_metadata_path": "test",
                            "storage_strategy_type": StorageStrategyType.LOCAL,
                            "metadata_strategy_type": MetadataStrategyType.LOCAL,
                            "id": file_id,
                            "size": 0,
                            "metadata": {},
                            "offset": 0,
                            "upload_length": 0,
                            "created_at": "2025-01-01T00:00:00+00:00",
                        }
                    )
                )

            metadata = local_metadata_strategy.get_metadata(file_id)
            assert metadata.id == "123"
            assert metadata.tus_resumable == "1.0.0"
            assert metadata.upload_offset == 0
            assert metadata.upload_length == 0
            assert metadata.upload_defer_length is None
            assert metadata.metadata == {}
            assert metadata.created_at.isoformat() == "2025-01-01T00:00:00+00:00"
            assert metadata.upload_storage_path == "test"
            assert metadata.storage_strategy_type == "LOCAL"
            assert metadata.upload_metadata_path == "test"
            assert metadata.metadata_strategy_type == "LOCAL"

    def test_check_or_make_folder(self, local_metadata_strategy):
        with tempfile.TemporaryDirectory() as temp_dir:
            local_metadata_strategy.config.metadata_path = temp_dir
            local_metadata_strategy._check_or_make_folder(temp_dir)
            assert os.path.exists(temp_dir)

    def test_create_metadata_file(self, local_metadata_strategy):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_id = "123"
            local_metadata_strategy.config.metadata_path = temp_dir
            metadata_path = local_metadata_strategy.generate_metadata_path(file_id)
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
            metadata = UploadMetadata(
                id=file_id,
                upload_storage_path="test",
                upload_metadata_path=metadata_path,
                storage_strategy_type=StorageStrategyType.LOCAL,
                metadata_strategy_type=MetadataStrategyType.LOCAL,
            )
            local_metadata_strategy._create_metadata_file(metadata)
            assert os.path.exists(metadata_path)
            with open(metadata_path, "r") as f:
                metadata_from_file = UploadMetadata(**json.load(f))
                assert metadata_from_file.id == file_id
                assert metadata_from_file.upload_storage_path == "test"
                assert metadata_from_file.upload_metadata_path == metadata_path
                assert metadata_from_file.upload_offset == 0
                assert metadata_from_file.upload_length == None
                assert metadata_from_file.upload_defer_length == None
                assert metadata_from_file.metadata == None

    def test_initialize(self, local_metadata_strategy):
        upload_metadata = UploadMetadata(
            id="123",
            upload_storage_path="test",
            upload_metadata_path="test",
            storage_strategy_type=StorageStrategyType.LOCAL,
            metadata_strategy_type=MetadataStrategyType.LOCAL,
        )
        with mock.patch.object(
            local_metadata_strategy, "_check_or_make_folder"
        ) as mock_check_or_make_folder, mock.patch.object(
            local_metadata_strategy, "_create_metadata_file"
        ) as mock_create_metadata_file:
            local_metadata_strategy.initialize(upload_metadata)
            mock_check_or_make_folder.assert_called_once_with(
                upload_metadata.upload_metadata_path
            )
            mock_create_metadata_file.assert_called_once_with(upload_metadata)

    def test_update_metadata_file(self, local_metadata_strategy):
        file_id = "123"
        with tempfile.TemporaryDirectory() as temp_dir:
            local_metadata_strategy.config.metadata_path = temp_dir
            metadata_path = local_metadata_strategy.generate_metadata_path(file_id)
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
            initial_metadata = UploadMetadata(
                id=file_id,
                upload_storage_path="test",
                upload_metadata_path=metadata_path,
                storage_strategy_type=StorageStrategyType.LOCAL,
                metadata_strategy_type=MetadataStrategyType.LOCAL,
            )
            local_metadata_strategy._create_metadata_file(initial_metadata)
            updated_metadata = UploadMetadata(
                id=file_id,
                upload_storage_path="test_updated",
                upload_metadata_path=metadata_path,
                storage_strategy_type=StorageStrategyType.LOCAL,
                metadata_strategy_type=MetadataStrategyType.LOCAL,
                upload_offset=100,
                upload_length=200,
                metadata={"key": "value"},
            )
            local_metadata_strategy._update_metadata_file(updated_metadata)
            with open(metadata_path, "r") as f:
                metadata_from_file = UploadMetadata(**json.load(f))
                assert metadata_from_file.id == file_id
                assert metadata_from_file.upload_storage_path == "test_updated"
                assert metadata_from_file.upload_metadata_path == metadata_path
                assert metadata_from_file.upload_offset == 100
                assert metadata_from_file.upload_length == 200
                assert metadata_from_file.upload_defer_length == None
                assert metadata_from_file.metadata == {"key": "value"}

    def test_update(self, local_metadata_strategy):
        upload_metadata = UploadMetadata(
            id="123",
            upload_storage_path="test",
            upload_metadata_path="test",
            storage_strategy_type=StorageStrategyType.LOCAL,
            metadata_strategy_type=MetadataStrategyType.LOCAL,
        )
        with mock.patch.object(
            local_metadata_strategy, "_update_metadata_file"
        ) as mock_update_metadata_file:
            local_metadata_strategy.update(upload_metadata)
            mock_update_metadata_file.assert_called_once_with(upload_metadata)
