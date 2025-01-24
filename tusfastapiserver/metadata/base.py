from tusfastapiserver.config import Config
from tusfastapiserver.config import MetadataStrategyType
from tusfastapiserver.schemas import UploadMetadata


class BaseMetadataStrategy:
    metadata_strategy_type: MetadataStrategyType

    def __init__(self, config: Config, *args, **kwargs):
        self.config = config

    def initialize(self, *args, **kwargs):
        raise NotImplementedError()

    def is_metadata_exists(self, file_id: str) -> bool:
        raise NotImplementedError()

    def get_metadata(self, file_id: str) -> UploadMetadata:
        raise NotImplementedError()

    def update(self, upload_metadata: UploadMetadata, *args, **kwargs):
        raise NotImplementedError()
