import pytest
import os
import tempfile
import json
from freezegun import freeze_time

from tusfastapiserver.config import Config
from tusfastapiserver.config import MetadataStrategyType
from tusfastapiserver.config import StorageStrategyType
from tusfastapiserver.metadata import LocalMetadataStrategy


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
