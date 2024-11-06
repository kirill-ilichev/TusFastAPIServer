import os
from pathlib import Path

from tusfastapiserver.storages import BaseStorageStrategy
from tusfastapiserver.config import StorageStrategyType
from tusfastapiserver.schemas import UploadMetadata


class LocalStorageStrategy(BaseStorageStrategy):
    storage_strategy_type = StorageStrategyType.LOCAL

    # TODO: ensure uniqueness of the path
    def generate_file_path(self, file_id: str) -> str:
        file_name = f"{file_id}"
        return os.path.join(self.config.file_path, os.path.join(file_id, file_name))

    def is_file_exists(self, file_id: str) -> bool:
        return os.path.exists(self.generate_file_path(file_id))

    @staticmethod
    def _check_or_make_folder(path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _create_empty_file(path: str) -> None:
        with open(path, "w"):
            pass

    def initialize(self, upload_metadata: UploadMetadata, *args, **kwargs):
        self._check_or_make_folder(upload_metadata.upload_storage_path)
        self._create_empty_file(upload_metadata.upload_storage_path)
    
    @staticmethod
    def update(upload_metadata: UploadMetadata, chunk: bytes):
        with open(upload_metadata.upload_storage_path, 'ab') as file:
            file.write(chunk)
