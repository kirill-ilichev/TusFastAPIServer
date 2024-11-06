from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict

from tusfastapiserver.config import MetadataStrategyType
from tusfastapiserver.config import StorageStrategyType


class BaseUploadMetadata(BaseModel):
    tus_resumable: str = "1.0.0"
    upload_offset: int = 0
    upload_length: Optional[int] = None
    upload_defer_length: Optional[bool] = None
    metadata: Optional[Dict[str, Optional[str]]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    upload_storage_path: str
    storage_strategy_type: StorageStrategyType
    upload_metadata_path: str
    metadata_strategy_type: MetadataStrategyType


class UploadMetadata(BaseUploadMetadata):
    id: str
