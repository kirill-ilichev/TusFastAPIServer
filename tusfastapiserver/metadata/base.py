from tusfastapiserver.config import Config
from tusfastapiserver.config import MetadataStrategyType


class BaseMetadataStrategy:
    metadata_strategy_type: MetadataStrategyType

    def __init__(self, config: Config, *args, **kwargs):
        self.config = config

    def initialize(self, *args, **kwargs):
        raise NotImplementedError()

    def is_metadata_exists(self, file_id: str) -> bool:
        raise NotImplementedError()
