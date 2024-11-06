import os
import json
from pathlib import Path

from tusfastapiserver.schemas import UploadMetadata
from tusfastapiserver.metadata import BaseMetadataStrategy
from tusfastapiserver.config import MetadataStrategyType


class LocalMetadataStrategy(BaseMetadataStrategy):
    metadata_strategy_type = MetadataStrategyType.LOCAL

    def generate_metadata_path(self, file_id: str) -> str:
        file_name = f"{file_id}.json"
        return os.path.join(self.config.metadata_path, os.path.join(file_id, file_name))

    def is_metadata_exists(self, file_id: str) -> bool:
        return os.path.exists(self.generate_metadata_path(file_id))

    def get_metadata(self, file_id: str) -> UploadMetadata:
        with open(self.generate_metadata_path(file_id), "r", encoding="utf-8") as f:
            return UploadMetadata(**json.load(f))

    @staticmethod
    def _check_or_make_folder(path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _create_metadata_file(upload_metadata: UploadMetadata) -> None:
        with open(upload_metadata.upload_metadata_path, "w", encoding="utf-8") as f:
            json.dump(
                upload_metadata.model_dump(),
                f,
                default=str,
                ensure_ascii=False,
                indent=4,
            )

    def initialize(self, upload_metadata: UploadMetadata) -> None:
        self._check_or_make_folder(upload_metadata.upload_metadata_path)
        self._create_metadata_file(upload_metadata)

    def _update_metadata_file(self, upload_metadata: UploadMetadata) -> None:
        with open(upload_metadata.upload_metadata_path, "r+", encoding="utf-8") as f:
            existing_data = json.load(f)
            existing_data.update(upload_metadata.model_dump())
            f.seek(0)
            json.dump(existing_data, f, default=str, ensure_ascii=False, indent=4)
            f.truncate()

    def update(self, upload_metadata: UploadMetadata, *args, **kwargs):
        self._update_metadata_file(upload_metadata)
