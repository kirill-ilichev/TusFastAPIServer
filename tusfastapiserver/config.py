import os

from dataclasses import dataclass, field
from typing import List
from enum import Enum


class StorageStrategyType(str, Enum):
    LOCAL = "LOCAL"


class MetadataStrategyType(str, Enum):
    LOCAL = "LOCAL"


class TusExtension(Enum):
    CREATION = "Creation"
    CREATION_WITH_UPLOAD = "Creation With Upload"
    EXPIRATION = "Expiration"
    CHECKSUM = "Checksum"
    TERMINATION = "Termination"
    CONCATENATION = "Concatenation"


@dataclass
class Config:
    storage_strategy_type: StorageStrategyType = field(
        default=StorageStrategyType.LOCAL
    )
    metadata_strategy_type: MetadataStrategyType = field(
        default=MetadataStrategyType.LOCAL
    )

    enabled_extensions: List[TusExtension] = field(
        default_factory=lambda: [TusExtension.CREATION]
    )
    file_path: str = field(default=os.path.join("tmp", "tusfastapiserver"))
    metadata_path: str = field(default=os.path.join("tmp", "tusfastapiserver"))
    path_prefix: str = field(default="/files")

    post_router_path: str = field(init=False)
    patch_router_path: str = field(init=False)
    head_router_path: str = field(init=False)
    options_router_path: str = field(init=False)
    delete_router_path: str = field(init=False)

    def __post_init__(self):
        self.post_router_path = f"{self.path_prefix}"
        self.patch_router_path = f"{self.path_prefix}/{{file_id}}"
        self.head_router_path = f"{self.path_prefix}/{{file_id}}"
        self.options_router_path = f"{self.path_prefix}"
        self.delete_router_path = f"{self.path_prefix}/{{file_id}}"
