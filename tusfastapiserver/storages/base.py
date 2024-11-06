from tusfastapiserver.config import Config
from tusfastapiserver.config import StorageStrategyType


class BaseStorageStrategy:
    storage_strategy_type: StorageStrategyType

    def __init__(self, config: Config, *args, **kwargs):
        self.config = config

    def initialize(self, *args, **kwargs):
        raise NotImplementedError()

    def is_file_exists(self, file_id: str) -> bool:
        raise NotImplementedError()
